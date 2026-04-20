#!/usr/bin/env ts-node
interface Crash {
    app: string;
    exception: string;
    thread: string;
    stackTrace: string[];
}

function parseCrash(lines: string[]): Crash {
    const crash: Crash = {
        app: 'unknown',
        exception: 'unknown',
        thread: 'main',
        stackTrace: [],
    };

    for (const line of lines) {
        if (/(\w+Exception|Error):\s+(.+)/.test(line)) {
            const m = line.match(/(\w+(?:Exception|Error)):/);
            if (m) crash.exception = m[1];
        }
        if (/^\s+at\s+/.test(line)) {
            crash.stackTrace.push(line.trim());
        }
    }
    return crash;
}

const input = require('fs').readFileSync(0, 'utf-8');
const crash = parseCrash(input.split('\n'));
console.log('💥 Crash Analysis');
console.log('  App: ' + crash.app);
console.log('  Exception: ' + crash.exception);
console.log('  Thread: ' + crash.thread);
if (crash.stackTrace.length > 0) {
    console.log('  Stack (top 3):');
    crash.stackTrace.slice(0, 3).forEach(line => {
        console.log('    ' + line.substring(0, 80));
    });
}
