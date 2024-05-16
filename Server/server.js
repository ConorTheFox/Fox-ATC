const express = require('express');
const WebSocket = require('ws');
const http = require('http');
const { spawn } = require('child_process');
const cors = require('cors'); // For Local Development

const version = '1.0.0';
console.log(`Server version: ${version}`);

const radios = {
    'SAN': {
        'Ground': 'http://d.liveatc.net/ksan1_gnd',
        'Tower': 'http://d.liveatc.net/ksan1_twr',
        'Departure': 'http://d.liveatc.net/ksan_dep_125150',
    }
}

const app = express();
app.use(cors()); // For Local Development

const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

wss.on('connection', function connection(ws) {
    console.log('Client connected');

    ws.on('message', function incoming(message) {
        console.log('Received message:', message);
        const { airport_code, frequency } = JSON.parse(message);
        console.log(`Client requested to monitor airport: ${airport_code}, frequency: ${frequency}`);
        const stream_url = radios[airport_code][frequency];
        monitorTraffic(stream_url, ws);
    });

    ws.on('close', function () {
        console.log('Client disconnected');
    });

    ws.on('error', function (error) {
        console.error('WebSocket error: ', error);
    });
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});

async function monitorTraffic(stream_url, ws) {
    const pythonProcess = spawn('python', ['transcribe.py', stream_url]);

    pythonProcess.stdout.on('data', (data) => {
        const transcription = data.toString().trim();
        ws.send(transcription);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
    });
}
