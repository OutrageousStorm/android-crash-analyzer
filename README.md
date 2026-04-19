# 💥 Android Crash Analyzer

Parse Android crash logs, ANRs, and tombstones. Extract stack traces and identify root causes.

```bash
adb logcat > crash.log
python3 analyze.py crash.log
```

Outputs:
- Root cause process
- Exception type
- Stack trace with line numbers
- Relevant system logs before crash
- Suggestions for fixes
