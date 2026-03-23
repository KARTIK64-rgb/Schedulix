from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_schedule_fcfs():
    response = client.post(
        "/schedule",
        json={
            "algorithm": "fcfs",
            "processes": [
                {"pid": "P1", "arrival_time": 0, "burst_time": 5},
                {"pid": "P2", "arrival_time": 1, "burst_time": 3},
            ],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "average_waiting_time" in data
    assert "process_metrics" in data
    assert "gantt_chart" in data
    assert len(data["process_metrics"]) == 2


def test_schedule_sjf_preemptive():
    response = client.post(
        "/schedule",
        json={
            "algorithm": "sjf_preemptive",
            "processes": [
                {"pid": "P1", "arrival_time": 0, "burst_time": 8},
                {"pid": "P2", "arrival_time": 1, "burst_time": 4},
            ],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "average_waiting_time" in data
    assert "process_metrics" in data


def test_schedule_round_robin():
    response = client.post(
        "/schedule",
        json={
            "algorithm": "round_robin",
            "time_quantum": 2,
            "processes": [
                {"pid": "P1", "arrival_time": 0, "burst_time": 5},
                {"pid": "P2", "arrival_time": 0, "burst_time": 3},
            ],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "average_waiting_time" in data
    assert "process_metrics" in data


def test_schedule_priority_preemptive():
    response = client.post(
        "/schedule",
        json={
            "algorithm": "priority_preemptive",
            "ageing_rate": 2,
            "processes": [
                {"pid": "P1", "arrival_time": 0, "burst_time": 5, "priority": 2},
                {"pid": "P2", "arrival_time": 1, "burst_time": 3, "priority": 1},
            ],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "average_waiting_time" in data
    assert "process_metrics" in data


def test_round_robin_missing_time_quantum():
    response = client.post(
        "/schedule",
        json={
            "algorithm": "round_robin",
            "processes": [
                {"pid": "P1", "arrival_time": 0, "burst_time": 5},
            ],
        },
    )
    assert response.status_code == 400
    assert "time quantum" in response.json()["detail"].lower()


def test_invalid_algorithm():
    response = client.post(
        "/schedule",
        json={
            "algorithm": "unknown_algo",
            "processes": [{"pid": "P1", "arrival_time": 0, "burst_time": 5}],
        },
    )
    assert response.status_code == 422


def test_missing_processes():
    response = client.post(
        "/schedule",
        json={
            "algorithm": "fcfs",
            "processes": [],
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Process list cannot be empty"
