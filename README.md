# CPU Scheduling Simulator

A web-based CPU scheduling simulator that visualizes process execution and calculates key scheduling metrics. 

## Features

- **Four Scheduling Algorithms Supported:**
  - First Come First Serve (FCFS)
  - Shortest Remaining Time First (SJF Preemptive)
  - Priority Scheduling (Preemptive)
  - Round Robin
- **Interactive Input:** Add and remove processes on the go with custom arrival times, burst times, and priorities.
- **Generated Gantt Chart:** Instant generation of a flexible, proportional Gantt chart to clearly show process execution order and preemption after running the scheduler.
- **Detailed Metrics:** Automatically calculates:
  - Completion Time
  - Turnaround Time
  - Waiting Time
  - Average Waiting Time
- **Clean Architecture:** Built cleanly with a FastAPI backend (handling algorithmic logic) and a Vanilla JavaScript/HTML/CSS frontend.
