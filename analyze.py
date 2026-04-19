#!/usr/bin/env python3
"""Android crash log analyzer"""
import re, sys, argparse

CRASH_PATTERN = re.compile(
    r'(FATAL EXCEPTION|AndroidRuntime|CRASHED|ANR in)',
    re.IGNORECASE
)
STACKTRACE_PATTERN = re.compile(
    r'at\s+([\w.]+)\((\w+\.java):(\d+)\)',
    re.IGNORECASE
)

def parse_crash(logfile):
    with open(logfile) as f:
        content = f.read()

    crashes = []
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        if CRASH_PATTERN.search(lines[i]):
            crash = {
                'type': lines[i],
                'stacktrace': [],
                'context': lines[max(0, i-5):i+20]
            }
            # Extract stack trace
            for j in range(i, min(i+30, len(lines))):
                m = STACKTRACE_PATTERN.search(lines[j])
                if m:
                    crash['stacktrace'].append({
                        'method': m.group(1),
                        'file': m.group(2),
                        'line': m.group(3)
                    })
            crashes.append(crash)
            i += 30
        else:
            i += 1

    return crashes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('logfile')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    crashes = parse_crash(args.logfile)
    print(f"Found {len(crashes)} crash(es)\n")

    for i, crash in enumerate(crashes):
        print(f"[{i+1}] {crash['type']}")
        if crash['stacktrace']:
            print("  Stack trace:")
            for st in crash['stacktrace'][:5]:
                print(f"    {st['method']} ({st['file']}:{st['line']})")
        print()

if __name__ == "__main__":
    main()
