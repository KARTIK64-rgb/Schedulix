import heapq
from models import ProcessInput
from scheduler.util.state_generator import generate_state_timeline

def schedule_priority_preemptive(processes: list[ProcessInput], ageing_rate: int = None):
    arrival_queue = sorted(processes, key=lambda x: x.arrival_time)
    
    n = len(processes)
    current_time = 0
    completed = 0
    
    # Priority Queue: (priority, arrival_time (tie breaker), pid, ProcessInput)
    # Lower numeric priority value = higher priority.
    ready_queue = [] 
    
    remaining_times = {p.pid: p.burst_time for p in processes}
    arrival_times = {p.pid: p.arrival_time for p in processes}
    
    # Tracking for Ageing
    wait_ticks = {p.pid: 0 for p in processes}
    current_priorities = {p.pid: (p.priority if p.priority is not None else 0) for p in processes}
    
    gantt_chart = []
    process_metrics = {}
    
    last_process_id = None
    start_time_of_current = -1
    
    idx = 0
    
    while completed != n:
        while idx < n and arrival_queue[idx].arrival_time <= current_time:
            push_process = arrival_queue[idx]
            pri = current_priorities[push_process.pid]
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
                # Process not finished, push back with current specific priority
                heapq.heappush(ready_queue, (current_priorities[current_process.pid], current_process.arrival_time, current_process.pid, current_process))
                
            # Apply Ageing to all processes CURRENTLY waiting in the ready queue
            if ageing_rate is not None and ageing_rate > 0 and len(ready_queue) > 0:
                aged_any = False
                new_ready_queue = []
                for p_pri, p_arr, p_pid, p_proc in ready_queue:
                    # By ignoring the currently running process (it was popped above and potentially pushed back),
                    # Wait, the currently running process WAS pushed back above if it didn't finish.
                    # We should NOT age the process that just ran.
                    if p_pid != current_process.pid:
                        wait_ticks[p_pid] += 1
                        if wait_ticks[p_pid] > 0 and wait_ticks[p_pid] % ageing_rate == 0:
                            current_priorities[p_pid] -= 1
                            aged_any = True
                    
                    # Store tuple with updated (or unchanged) priority
                    new_ready_queue.append((current_priorities[p_pid], p_arr, p_pid, p_proc))
                
                if aged_any:
                    ready_queue = new_ready_queue
                    heapq.heapify(ready_queue)
                else:
                    ready_queue = new_ready_queue
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
