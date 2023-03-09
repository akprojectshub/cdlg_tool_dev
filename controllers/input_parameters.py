from dataclasses import dataclass, fields
from datetime import datetime
from controllers import configurations as config
import ast
from random import randint, uniform, choice

@dataclass
class InputParameters:

    Complexity_random_tree: list
    Number_event_logs: int
    Number_traces_per_event_log: list
    Drifts: list
    Drift_area: list
    Proportion_random_evolution_sector: list
    Noise: list
    Noisy_trace_prob: list
    Noisy_event_prob: list
    Timestamp_first_trace: list
    Trace_exp_arrival_sec: list
    Task_exp_duration_sec: list
    Gradual_drift_type: list
    Incremental_drift_number: list
    Recurring_drift_seasons: list


    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in {field.name for field in fields(InputParameters)}:
                setattr(self, key, value)




