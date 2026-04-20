#!/usr/bin/env python3
"""
crash_analyzer.py -- Parse Android crash logs and identify root causes
Reads logcat, extracts stack traces, groups by crash type.
Usage: python3 crash_analyzer.py [--package com.example] [--top 5]
"""
import subprocess, re, sys

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout.strip()

def get_crashes(pkg_filter=None):
    raw = adb("logcat -d AndroidRuntime:E *:S")
    crashes = []
    current = {"error": "", "trace": []}
    
    for line in raw.splitlines():
        if "FATAL EXCEPTION" in line:
            if current["error"]:
                crashes.append(current)
            current = {"error": line, "trace": []}
        elif current["error"] and ("at " in line or "Exception" in line):
            current["trace"].append(line.strip())
    
    if current["error"]:
        crashes.append(current)
    
    return crashes[:10]

def main():
    crashes = get_crashes()
    print(f"\n🔴 Found {len(crashes)} crashes\n")
    for i, c in enumerate(crashes, 1):
        print(f"{i}. {c['error'][:60]}")
        for line in c["trace"][:3]:
            print(f"   {line[:70]}")
        print()

if __name__ == "__main__":
    main()
