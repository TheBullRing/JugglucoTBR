# WFF reference

Schema: Watch Face Format **v2** (Wear OS 5). `watchface.xml` validates with 0 errors against Google's official
`third_party/wff/specification/documents/2/watchface.xsd` (https://github.com/google/watchface, XSD 1.1).

## Native elements (no complication needed)

* Date: `DAY_OF_WEEK_S DAY MONTH_S` inside `<Upper>`, bold 26, hidden in AOD. It sits at y=42, below the system status
  icon (do-not-disturb / charging) that Wear OS draws at the top centre; at y=28 that icon covered the text.
* Time: `hh:mm` (one `TimeText`, bold 96) plus `:ss` (`PartText` on `[SECOND_Z]`, bold 36, baseline-aligned, hidden in
  AOD). In AOD only a centred regular-weight `hh:mm` is shown. `TimeText` only accepts time patterns in WFF v2, hence
  date and seconds are `PartText`.
* Weather icon + temperature (`BitmapFonts` indexed by `[WEATHER.CONDITION]`), shown when `WEATHER.IS_AVAILABLE`.
* Battery: `[BATTERY_PERCENT]` with a drawn battery icon; green >= 50, yellow >= 20, red below.

## Typography hierarchy

| Level | Element | Size | Weight | Colour |
| --- | --- | --- | --- | --- |
| 1 | Time hh:mm | 96 | Bold | white (`theme.1`) |
| 1b | Seconds | 36 | Bold | grey |
| 2 | Glucose | 84 | Bold | accent (`theme.0`) |
| 3 | Trend arrow | 60 px icon | - | accent (`theme.0`) |
| 4 | Reading age | 32 | Regular | grey `#C0C0C0` |
| 4 | Delta | 28 | Regular | grey `#C0C0C0` |
| 5 | Complications, weather, battery | 22 (caption 13) | Regular | light grey, icon + value + caption |

## Complication slots (canvas 450x450)

All five slots are `isCustomizable="TRUE"`: long-press the face, tap **Complications**, tap a slot.

| slotId | Position | Default provider | Types | Ambient |
| --- | --- | --- | --- | --- |
| 11 | row 1, right | `NEXT_EVENT` | SHORT_TEXT, LONG_TEXT, RANGED_VALUE, GOAL_PROGRESS, SMALL_IMAGE | hidden |
| 12 | row 2, left | `STEP_COUNT` | same as slot 11 | hidden |
| 13 | glucose + arrow (centre) | Juggluco `ShortArrowValueDataSourceService` | SHORT_TEXT, LONG_TEXT, SMALL_IMAGE, MONOCHROMATIC_IMAGE | visible |
| 14 | delta (right of arrow) | empty | SHORT_TEXT, LONG_TEXT | hidden |
| 15 | reading age (below glucose) | Juggluco `TimeStampComplicationService` | RANGED_VALUE, SHORT_TEXT | hidden |

Rows: row 1 = weather (native, left) | slot 11; row 2 = slot 12 | battery (native, right). SHORT_TEXT cells draw the
provider's monochromatic icon next to the value, plus the provider's title (`[COMPLICATION.TITLE]`, e.g. "Steps",
"Next event") as a small caption when the provider supplies one, so each complication can be identified.
Ambient hiding uses `<Variant mode="AMBIENT" target="alpha" value="0"/>`.

### Slot ids 11..15

Ids 1..7 were used by earlier layouts. Wear OS stores the provider a user chose per slot id, so reusing them made
old choices appear in the wrong place (a bell + "100" shown on the glucose slot, and the glucose reduced to a single
digit). New ids start clean from the defaults above. Do not renumber slots again without a reason; if you must, use
fresh ids.

### Deviations from the brief (WFF limitations)

* **Weather**: WFF's `DefaultProviderPolicy` has no system weather provider, so weather is drawn natively from
  `[WEATHER.*]` rather than from a complication slot. The official Weather sample declares no extra permission.
* **Delta**: Juggluco exposes no delta complication provider, so slot 14 is empty by default (user may assign one).
  WFF cannot compute it itself.
* **Reading age**: built from Juggluco's `TimeStampComplicationService` (RANGED_VALUE = seconds since reading),
  rendered as `N min ago`.
* **Glucose slot types**: LONG_TEXT, SMALL_IMAGE and MONOCHROMATIC_IMAGE are supported in addition so other
  providers can be selected. `GOAL_PROGRESS` is only on slots 11-12.
* **Slot ids were renumbered** (now 11..15), so saved editor selections from older versions reset to defaults.
* **Trend arrow**: it is a bitmap supplied by Juggluco (`MONOCHROMATIC_IMAGE`, or `SMALL_IMAGE` as fallback), tinted
  with the accent in the monochromatic case. If the provider returns no image, only the value is shown.
* **Battery** is native (`[BATTERY_PERCENT]`) rather than a complication, because WFF cannot colour a complication's
  text by its value.

## Themes (`ColorConfiguration id="theme"`)

Palette index `0` accent (glucose + arrow), `1` primary text (time): `[CONFIGURATION.theme.N]`.

| Theme | Accent |
| --- | --- |
| Pixel Blue (default) | `#62A8FF` |
| Libre Orange | `#F59E0B` |
| Green | `#22C55E` |
| Red | `#EF4444` |
| Purple | `#A855F7` |
| Cyan | `#22D3EE` |
| Yellow | `#FACC15` |
| Monochrome | `#B3B3B3` |

## Re-validating

The official v2 XSD (Apache-2.0, from https://github.com/google/watchface) is vendored in `tools/wff-schema/v2`.

```powershell
pip install xmlschema pillow
python tools/generate_watchface.py   # writes res/raw/watchface.xml
python tools/validate_wff.py         # expect 'errors: 0'; also runs a negative test
python tools/generate_assets.py     # preview / icon / Play Store images
```

## Not verified here

No Wear OS emulator image was available on the build machine, so the rendering (especially the Juggluco arrow
colour, which is a bitmap supplied by the provider) is verified by schema + build + lint only. Test on a
Wear OS 5 emulator or watch before release. Dynamic glucose colouring (<70 / 70-180 / >180) is a v2 item.
