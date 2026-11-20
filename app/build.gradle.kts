/*
 * Based on android/wear-os-samples WatchFaceFormat.
 * Copyright 2024 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

plugins {
    id("com.android.application")
}

android {
    // Watch Face Format packages are resource-only: no Kotlin, no classes.dex.
    enableKotlin = false
    namespace = "com.juggluco.tbr"
    compileSdk = 37

    defaultConfig {
        applicationId = "com.juggluco.tbr"
        minSdk = 34
        targetSdk = 37
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        debug {
            isMinifyEnabled = true
        }
        release {
            // TODO: add your upload-key signingConfig here for Play Store builds.
            isMinifyEnabled = true
            // Keep shrinkResources false: resources are only referenced from res/raw/watchface.xml,
            // which the shrinker cannot trace.
            isShrinkResources = false
        }
    }

    lint {
        abortOnError = true
        // Resources are referenced only from res/raw/watchface.xml and watch_face_info.xml.
        disable += listOf("UnusedResources", "DataExtractionRules", "IconLauncherShape")
    }
}
