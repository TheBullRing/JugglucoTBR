# JugglucoTBR

Wear OS 5 watch face built with **Watch Face Format (WFF v2)**. Resource-only package (no code), AMOLED black,
calm medical-device style layout on a single central axis. Glucose comes from the existing Juggluco complication
providers; there is no Bluetooth code, no service and no companion app.

```text
     SAT 15 NOV                 <- date (native, uppercase, bold)
    17:51 :32                   <- hh:mm same size + weight; seconds smaller (hidden in AOD)
    128 ->   +8                 <- glucose + trend arrow (slot 13, accent, also in AOD) | optional delta (slot 14)
     0 min ago                  <- reading age (slot 15), directly below glucose
  [sun] 19°    [arrow]          <- native weather | slot 11 (default: Juggluco trend arrow image)
  [steps] 3168 [bat] 97%        <- slot 12 (default: steps + caption) | native battery (green / yellow / red)
```

Hierarchy: 1 time, 2 glucose, 3 trend arrow, 4 reading age, 5 complications. Complications are secondary (22 px,
light grey, icon + value + small caption, no containers) and all five slots are editable (long-press the face >
Complications). Only glucose + arrow use the theme accent. The battery is native and turns
green (>= 50 %), yellow (>= 20 %) or red. Always-on display keeps only hh:mm (regular weight, no seconds) and the
glucose slot. Eight accent themes are selectable in the watch-face editor.

Preview images in `docs/` are drawn mock-ups of the intended layout (`docs/previews`), not emulator captures.

Default providers: slot 11 `tk.glucodata/...glucosecomplication.ArrowDataSourceService`, slot 12 system step count,
slot 13 `NumberDataSourceService`, slot 14 system heart rate, slot 15 `TimeStampComplicationService`.
If your Juggluco build uses a different application id, change `JUGGLUCO` in
`tools/generate_watchface.py` and regenerate (or just pick the provider manually in the editor).

## Build

Requirements: JDK 17+, Android SDK with platform `android-37`, Gradle wrapper included.

```powershell
# local.properties (not committed):  sdk.dir=C\:\\Users\\<you>\\AppData\\Local\\Android\\Sdk
.\gradlew.bat assembleDebug assembleRelease lint
```

Outputs: `app/build/outputs/apk/{debug,release}`. Open the folder as a project in Android Studio to import it.
Install on a Wear OS 5 emulator/watch: `adb install app/build/outputs/apk/debug/app-debug.apk`, then pick
**JugglucoTBR** in the watch-face picker.

Config: `compileSdk 37`, `targetSdk 37`, `minSdk 34`, package `com.juggluco.tbr`, `versionCode 1`, `versionName 1.0`.

## Project layout

| Path | Purpose |
| --- | --- |
| `app/src/main/AndroidManifest.xml` | `hasCode="false"`, WFF version property (`2`, literal; lint forbids a resource), legacy `watchface.format` meta-data |
| `app/src/main/res/raw/watchface.xml` | The WFF definition (generated, see below) |
| `app/src/main/res/xml/watch_face_info.xml` | Preview image, editable, multiple instances |
| `app/src/main/res/font/inter_*.ttf` | Inter Regular / Bold (SIL OFL 1.1) |
| `app/src/main/res/drawable-nodpi/` | `preview.png`, `icon.png` |
| `docs/previews/` | `preview_round`, `preview_square`, `preview_ambient` |
| `docs/play-store/` | Feature graphic, 512 icon, screenshots, listing text |
| `tools/generate_watchface.py` | Generator for `watchface.xml` |
| `tools/validate_wff.py` | Validates `watchface.xml` against the vendored XSD |
| `tools/generate_assets.py` | Regenerates preview / icon / Play Store images (Pillow) |
| `tools/wff-schema/v2/` | Official WFF v2 XSD (Apache-2.0, google/watchface) |
| `docs/WFF.md` | Slot / theme / validation reference |

## Baseline and regeneration

The project is based on **android/wear-os-samples `WatchFaceFormat`**: build setup, manifest, `watch_face_info.xml`
and `SimpleDigital` (dual `TimeText` switched with `<Variant mode="AMBIENT">`) / `Complications` (slot layout,
`Condition`/`Expressions` null checks, -150..150 degree arcs, `ColorConfiguration` palettes).

`app/src/main/res/raw/watchface.xml` is generated: edit `tools/generate_watchface.py`, then run
`python tools/generate_watchface.py`.

## Release package

As in the samples, `enableKotlin = false` and `isMinifyEnabled = true` keep the package resource-only: the APK/AAB
contain only `AndroidManifest.xml`, `resources.arsc` and `res/` (no `classes.dex`), which Google Play requires for WFF.
`app-release-unsigned.apk` is unsigned; add your upload key to `signingConfig` and use `.\gradlew.bat bundleRelease`
for the AAB.