document.addEventListener('DOMContentLoaded', function () {
    const monitorButton = document.getElementById('monitor-button');
    const centerBox = document.getElementById('center-box');
    
    monitorButton.addEventListener('click', () => {
        monitorTraffic();
        centerBox.innerHTML = '<p>Sit back and relax...</p>';
    });

    function monitorTraffic() {
        console.log('Monitor Traffic button clicked');
        // Get User Inputs
        const airport_code = document.getElementById('airport-code').value;
        const frequency = document.getElementById('frequency').value;
        // WebSocket Connection To Server
        const socket = new WebSocket('ws://localhost:3000/');

        // On Connection Open
        socket.onopen = function () {
            console.log('Connected to server');
            // Send User Inputs to Server
            socket.send(JSON.stringify({ airport_code, frequency }));
        };

        // On Connection Error
        socket.onerror = function (error) {
            console.error('WebSocket Error: ', error);
        };

        // On Message Received
        socket.onmessage = function (event) {
            console.log('Message from server: ', event.data);
            // Display Message
            centerBox.innerHTML = `<p>${event.data}</p>`;
        };

        // On Connection Close
        socket.onclose = function (event) {
            console.log('Connection closed: ', event);
        };
    }
});