#!/usr/bin/env node
const fs = require('fs');

function parseCrash(logContent) {
    const lines = logContent.split('\n');
    const crashes = [];
    let currentCrash = null;

    for (const line of lines) {
        if (line.includes('FATAL') || line.includes('Exception')) {
            if (currentCrash) crashes.push(currentCrash);
            currentCrash = {
                timestamp: (line.match(/(\d{2}-\d{2} \d{2}:\d{2}:\d{2})/) || [])[1],
                type: (line.match(/([A-Z][A-Za-z]*Exception)/) || [])[1] || 'Unknown',
                stack: [],
            };
        } else if (currentCrash && line.match(/^\s+at\s+/)) {
            currentCrash.stack.push(line.trim());
        }
    }
    if (currentCrash) crashes.push(currentCrash);
    return crashes;
}

const file = process.argv[2];
if (!file) {
    console.log('Usage: node analyze.js <logfile>');
    process.exit(1);
}

const content = fs.readFileSync(file, 'utf8');
const crashes = parseCrash(content);
console.log(`Found ${crashes.length} crash(es)\n`);

for (const c of crashes.slice(0, 5)) {
    console.log(`[${c.timestamp}] ${c.type}`);
    for (const s of c.stack.slice(0, 5)) console.log(`  ${s}`);
    console.log('');
}
