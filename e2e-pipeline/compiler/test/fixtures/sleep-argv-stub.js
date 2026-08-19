#!/usr/bin/env node
'use strict';

const fs = require('node:fs');

const logPath = process.env.E2E_SLEEP_STUB_LOG;
if (logPath) {
  fs.appendFileSync(logPath, JSON.stringify(process.argv.slice(2)) + '\n');
}
