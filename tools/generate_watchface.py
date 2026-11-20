"""Generates app/src/main/res/raw/watchface.xml for JugglucoTBR.

Idioms are taken from android/wear-os-samples WatchFaceFormat:
  * SimpleDigital   - TimeText switched with <Variant mode="AMBIENT">
  * Complications   - ComplicationSlot + Condition/Expressions null checks,
                      ColorConfiguration palette addressed as [CONFIGURATION.<id>.<index>]
  * Weather         - BitmapFonts indexed by [WEATHER.CONDITION]

Layout v4 (450x450 canvas), everything on one central axis.
Hierarchy: 1 time > 2 glucose > 3 trend arrow > 4 reading age > 5 complications.

           SAT 15 NOV                date (native, uppercase, lowered so the system status icon never covers it)
         17:51 :32                   time hh:mm (same size, bold) + seconds (smaller); seconds hidden in AOD
         126 [arrow]  [delta]        Juggluco glucose + trend arrow (slot 13, accent, also in AOD) | optional delta (14)
          0 min ago                  reading age (slot 15)
     [sun] 19       [icon] 18:12     native weather | slot 11 (editable, default: next event, with caption)
     [icon] 3168    [bat] 97%        slot 12 (editable, default: step count, with caption) | native battery

Complications are secondary: icon + value + small caption (the provider's title, when it has one), no containers.
Always-on display keeps only hh:mm (centred, regular weight) and the glucose slot.

Slot ids are 11..15 on purpose: ids 1..7 were used by earlier layouts, and Wear OS keeps the provider a user
picked per slot id, so re-using them made old choices (bell, battery...) show up in the wrong place.

Run:  python tools/generate_watchface.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "app" / "src" / "main" / "res" / "raw" / "watchface.xml"

ACCENT = "[CONFIGURATION.theme.0]"
PRIMARY = "[CONFIGURATION.theme.1]"
GREY = "#ffc0c0c0"          # reading age, delta
DATE_COL = "#ffe0e0e0"      # date
CELL_TEXT = "#ffd8d8d8"     # complication values (secondary)
CELL_TITLE = "#ff909090"    # complication caption (provider title)
CELL_ICON = "#ffb8b8b8"     # complication icons
BAT_GREEN, BAT_YELLOW, BAT_RED = "#ff5fbf7a", "#ffe3b341", "#ffe5534b"
AMB_HIDE = '<Variant mode="AMBIENT" target="alpha" value="0"/>'

JUGGLUCO = "tk.glucodata"
GLUCOSE_PROVIDER = f"{JUGGLUCO}/{JUGGLUCO}.glucosecomplication.NumberDataSourceService"
ARROW_PROVIDER = f"{JUGGLUCO}/{JUGGLUCO}.glucosecomplication.ArrowDataSourceService"
AGE_PROVIDER = f"{JUGGLUCO}/{JUGGLUCO}.glucosecomplication.TimeStampComplicationService"

TEXT = "[COMPLICATION.TEXT]"
TITLE = "[COMPLICATION.TITLE]"
MONO = "[COMPLICATION.MONOCHROMATIC_IMAGE]"
SMALL = "[COMPLICATION.SMALL_IMAGE]"

CX = 225  # central axis

# slot ids (see module docstring: never reuse 1..7)
SLOT_CELL1, SLOT_CELL2, SLOT_GLUCOSE, SLOT_DELTA, SLOT_AGE = 11, 12, 13, 14, 15


# ------------------------------------------------------------------ helpers
def ind(s, n):
    pad = " " * n
    return "\n".join(pad + l if l.strip() else l for l in s.split("\n"))


def part_text(x, y, w, h, size, color, expr, family="inter_regular", align="CENTER",
              max_lines=None, fmt="%s"):
    ml = f' maxLines="{max_lines}"' if max_lines else ""
    return (
        f'<PartText x="{x}" y="{y}" width="{w}" height="{h}">\n'
        f'  <Text align="{align}" ellipsis="TRUE"{ml}>\n'
        f'    <Font family="{family}" size="{size}" color="{color}">\n'
        f'      <Template><![CDATA[{fmt}]]>\n'
        f'        <Parameter expression="{expr}"/>\n'
        f'      </Template>\n'
        f'    </Font>\n'
        f'  </Text>\n'
        f'</PartText>'
    )


def part_image(x, y, w, h, res, tint=None):
    t = f' tintColor="{tint}"' if tint else ""
    return f'<PartImage x="{x}" y="{y}" width="{w}" height="{h}"{t}>\n  <Image resource="{res}"/>\n</PartImage>'


def expr(name, body):
    return f'<Expression name="{name}"><![CDATA[{body}]]></Expression>'


# ------------------------------------------------------------------ secondary cells (icon + value + caption)
CELL_W, CELL_H, CELL_GAP = 130, 46, 20
LEFT_X, RIGHT_X = CX - CELL_GAP // 2 - CELL_W, CX + CELL_GAP // 2
ROW1_Y, ROW2_Y = 284, 338
ICON_X, ICON_S = 10, 26
TXT_X = 44
CELL_FONT, TITLE_FONT = 22, 13


def single_y(h=CELL_H):
    return (h - 30) // 2


def text_block(x, w, h, align):
    """Value with the provider's title as a small caption underneath when the provider supplies one."""
    return f"""<Condition>
  <Expressions>
    {expr("c_title", f"{TITLE} != null")}
  </Expressions>
  <Compare expression="c_title">
{ind(part_text(x, 2, w, 28, CELL_FONT, CELL_TEXT, TEXT, align=align), 4)}
{ind(part_text(x, 28, w, 16, TITLE_FONT, CELL_TITLE, TITLE, align=align, max_lines=1), 4)}
  </Compare>
  <Default>
{ind(part_text(x, single_y(h), w, 30, CELL_FONT, CELL_TEXT, TEXT, align=align), 4)}
  </Default>
</Condition>"""


def cell_short(w, h):
    iy = (h - ICON_S) // 2
    return f"""<Complication type="SHORT_TEXT">
  <Condition>
    <Expressions>
      {expr("c_img", f"{MONO} != null")}
    </Expressions>
    <Compare expression="c_img">
{ind(part_image(ICON_X, iy, ICON_S, ICON_S, MONO, CELL_ICON), 6)}
{ind(text_block(TXT_X, w - TXT_X - 2, h, "START"), 6)}
    </Compare>
    <Default>
{ind(text_block(4, w - 8, h, "CENTER"), 6)}
    </Default>
  </Condition>
</Complication>"""


def cell_long(w, h):
    return f"""<Complication type="LONG_TEXT">
{ind(text_block(6, w - 12, h, "CENTER"), 2)}
</Complication>"""


def cell_ranged(w, h):
    return f"""<Complication type="RANGED_VALUE">
{ind(text_block(4, w - 8, h, "CENTER"), 2)}
</Complication>"""


def cell_goal(w, h):
    return f"""<Complication type="GOAL_PROGRESS">
{ind(text_block(4, w - 8, h, "CENTER"), 2)}
</Complication>"""


def cell_small(w, h):
    s = h - 6
    return f"""<Complication type="SMALL_IMAGE">
{ind(part_image((w - s) // 2, 3, s, s, SMALL), 2)}
</Complication>"""


CELLS = {
    "SHORT_TEXT": cell_short,
    "LONG_TEXT": cell_long,
    "RANGED_VALUE": cell_ranged,
    "GOAL_PROGRESS": cell_goal,
    "SMALL_IMAGE": cell_small,
}
ALL5 = ["SHORT_TEXT", "LONG_TEXT", "RANGED_VALUE", "GOAL_PROGRESS", "SMALL_IMAGE"]


def cell_slot(slot_id, label, x, y, w, h, provider, provider_type, types, primary=None, primary_type=None):
    body = "\n".join(ind(CELLS[t](w, h), 2) for t in types)
    prim = f' primaryProvider="{primary}" primaryProviderType="{primary_type}"' if primary else ""
    return f"""<ComplicationSlot x="{x}" y="{y}" width="{w}" height="{h}" slotId="{slot_id}" displayName="{label}" isCustomizable="TRUE" supportedTypes="{' '.join(types)} EMPTY">
  {AMB_HIDE}
  <DefaultProviderPolicy defaultSystemProvider="{provider}" defaultSystemProviderType="{provider_type}"{prim}/>
  <BoundingRoundBox x="0" y="0" width="{w}" height="{h}" cornerRadius="8" outlinePadding="2.0"/>
{body}
</ComplicationSlot>"""


# ------------------------------------------------------------------ vertical metrics (Inter)
# Text is centred in its box; Inter's baseline sits ~0.364 em below the box centre and digits are ~0.73 em tall.
BASE_K = 0.364

# ------------------------------------------------------------------ native: time (hh:mm + smaller :ss)
HM_SIZE, SS_SIZE = 96, 36
HM_Y, HM_H = 60, 116
HM_W = 292                                       # widest bold "00:00" at 96 px (~289)
SS_GAP, SS_W = 4, 70                             # ":ss" at 36 px is ~61 px wide
GROUP_W = HM_W + SS_GAP + 62
HM_END = CX - GROUP_W // 2 + HM_W                # right edge of the hh:mm block
SS_X = HM_END + SS_GAP
BASELINE = HM_Y + HM_H / 2 + BASE_K * HM_SIZE
SS_H = 44
SS_Y = round(BASELINE - BASE_K * SS_SIZE - SS_H / 2)


def time_text(fmt, x, y, w, h, size, color, family, weight, mode, align="CENTER"):
    """mode: 'interactive' (hidden in AOD), 'ambient' (AOD only)."""
    if mode == "interactive":
        alpha, var = 255, '\n        <Variant mode="AMBIENT" target="alpha" value="0"/>'
    else:
        alpha, var = 0, '\n        <Variant mode="AMBIENT" target="alpha" value="255"/>'
    return (
        f'<TimeText format="{fmt}" hourFormat="SYNC_TO_DEVICE" align="{align}" x="{x}" y="{y}" width="{w}" height="{h}" alpha="{alpha}">{var}\n'
        f'        <Font family="{family}" size="{size}" weight="{weight}" slant="NORMAL" color="{color}"/>\n'
        f'      </TimeText>'
    )


clock = f"""<DigitalClock x="0" y="0" width="450" height="450">
      <!-- hh:mm: same size and weight, right-aligned so the seconds sit next to it in active mode -->
      {time_text("hh:mm", HM_END - HM_W, HM_Y, HM_W, HM_H, HM_SIZE, PRIMARY, "inter_bold", "BOLD", "interactive", align="END")}
      <!-- AOD: hh:mm alone, centred on the axis, regular weight -->
      {time_text("hh:mm", 25, HM_Y, 400, HM_H, HM_SIZE, PRIMARY, "inter_regular", "NORMAL", "ambient")}
    </DigitalClock>"""

seconds_text = f"""<PartText x="{SS_X}" y="{SS_Y}" width="{SS_W}" height="{SS_H}">
  {AMB_HIDE}
  <Text align="START">
    <Font family="inter_bold" size="{SS_SIZE}" color="{GREY}">
      <Template><![CDATA[:%s]]>
        <Parameter expression="[SECOND_Z]"/>
      </Template>
    </Font>
  </Text>
</PartText>"""

# ------------------------------------------------------------------ native: date (uppercase)
# The system status icon (DND / charging / ...) is drawn over y ~ 20..46 at the top centre, so the date sits below it.
DATE_Y = 42
date_text = """<PartText x="75" y="%d" width="300" height="34">
  <Text align="CENTER">
    <Font family="inter_bold" size="26" color="%s">
      <Upper>
        <Template><![CDATA[%%s %%s %%s]]>
          <Parameter expression="[DAY_OF_WEEK_S]"/>
          <Parameter expression="[DAY]"/>
          <Parameter expression="[MONTH_S]"/>
        </Template>
      </Upper>
    </Font>
  </Text>
</PartText>""" % (DATE_Y, DATE_COL)
date_text = date_text.replace("%%s", "%s")
date_text = f"""<Group name="date" x="0" y="0" width="450" height="450">
  {AMB_HIDE}
{ind(date_text, 2)}
</Group>"""

# ------------------------------------------------------------------ Juggluco glucose + trend arrow (kept in AOD)
G_SIZE = 84
GH = 104
GY = round(BASELINE + 16 + 0.365 * G_SIZE - GH / 2)   # digits start 16 px below the time baseline
G_ARROW_S = 60
G_VALUE_RIGHT = 272                                    # abs x of the value's right edge ("266" is ~161 px wide)
G_ARROW_ABS = G_VALUE_RIGHT + 8                        # value + arrow block is centred on the axis
GX, GW = 90, 260
G_TXT_W = G_VALUE_RIGHT - GX
G_ARROW_X = G_ARROW_ABS - GX
G_ARROW_Y = (GH - G_ARROW_S) // 2


def glucose_slot(slot_id):
    types = "SHORT_TEXT LONG_TEXT SMALL_IMAGE MONOCHROMATIC_IMAGE"
    return f"""<ComplicationSlot x="{GX}" y="{GY}" width="{GW}" height="{GH}" slotId="{slot_id}" displayName="glucose_complication_label" isCustomizable="TRUE" supportedTypes="{types} EMPTY">
  <DefaultProviderPolicy defaultSystemProvider="EMPTY" defaultSystemProviderType="EMPTY" primaryProvider="{GLUCOSE_PROVIDER}" primaryProviderType="SMALL_IMAGE"/>
  <BoundingBox x="0" y="0" width="{GW}" height="{GH}" outlinePadding="2.0"/>
  <Complication type="SHORT_TEXT">
    <Condition>
      <Expressions>
        {expr("g_img", f"{MONO} != null")}
        {expr("g_small", f"{SMALL} != null")}
      </Expressions>
      <Compare expression="g_img">
{ind(part_text(0, 0, G_TXT_W, GH, G_SIZE, ACCENT, TEXT, "inter_bold", align="END"), 8)}
{ind(part_image(G_ARROW_X, G_ARROW_Y, G_ARROW_S, G_ARROW_S, MONO, ACCENT), 8)}
      </Compare>
      <Compare expression="g_small">
{ind(part_text(0, 0, G_TXT_W, GH, G_SIZE, ACCENT, TEXT, "inter_bold", align="END"), 8)}
{ind(part_image(G_ARROW_X, G_ARROW_Y, G_ARROW_S, G_ARROW_S, SMALL), 8)}
      </Compare>
      <Default>
{ind(part_text(0, 0, GW, GH, G_SIZE, ACCENT, TEXT, "inter_bold"), 8)}
      </Default>
    </Condition>
  </Complication>
  <Complication type="LONG_TEXT">
{ind(part_text(0, 0, GW, GH, 40, ACCENT, TEXT, "inter_bold", max_lines=1), 4)}
  </Complication>
  <Complication type="SMALL_IMAGE">
{ind(part_image(90, 12, 80, 80, SMALL), 4)}
  </Complication>
  <Complication type="MONOCHROMATIC_IMAGE">
{ind(part_image(90, 12, 80, 80, MONO, ACCENT), 4)}
  </Complication>
</ComplicationSlot>"""


# ------------------------------------------------------------------ delta (right of the arrow) + reading age (below)
def delta_slot(slot_id):
    w, h = 70, 44
    x, y = G_ARROW_ABS + G_ARROW_S + 8, GY + (GH - h) // 2
    return f"""<ComplicationSlot x="{x}" y="{y}" width="{w}" height="{h}" slotId="{slot_id}" displayName="delta_complication_label" isCustomizable="TRUE" supportedTypes="SHORT_TEXT LONG_TEXT EMPTY">
  {AMB_HIDE}
  <DefaultProviderPolicy defaultSystemProvider="HEART_RATE" defaultSystemProviderType="SHORT_TEXT"/>
  <BoundingBox x="0" y="0" width="{w}" height="{h}" outlinePadding="2.0"/>
  <Complication type="SHORT_TEXT">
{ind(part_text(0, 0, w, h, 28, GREY, TEXT, align="START"), 4)}
  </Complication>
  <Complication type="LONG_TEXT">
{ind(part_text(0, 0, w, h, 20, GREY, TEXT, align="START", max_lines=1), 4)}
  </Complication>
</ComplicationSlot>"""


AGE_SIZE = 32


def age_slot(slot_id):
    w, h = 240, 40
    x, y = CX - w // 2, GY + GH - 12
    minutes = 'numberFormat(&quot;#&quot;, floor([COMPLICATION.RANGED_VALUE_VALUE] / 60))'
    return f"""<ComplicationSlot x="{x}" y="{y}" width="{w}" height="{h}" slotId="{slot_id}" displayName="age_complication_label" isCustomizable="TRUE" supportedTypes="RANGED_VALUE SHORT_TEXT EMPTY">
  {AMB_HIDE}
  <DefaultProviderPolicy defaultSystemProvider="EMPTY" defaultSystemProviderType="EMPTY" primaryProvider="{AGE_PROVIDER}" primaryProviderType="RANGED_VALUE"/>
  <BoundingBox x="0" y="0" width="{w}" height="{h}" outlinePadding="2.0"/>
  <Complication type="RANGED_VALUE">
    <PartText x="0" y="0" width="{w}" height="{h}">
      <Text align="CENTER" ellipsis="TRUE" maxLines="1">
        <Font family="inter_regular" size="{AGE_SIZE}" color="{GREY}">
          <Template><![CDATA[%s %s]]>
            <Parameter expression="{minutes}"/>
            <Parameter expression="min_ago"/>
          </Template>
        </Font>
      </Text>
    </PartText>
  </Complication>
  <Complication type="SHORT_TEXT">
{ind(part_text(0, 0, w, h, AGE_SIZE, GREY, TEXT), 4)}
  </Complication>
</ComplicationSlot>"""


# ------------------------------------------------------------------ native: weather (row 1, left)
def weather_icon(font):
    return f"""<PartText x="{ICON_X - 2}" y="{(CELL_H - 30) // 2}" width="30" height="30">
  <Text>
    <BitmapFont family="{font}" size="30">
      <Template><![CDATA[%s]]>
        <Parameter expression="[WEATHER.CONDITION] &lt;= 15 ? [WEATHER.CONDITION] : 0"/>
      </Template>
    </BitmapFont>
  </Text>
</PartText>"""


weather = f"""<Group name="weather" x="{LEFT_X}" y="{ROW1_Y}" width="{CELL_W}" height="{CELL_H}">
  {AMB_HIDE}
  <Condition>
    <Expressions>
      {expr("w_avail", "[WEATHER.IS_AVAILABLE]")}
    </Expressions>
    <Compare expression="w_avail">
      <Condition>
        <Expressions>
          {expr("w_day", "[WEATHER.IS_DAY]")}
        </Expressions>
        <Compare expression="w_day">
{ind(weather_icon("weather_icons_day"), 10)}
        </Compare>
        <Default>
{ind(weather_icon("weather_icons_night"), 10)}
        </Default>
      </Condition>
{ind(part_text(TXT_X, single_y(), CELL_W - TXT_X - 2, 30, CELL_FONT, CELL_TEXT, "round([WEATHER.TEMPERATURE])", align="START", fmt="%s\u00b0"), 6)}
    </Compare>
  </Condition>
</Group>"""

CONDITIONS_DAY = [
    ("Character", 0, "ic_unknown"), ("Character", 1, "ic_clear"), ("Character", 2, "ic_cloudy"),
    ("Character", 3, "ic_fog"), ("Character", 4, "ic_heavy_rain"), ("Character", 5, "ic_heavy_snow"),
    ("Character", 6, "ic_rain"), ("Character", 7, "ic_snow"), ("Character", 8, "ic_sunny"),
    ("Character", 9, "ic_thunderstorm"), ("Word", 10, "ic_sleet"), ("Word", 11, "ic_snow"),
    ("Word", 12, "ic_rain"), ("Word", 13, "ic_fog"), ("Word", 14, "ic_partly_cloudy_day"),
    ("Word", 15, "ic_windy"),
]


def bitmap_font(name, partly):
    rows = []
    for kind, idx, res in CONDITIONS_DAY:
        if idx == 14:
            res = partly
        rows.append(f'    <{kind} name="{idx}" resource="{res}" width="96" height="96"/>')
    return f'  <BitmapFont name="{name}">\n' + "\n".join(rows) + "\n  </BitmapFont>"


bitmap_fonts = (
    "  <BitmapFonts>\n"
    + bitmap_font("weather_icons_day", "ic_partly_cloudy_day") + "\n"
    + bitmap_font("weather_icons_night", "ic_partly_cloudy_night") + "\n"
    + "  </BitmapFonts>"
)


# ------------------------------------------------------------------ native: battery (row 2, right), coloured by level
def battery_state(color):
    bx, bw, bh = ICON_X, 24, 13
    by = (CELL_H - bh) / 2
    return f"""<PartDraw x="0" y="0" width="{CELL_W}" height="{CELL_H}">
  <Rectangle x="{bx}" y="{by}" width="{bw}" height="{bh}">
    <Stroke color="{color}" thickness="1.5"/>
  </Rectangle>
  <Rectangle x="{bx + bw}" y="{by + 3.5}" width="2.5" height="6">
    <Fill color="{color}"/>
  </Rectangle>
  <Rectangle x="{bx + 2.5}" y="{by + 2.5}" width="{bw - 5}" height="{bh - 5}">
    <Fill color="{color}"/>
    <Transform target="width" value="{bw - 5} * clamp([BATTERY_PERCENT], 0, 100) / 100"/>
  </Rectangle>
</PartDraw>
{part_text(TXT_X, single_y(), CELL_W - TXT_X - 2, 30, CELL_FONT, color, "[BATTERY_PERCENT]", align="START", fmt="%s%%")}"""


battery = f"""<Group name="battery" x="{RIGHT_X}" y="{ROW2_Y}" width="{CELL_W}" height="{CELL_H}">
  {AMB_HIDE}
  <Condition>
    <Expressions>
      {expr("b_hi", "[BATTERY_PERCENT] >= 50")}
      {expr("b_mid", "[BATTERY_PERCENT] >= 20")}
    </Expressions>
    <Compare expression="b_hi">
{ind(battery_state(BAT_GREEN), 6)}
    </Compare>
    <Compare expression="b_mid">
{ind(battery_state(BAT_YELLOW), 6)}
    </Compare>
    <Default>
{ind(battery_state(BAT_RED), 6)}
    </Default>
  </Condition>
</Group>"""

# ------------------------------------------------------------------ themes (accent only; text stays white / grey)
THEMES = [
    ("theme_pixel_blue", "#62A8FF"),
    ("theme_libre_orange", "#F59E0B"),
    ("theme_green", "#22C55E"),
    ("theme_red", "#EF4444"),
    ("theme_purple", "#A855F7"),
    ("theme_cyan", "#22D3EE"),
    ("theme_yellow", "#FACC15"),
    ("theme_monochrome", "#B3B3B3"),
]
theme_opts = "\n".join(
    f'      <ColorOption id="{i}" displayName="{name}" screenReaderText="{name}" colors="{acc} #FFFFFF #333333"/>'
    for i, (name, acc) in enumerate(THEMES)
)

# ------------------------------------------------------------------ assemble
# Order = z-order: slots that overlap (age over the bottom of glucose) must come after the one they overlap.
slots = "\n".join(
    ind(s, 4)
    for s in (
        cell_slot(SLOT_CELL1, "slot1_complication_label", RIGHT_X, ROW1_Y, CELL_W, CELL_H, "EMPTY", "EMPTY", ALL5,
                  primary=ARROW_PROVIDER, primary_type="SMALL_IMAGE"),
        cell_slot(SLOT_CELL2, "slot2_complication_label", LEFT_X, ROW2_Y, CELL_W, CELL_H, "STEP_COUNT", "SHORT_TEXT", ALL5),
        glucose_slot(SLOT_GLUCOSE),
        delta_slot(SLOT_DELTA),
        age_slot(SLOT_AGE),
    )
)

xml = f"""<?xml version="1.0" encoding="utf-8"?>
<!--
    JugglucoTBR - Watch Face Format v2 (Wear OS 5), layout v4.
    Based on android/wear-os-samples WatchFaceFormat (SimpleDigital, Complications, Weather).
    GENERATED by tools/generate_watchface.py - edit the generator, not this file.

    Native (no complication needed): date (uppercase), time hh:mm + seconds, weather, battery (red/yellow/green).
    Complication slots (all user-editable; ids 11..15, never reuse 1..7 from earlier layouts)
      11 row 1, right        default: Juggluco ArrowDataSourceService (small image)
      12 row 2, left         default: step count (value + provider caption)
      13 glucose             Juggluco NumberDataSourceService (small image, stays visible in AOD)
      14 delta               default: heart rate (right of the arrow)
      15 reading age         Juggluco TimeStampComplicationService (directly below glucose)
    Theme palette ([CONFIGURATION.theme.N]): 0 = accent (glucose + arrow), 1 = primary text (time).
    Always-on display: only hh:mm (no seconds) and slot 13 remain visible.
-->
<WatchFace width="450" height="450" clipShape="CIRCLE">
  <Metadata key="CLOCK_TYPE" value="DIGITAL"/>
  <Metadata key="PREVIEW_TIME" value="17:51:32"/>
  <UserConfigurations>
    <ColorConfiguration id="theme" defaultValue="0" displayName="colors_label" screenReaderText="colors_label">
{theme_opts}
    </ColorConfiguration>
  </UserConfigurations>
{bitmap_fonts}
  <Scene backgroundColor="#ff000000">
    {clock}
{ind(seconds_text, 4)}
{ind(date_text, 4)}
{ind(weather, 4)}
{ind(battery, 4)}
{slots}
  </Scene>
</WatchFace>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(xml, encoding="utf-8", newline="\n")
print(f"written {OUT} ({len(xml)} bytes)")
print(f"time baseline={BASELINE:.1f} glucose slot y={GY}..{GY + GH} age y={GY + GH - 12} rows={ROW1_Y},{ROW2_Y}")
