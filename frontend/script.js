document.addEventListener('DOMContentLoaded', () => {
    const processTableBody = document.querySelector('#process-table tbody');
    const addProcessBtn = document.getElementById('add-process-btn');
    const runBtn = document.getElementById('run-btn');
    const algorithmSelect = document.getElementById('algorithm');
    const tqContainer = document.getElementById('tq-container');
    const ageingContainer = document.getElementById('ageing-container');

    let processCount = 0;

    function addProcessRow() {
        processCount++;
        const tr = document.createElement('tr');

        tr.innerHTML = `
            <td><input type="text" class="pid-input" value="P${processCount}" readonly></td>
            <td><input type="number" class="at-input" value="0" min="0"></td>
            <td><input type="number" class="bt-input" value="1" min="1"></td>
            <td class="priority-col" style="display: ${algorithmSelect.value === 'priority_preemptive' ? 'table-cell' : 'none'};">
                <input type="number" class="pri-input" value="1" min="0">
            </td>
            <td><button class="remove-btn">Remove</button></td>
        `;

        tr.querySelector('.remove-btn').addEventListener('click', () => {
            tr.remove();
        });

        processTableBody.appendChild(tr);
    }

    // Initial row
    addProcessRow();

    addProcessBtn.addEventListener('click', addProcessRow);

    algorithmSelect.addEventListener('change', (e) => {
        const alg = e.target.value;
        const currentPriorityCols = document.querySelectorAll('.priority-col');

        if (alg === 'round_robin') {
            tqContainer.style.display = 'flex';
        } else {
            tqContainer.style.display = 'none';
        }

        if (alg === 'priority_preemptive') {
            currentPriorityCols.forEach(col => col.style.display = 'table-cell');
            ageingContainer.style.display = 'flex';
        } else {
            currentPriorityCols.forEach(col => col.style.display = 'none');
            ageingContainer.style.display = 'none';
        }
    });

    runBtn.addEventListener('click', async () => {
        const rows = document.querySelectorAll('#process-table tbody tr');
        if (rows.length === 0) {
            alert("Please add at least one process.");
            return;
        }

        const processes = [];
        const algorithm = algorithmSelect.value;
        let time_quantum = null;
        let ageing_rate = null;

        if (algorithm === 'round_robin') {
            time_quantum = parseInt(document.getElementById('time-quantum').value, 10);
            if (isNaN(time_quantum) || time_quantum <= 0) {
                alert("Please enter a valid positive time quantum.");
                return;
            }
        }

        if (algorithm === 'priority_preemptive') {
            ageing_rate = parseInt(document.getElementById('ageing-rate').value, 10);
            if (isNaN(ageing_rate) || ageing_rate <= 0) {
                alert("Please enter a valid positive ageing rate.");
                return;
            }
        }

        rows.forEach(row => {
            const pid = row.querySelector('.pid-input').value;
            const arrival_time = parseInt(row.querySelector('.at-input').value, 10);
            const burst_time = parseInt(row.querySelector('.bt-input').value, 10);

            const processData = { pid, arrival_time, burst_time };

            if (algorithm === 'priority_preemptive') {
                processData.priority = parseInt(row.querySelector('.pri-input').value, 10);
            }

            processes.push(processData);
        });

        const payload = {
            algorithm,
            processes
        };

        if (time_quantum !== null) {
            payload.time_quantum = time_quantum;
        }

        if (ageing_rate !== null) {
            payload.ageing_rate = ageing_rate;
        }

        try {
            const response = await fetch('https://schedulix-kud5.onrender.com', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errData = await response.json();
                alert(`Error: ${errData.detail || 'Scheduling failed'}`);
                return;
            }

            const data = await response.json();
            displayResults(data);
        } catch (error) {
            alert("Failed to connect to the backend. Is it running?");
            console.error(error);
        }
    });

    function displayResults(data) {
        document.getElementById('results').style.display = 'block';

        // Render Gantt Chart
        const ganttContainer = document.getElementById('gantt-chart');
        ganttContainer.innerHTML = '';

        data.gantt_chart.forEach(block => {
            const duration = block.end - block.start;
            const blockEl = document.createElement('div');
            blockEl.className = 'gantt-block';
            blockEl.style.flexGrow = duration;

            blockEl.innerHTML = `
                <div><strong>${block.process}</strong></div>
                <div class="gantt-time">
                    <span>${block.start}</span>
                    <span>${block.end}</span>
                </div>
            `;
            ganttContainer.appendChild(blockEl);
        });

        // Render Metrics Table
        const metricsBody = document.querySelector('#metrics-table tbody');
        metricsBody.innerHTML = '';

        data.process_metrics.forEach(m => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${m.pid}</td>
                <td>${m.completion_time}</td>
                <td>${m.turnaround_time}</td>
                <td>${m.waiting_time}</td>
            `;
            metricsBody.appendChild(tr);
        });

        // Render State Timeline
        const timelineHeader = document.getElementById('timeline-header');
        const timelineBody = document.querySelector('#timeline-table tbody');

        timelineHeader.innerHTML = '<th>PID</th>';
        timelineBody.innerHTML = '';

        if (data.process_states && Object.keys(data.process_states).length > 0) {
            // Determine max time units
            const firstPid = Object.keys(data.process_states)[0];
            const maxTime = data.process_states[firstPid].length;

            // Generate headers for time units
            for (let t = 0; t < maxTime; t++) {
                const th = document.createElement('th');
                th.textContent = t;
                timelineHeader.appendChild(th);
            }

            // Generate rows for each process
            for (const item of data.process_metrics) {
                // Ensure we print in order of original process list
                const pid = item.pid;
                const states = data.process_states[pid];

                const tr = document.createElement('tr');
                const tdPid = document.createElement('td');
                tdPid.innerHTML = `<strong>${pid}</strong>`;
                tr.appendChild(tdPid);

                if (states) {
                    for (let t = 0; t < maxTime; t++) {
                        const state = states[t] || "UNKNOWN";
                        const td = document.createElement('td');
                        td.className = `state-${state}`;

                        // Abbreviate state for better fit if needed, but let's try full word first
                        td.textContent = state;
                        tr.appendChild(td);
                    }
                }

                timelineBody.appendChild(tr);
            }
        }

        document.getElementById('avg-wt-value').textContent = data.average_waiting_time;
    }
});
