import heapq
from models import ProcessInput

def schedule_sjf_preemptive(processes: list[ProcessInput]):
    # Sort processes by arrival time to know when they come into the system.
    # processes list is essentially our arrival queue
    arrival_queue = sorted(processes, key=lambda x: x.arrival_time)
    
    n = len(processes)
    current_time = 0
    completed = 0
    
    ready_queue = [] # Min Heap: (remaining_time, arrival_time (as tie breaker), pid, ProcessInput)
    
    remaining_times = {p.pid: p.burst_time for p in processes}
    arrival_times = {p.pid: p.arrival_time for p in processes}
    
    gantt_chart = []
    process_metrics = {}
    
    last_process_id = None
    start_time_of_current = -1
    
    idx = 0
    
    while completed != n:
        # Push processes that have arrived up to current_time into the ready queue
        while idx < n and arrival_queue[idx].arrival_time <= current_time:
            push_process = arrival_queue[idx]
            # Use remaining time, then arrival time as tie breakers
            heapq.heappush(ready_queue, (remaining_times[push_process.pid], push_process.arrival_time, push_process.pid, push_process))
            idx += 1
            
        if ready_queue:
            # We peek first to see who should run
            rem_time, arr_time, pid, current_process = heapq.heappop(ready_queue)
            
            # If we switched processes or it's the first process
            if last_process_id != current_process.pid:
                # Close out the previous gantt block if it exists
                if last_process_id is not None:
                    if start_time_of_current < current_time:
                        gantt_chart.append({
                            "process": last_process_id,
                            "start": start_time_of_current,
                            "end": current_time
                        })
                start_time_of_current = current_time
                last_process_id = current_process.pid
                
            # Execute for 1 unit of time
            remaining_times[current_process.pid] -= 1
            current_time += 1
            
            # Check if process is completed
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
                
                # Close the block
                gantt_chart.append({
                    "process": current_process.pid,
                    "start": start_time_of_current,
                    "end": current_time
                })
                last_process_id = None # Reset so next pop starts a new block
            else:
                # Put it back in the queue with updated remaining time
                heapq.heappush(ready_queue, (remaining_times[current_process.pid], current_process.arrival_time, current_process.pid, current_process))
        else:
            # CPU is idle
            current_time += 1
            
    # Combine consecutive Gantt chart entries for the same process
    merged_gantt = []
    for entry in gantt_chart:
        if merged_gantt and merged_gantt[-1]["process"] == entry["process"] and merged_gantt[-1]["end"] == entry["start"]:
            merged_gantt[-1]["end"] = entry["end"]
        else:
            merged_gantt.append(entry)
            
    # Reorder metrics to match original input order
    metrics_list = [process_metrics[p.pid] for p in processes]
    avg_wt = sum(m["waiting_time"] for m in metrics_list) / len(metrics_list) if metrics_list else 0
    
    return {
        "gantt_chart": merged_gantt,
        "process_metrics": metrics_list,
        "average_waiting_time": round(avg_wt, 2)
    }
