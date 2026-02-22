document.addEventListener('DOMContentLoaded', () => {
    const activeSessionsEl = document.getElementById('activeSessions');
    const uniqueIpsEl = document.getElementById('uniqueIps');
    const totalEventsEl = document.getElementById('totalEvents');
    const lastUpdatedEl = document.getElementById('lastUpdated');
    const logTableBody = document.querySelector('#logTable tbody');
    const incidentTableBody = document.querySelector('#incidentTable tbody');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    // Tab Switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.tab;
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(`${target}Tab`).classList.add('active');
        });
    });

    function fetchStats() {
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                updateDashboard(data);
            })
            .catch(error => console.error('Error fetching stats:', error));
    }

    function updateDashboard(data) {
        activeSessionsEl.textContent = data.active_sessions;
        uniqueIpsEl.textContent = data.unique_ips;
        totalEventsEl.textContent = data.total_events;

        const now = new Date();
        lastUpdatedEl.textContent = `Last check: ${now.toLocaleTimeString()}`;

        renderLogs(data.logs);
        renderIncidents(data.incidents);
    }

    function renderLogs(logs) {
        logTableBody.innerHTML = '';
        if (logs.length === 0) {
            logTableBody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 2rem;">No events captured yet...</td></tr>';
            return;
        }

        logs.forEach(log => {
            const row = document.createElement('tr');
            const timestamp = new Date(log.timestamp).toLocaleString();
            let eventType = log.eventid.replace('cowrie.', '');
            let eventColor = '#e0e6ed';

            if (eventType.includes('login.success')) eventColor = '#ef4444';
            else if (eventType.includes('login.failed')) eventColor = '#f59e0b';
            else if (eventType.includes('command')) eventColor = '#10b981';

            let details = log.message;
            if (log.input) details = `Command: <span style="font-family:monospace; background:rgba(255,255,255,0.1); padding:2px 4px; border-radius:3px;">${log.input}</span>`;
            else if (log.username && log.password) details = `User: <b>${log.username}</b> Pass: <b>${log.password}</b>`;

            const risk = log.risk_score || 0;
            const riskClass = risk > 60 ? 'risk-high' : risk > 30 ? 'risk-med' : 'risk-low';

            row.innerHTML = `
                <td class="log-timestamp">${timestamp}</td>
                <td class="log-ip">${log.src_ip}</td>
                <td class="log-event" style="color: ${eventColor}">${eventType}</td>
                <td class="log-details">${details}</td>
                <td><span class="risk-badge ${riskClass}">${risk}%</span></td>
            `;
            logTableBody.appendChild(row);
        });
    }

    function renderIncidents(incidents) {
        incidentTableBody.innerHTML = '';
        if (incidents.length === 0) {
            incidentTableBody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding: 2rem;">No suspicious activity requiring response.</td></tr>';
            return;
        }

        incidents.forEach(inc => {
            const row = document.createElement('tr');
            const riskClass = inc.max_risk > 60 ? 'risk-high' : inc.max_risk > 30 ? 'risk-med' : 'risk-low';
            const actionBtn = inc.is_blocked ?
                `<button class="btn-unblock" onclick="toggleBlock('${inc.ip}', false)">UNBLOCK</button>` :
                `<button class="btn-block" onclick="toggleBlock('${inc.ip}', true)">BLOCK</button>`;

            row.innerHTML = `
                <td><b>${inc.ip}</b> ${inc.is_blocked ? '<span class="blocked-tag">[AUTO-BLOCKED]</span>' : ''}</td>
                <td><span class="risk-badge ${riskClass}">${inc.max_risk}%</span></td>
                <td>${inc.events}</td>
                <td>${new Date(inc.last_seen).toLocaleTimeString()}</td>
                <td>${actionBtn}</td>
            `;
            incidentTableBody.appendChild(row);
        });
    }

    window.toggleBlock = (ip, block) => {
        const endpoint = block ? '/api/block' : '/api/unblock';
        fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ip: ip })
        })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    fetchStats(); // Refresh immediately
                }
            });
    };

    fetchStats();
    setInterval(fetchStats, 3000);
});
