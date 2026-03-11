import heapq
from models import ProcessInput
from scheduler.util.state_generator import generate_state_timeline

def schedule_priority_preemptive(processes: list[ProcessInput]):
    arrival_queue = sorted(processes, key=lambda x: x.arrival_time)
    
    n = len(processes)
    current_time = 0
    completed = 0
    
    # Priority Queue: (priority, arrival_time (tie breaker), pid, ProcessInput)
    # Lower numeric priority value = higher priority.
    ready_queue = [] 
    
    remaining_times = {p.pid: p.burst_time for p in processes}
    arrival_times = {p.pid: p.arrival_time for p in processes}
    
    gantt_chart = []
    process_metrics = {}
    
    last_process_id = None
    start_time_of_current = -1
    
    idx = 0
    
    while completed != n:
        while idx < n and arrival_queue[idx].arrival_time <= current_time:
            push_process = arrival_queue[idx]
            # Default priority to 0 if not provided
            pri = push_process.priority if push_process.priority is not None else 0
            heapq.heappush(ready_queue, (pri, push_process.arrival_time, push_process.pid, push_process))
            idx += 1
            
        if ready_queue:
            pri, arr_time, pid, current_process = heapq.heappop(ready_queue)
            
            if last_process_id != current_process.pid:
                if last_process_id is not None:
                    if start_time_of_current < current_time:
                        gantt_chart.append({
                            "process": last_process_id,
                            "start": start_time_of_current,
                            "end": current_time
                        })
                start_time_of_current = current_time
                last_process_id = current_process.pid
                
            remaining_times[current_process.pid] -= 1
            current_time += 1
            
            if remaining_times[current_process.pid] == 0:
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
                
                gantt_chart.append({
                    "process": current_process.pid,
                    "start": start_time_of_current,
                    "end": current_time
                })
                last_process_id = None
            else:
                heapq.heappush(ready_queue, (pri, current_process.arrival_time, current_process.pid, current_process))
        else:
            # CPU is idle
            current_time += 1
            
    merged_gantt = []
    for entry in gantt_chart:
        if merged_gantt and merged_gantt[-1]["process"] == entry["process"] and merged_gantt[-1]["end"] == entry["start"]:
            merged_gantt[-1]["end"] = entry["end"]
        else:
            merged_gantt.append(entry)
            
    metrics_list = [process_metrics[p.pid] for p in processes]
    avg_wt = sum(m["waiting_time"] for m in metrics_list) / len(metrics_list) if metrics_list else 0
    process_states = generate_state_timeline(processes, merged_gantt, metrics_list)
    
    return {
        "gantt_chart": merged_gantt,
        "process_metrics": metrics_list,
        "average_waiting_time": round(avg_wt, 2),
        "process_states": process_states
    }
