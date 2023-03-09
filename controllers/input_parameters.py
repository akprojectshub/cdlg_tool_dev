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
    GRADUAL_DRIFT_TYPE: list

    # selected_complexity: str
    # selected_number_logs: int
    # selected_number_traces: int
    # selected_drift: str
    # selected_drift_area: list
    # selected_proportion_random_evolution: list
    # selected_noise: list
    # selected_noisy_trace_prob: list
    # selected_noisy_event_prob: list
    # selected_timestamp_first_trace: datetime
    # selected_trace_exp_arrival_sec: int
    # selected_task_exp_duration_sec: int


    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in {field.name for field in fields(InputParameters)}:
                setattr(self, key, value)

    # def select_par(self):
    #     selected_option = attribute_option_list[randint(0, len(attribute_option_list) - 1)]
    #     setattr(self, 'selected_', selected_option)
    #     return selected_option




