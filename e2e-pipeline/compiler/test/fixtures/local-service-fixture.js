#!/usr/bin/env node
'use strict';

const net = require('node:net');

const portIndex = process.argv.indexOf('--port');
const hostIndex = process.argv.indexOf('--host');
const port = Number(process.argv[portIndex + 1]);
const host = hostIndex === -1 ? '127.0.0.1' : process.argv[hostIndex + 1];

if (!Number.isInteger(port) || port < 1 || port > 65535) {
  process.stderr.write('invalid --port\n');
  process.exit(64);
}

const server = net.createServer(function(socket) {
  socket.on('error', function() {
    // Readiness probes may disconnect immediately after connect.
  });
  socket.end('ready\n');
});

server.listen(port, host);

function shutdown() {
  server.close(function() {
    process.exit(0);
  });
  setTimeout(function() {
    process.exit(1);
  }, 2000).unref();
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
