#!/usr/bin/env python3
"""
anr_parser.py -- Parse Android ANR (Application Not Responding) traces
Extracts: which app, which thread, stack traces, binder calls
Usage: python3 anr_parser.py bugreport.zip [--filter app.name]
"""
import sys, re, zipfile, argparse, json
from pathlib import Path

def extract_anr(zip_path):
    """Extract ANR traces from bugreport"""
    with zipfile.ZipFile(zip_path, 'r') as z:
        names = z.namelist()
        for name in names:
            if 'trace' in name.lower() or 'anr' in name.lower():
                with z.open(name) as f:
                    return f.read().decode('utf-8', errors='ignore')
    return None

def parse_anr(content, filter_app=None):
    anrs = []
    current = None
    
    for line in content.splitlines():
        # Start of ANR block
        if 'ANR in' in line or 'Application Not Responding' in line:
            if current:
                anrs.append(current)
            m = re.search(r'ANR in (.+?)\s*\(', line)
            current = {
                'app': m.group(1) if m else 'unknown',
                'reason': line,
                'threads': [],
                'stack': []
            }
            if filter_app and filter_app.lower() not in current['app'].lower():
                current = None
        
        # Thread info
        elif current and '"' in line and 'tid=' in line:
            m = re.search(r'"(.+?)".+?tid=(\d+)', line)
            if m:
                current['threads'].append({'name': m.group(1), 'tid': m.group(2)})
        
        # Stack trace lines
        elif current and line.startswith('  at '):
            current['stack'].append(line.strip())
    
    if current:
        anrs.append(current)
    
    return anrs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('bugreport')
    parser.add_argument('--filter', help='Filter by app name')
    parser.add_argument('--json', help='Export to JSON')
    args = parser.parse_args()

    print(f"📋 ANR Analyzer — {args.bugreport}")
    content = extract_anr(args.bugreport)
    if not content:
        print("No ANR traces found.")
        return

    anrs = parse_anr(content, args.filter)
    
    print(f"\nFound {len(anrs)} ANR(s)\n")
    for i, anr in enumerate(anrs, 1):
        print(f"  {i}. {anr['app']}")
        print(f"     Threads: {len(anr['threads'])}")
        print(f"     Stack frames: {len(anr['stack'])}")
        if anr['stack'][:3]:
            print("     Top frames:")
            for frame in anr['stack'][:3]:
                print(f"       {frame[:70]}")
    
    if args.json:
        with open(args.json, 'w') as f:
            json.dump(anrs, f, indent=2)
        print(f"\n✅ Exported to {args.json}")

if __name__ == "__main__":
    main()
