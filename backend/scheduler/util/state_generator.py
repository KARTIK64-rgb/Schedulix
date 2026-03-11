def generate_state_timeline(processes, gantt_chart, metrics_list):
    """
    Given the list of processes, the generated gantt_chart, and process metrics,
    returns a dictionary mapping pid to a list of states.
    
    States:
      - NEW (before arrival)
      - READY (arrived, waiting to run)
      - RUNNING (currently executing in Gantt chart)
      - TERMINATED (execution complete)
    """
    # Find the maximum time the simulation ran
    max_time = 0
    if gantt_chart:
        max_time = max(block["end"] for block in gantt_chart)
        
    process_states = {}
    
    # Create lookup dictionaries for easier access
    arrival_times = {p.pid: p.arrival_time for p in processes}
    completion_times = {m["pid"]: m["completion_time"] for m in metrics_list}
    
    # Create a map of pid to a list of (start, end) execution blocks
    execution_blocks = {p.pid: [] for p in processes}
    for block in gantt_chart:
        execution_blocks[block["process"]].append((block["start"], block["end"]))
        
    for p in processes:
        pid = p.pid
        arrival = arrival_times[pid]
        completion = completion_times.get(pid, 0)
        
        timeline = []
        for t in range(max_time):
            state = "UNKNOWN"
            
            if t < arrival:
                state = "NEW"
            elif t >= completion:
                state = "TERMINATED"
            else:
                # Process has arrived but not completed. Is it running at time t?
                is_running = False
                for start, end in execution_blocks[pid]:
                    if start <= t < end:
                        is_running = True
                        break
                
                if is_running:
                    state = "RUNNING"
                else:
                    state = "READY"
            
            timeline.append(state)
                    
        process_states[pid] = timeline
        
    return process_states
