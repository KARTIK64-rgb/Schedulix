from models import ProcessInput

def schedule_fcfs(processes: list[ProcessInput]):
    # FCFS uses a standard List/Queue.
    # We sort by arrival time to simulate the queue correctly.
    sorted_processes = sorted(processes, key=lambda x: x.arrival_time)
    
    current_time = 0
    gantt_chart = []
    process_metrics = {}
    
    for p in sorted_processes:
        if current_time < p.arrival_time:
            current_time = p.arrival_time
            
        start_time = current_time
        end_time = current_time + p.burst_time
        
        gantt_chart.append({
            "process": p.pid,
            "start": start_time,
            "end": end_time
        })
        
        current_time = end_time
        
        completion_time = end_time
        turnaround_time = completion_time - p.arrival_time
        waiting_time = turnaround_time - p.burst_time
        
        process_metrics[p.pid] = {
            "pid": p.pid,
            "completion_time": completion_time,
            "turnaround_time": turnaround_time,
            "waiting_time": waiting_time
        }
        
    metrics_list = list(process_metrics.values())
    avg_wt = sum(m["waiting_time"] for m in metrics_list) / len(metrics_list) if metrics_list else 0
    
    return {
        "gantt_chart": gantt_chart,
        "process_metrics": metrics_list,
        "average_waiting_time": round(avg_wt, 2)
    }
