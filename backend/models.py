from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class AlgorithmEnum(str, Enum):
    fcfs = "fcfs"
    sjf_preemptive = "sjf_preemptive"
    priority_preemptive = "priority_preemptive"
    round_robin = "round_robin"

class ProcessInput(BaseModel):
    pid: str
    arrival_time: int
    burst_time: int
    priority: Optional[int] = None

class ScheduleRequest(BaseModel):
    algorithm: AlgorithmEnum
    time_quantum: Optional[int] = None
    processes: List[ProcessInput]
