#!/bin/sh

ANDROID_HOME="$HOME/Library/Android/sdk"

$ANDROID_HOME/platform-tools/adb tcpip 5555
$ANDROID_HOME/platform-tools/adb connect 10.125.236.109:5555
