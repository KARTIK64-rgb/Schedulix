from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ScheduleRequest, AlgorithmEnum
from scheduler.fcfs import schedule_fcfs
from scheduler.sjf_preemptive import schedule_sjf_preemptive
from scheduler.priority_preemptive import schedule_priority_preemptive
from scheduler.round_robin import schedule_round_robin

app = FastAPI(title="CPU Scheduling Simulator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/schedule")
def schedule_processes(request: ScheduleRequest):
    if not request.processes:
        raise HTTPException(status_code=400, detail="Process list cannot be empty")

    if request.algorithm == AlgorithmEnum.fcfs:
        return schedule_fcfs(request.processes)
    elif request.algorithm == AlgorithmEnum.sjf_preemptive:
        return schedule_sjf_preemptive(request.processes)
    elif request.algorithm == AlgorithmEnum.priority_preemptive:
        return schedule_priority_preemptive(request.processes, request.ageing_rate)
    elif request.algorithm == AlgorithmEnum.round_robin:
        if request.time_quantum is None or request.time_quantum <= 0:
            raise HTTPException(status_code=400, detail="Time quantum must be a positive integer for Round Robin")
        return schedule_round_robin(request.processes, request.time_quantum)
    
    raise HTTPException(status_code=400, detail="Invalid algorithm")
