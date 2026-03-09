from collections import deque
from models import ProcessInput

def schedule_round_robin(processes: list[ProcessInput], time_quantum: int):
    arrival_queue = sorted(processes, key=lambda x: x.arrival_time)
    
    n = len(processes)
    current_time = 0
    completed = 0
    
    ready_queue = deque()
    
    remaining_times = {p.pid: p.burst_time for p in processes}
    arrival_times = {p.pid: p.arrival_time for p in processes}
    
    gantt_chart = []
    process_metrics = {}
    
    idx = 0
    
    if n > 0 and arrival_queue[0].arrival_time > 0:
        current_time = arrival_queue[0].arrival_time
        
    while idx < n and arrival_queue[idx].arrival_time <= current_time:
        ready_queue.append(arrival_queue[idx])
        idx += 1
        
    while completed != n:
        if ready_queue:
            current_process = ready_queue.popleft()
            
            run_time = min(time_quantum, remaining_times[current_process.pid])
            start_time = current_time
            end_time = current_time + run_time
            
            # Execute
            gantt_chart.append({
                "process": current_process.pid,
                "start": start_time,
                "end": end_time
            })
            
            current_time = end_time
            remaining_times[current_process.pid] -= run_time
            
            # Enqueue new arrivals during execution period
            while idx < n and arrival_queue[idx].arrival_time <= current_time:
                ready_queue.append(arrival_queue[idx])
                idx += 1
                
            # If not finished, push back to queue
            if remaining_times[current_process.pid] > 0:
                ready_queue.append(current_process)
            else:
                completed += 1
                completion_time = current_time
                turnaround_time = completion_time - arrival_times[current_process.pid]
                waiting_time = turnaround_time - current_process.burst_time
                
                process_metrics[current_process.pid] = {
                    "pid": current_process.pid,
                    "completion_time": completion_time,
                    "turnaround_time": turnaround_time,
                    "waiting_time": waiting_time
                }
        else:
            # CPU is idle
            if idx < n:
                current_time = arrival_queue[idx].arrival_time
                while idx < n and arrival_queue[idx].arrival_time <= current_time:
                    ready_queue.append(arrival_queue[idx])
                    idx += 1

    merged_gantt = []
    for entry in gantt_chart:
        if merged_gantt and merged_gantt[-1]["process"] == entry["process"] and merged_gantt[-1]["end"] == entry["start"]:
            merged_gantt[-1]["end"] = entry["end"]
        else:
            merged_gantt.append(entry)

    metrics_list = [process_metrics[p.pid] for p in processes]
    avg_wt = sum(m["waiting_time"] for m in metrics_list) / len(metrics_list) if metrics_list else 0
    
    return {
        "gantt_chart": merged_gantt,
        "process_metrics": metrics_list,
        "average_waiting_time": round(avg_wt, 2)
    }
