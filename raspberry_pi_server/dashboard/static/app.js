const socket = io();

socket.on('status_update', (data) => {
    // Update stations
    document.getElementById('state-a').textContent = data.station_a.state;
    document.getElementById('track-a').textContent = data.station_a.track;
    document.getElementById('state-b').textContent = data.station_b.state;
    document.getElementById('track-b').textContent = data.station_b.track;

    // Update rings
    updateRing('ring-a', data.station_a.state);
    updateRing('ring-b', data.station_b.state);

    // Update sync meter
    const meter = document.getElementById('sync-meter');
    if (data.current_state === 'matched') {
        meter.style.width = '100%';
        addConfetti();
    } else if (data.station_a.state === 'scanning' || data.station_b.state === 'scanning') {
        meter.style.width = '50%';
    } else {
        meter.style.width = '0%';
    }

    // Update stats
    document.getElementById('sync-count').textContent = data.sync_count;
    document.getElementById('avg-time').textContent = data.avg_sync_time.toFixed(2) + 's';
    document.getElementById('countdown').textContent = data.countdown;

    // Update events
    const eventList = document.getElementById('event-list');
    eventList.innerHTML = '';
    data.events.slice(-10).forEach(event => {
        const li = document.createElement('li');
        li.textContent = `${new Date(event.time * 1000).toLocaleTimeString()}: ${event.event}`;
        eventList.appendChild(li);
    });
});

function updateRing(ringId, state) {
    const ring = document.getElementById(ringId);
    ring.className = 'ring';
    if (state === 'scanning') {
        ring.classList.add('scanning');
    } else if (state === 'matched') {
        ring.classList.add('matched');
    }
}

function addConfetti() {
    for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + 'vw';
        confetti.style.animationDelay = Math.random() * 3 + 's';
        document.body.appendChild(confetti);
        setTimeout(() => document.body.removeChild(confetti), 3000);
    }
}