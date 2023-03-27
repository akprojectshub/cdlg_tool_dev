from dataclasses import dataclass, fields
from datetime import datetime
from controllers import configurations as config
import ast
from random import randint, uniform, choice

@dataclass
class InputParameters:

    Process_tree_complexity: list
    Process_tree_evolution_proportion: list
    Number_event_logs: list
    Number_traces_per_event_log: list
    Drift_types: list
    Number_drifts_per_log: list
    Drift_area: list
    Noise: list
    Noisy_trace_prob: list
    Noisy_event_prob: list
    Timestamp_first_trace: list
    Trace_exp_arrival_sec: list
    Task_exp_duration_sec: list
    Gradual_drift_type: list
    Incremental_drift_number: list
    Recurring_drift_number: list

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in {field.name for field in fields(InputParameters)}:
                setattr(self, key, value)

