from enum import Enum
from random import uniform, randint


def select_random(data: list, option: str = 'random') -> any:
    if len(data) == 1:
        data_selected = data[0]
    elif len(data) == 2 and option == 'uniform':
        data_selected = uniform(data[0], data[1])
    elif len(data) == 2 and option == 'uniform_int':
        data_selected = randint(data[0], data[1])
    elif len(data) == 2 and option == 'uniform_step':
        data_selected = round(uniform(data[0], data[1]), 1)
    elif option == 'random':
        data_selected = data[randint(0, len(data) - 1)]
    else:
        data_selected = None
        Warning(f"Check function 'select_random' call: {data, option, data_selected}")

    if isinstance(data, float):
        data_selected = round(data_selected, 2)

    return data_selected


class InfoTypes(Enum):
    drift_info = "drift:info"
    noise_info = "noise:info"


class DriftTypes(Enum):
    sudden = 'sudden'
    gradual = 'gradual'
    recurring = 'recurring'
    incremental = 'incremental'


class ChangeTypes(Enum):
    sudden = 'sudden'
    gradual = 'gradual'


class TraceAttributes(Enum):

    concept_name = "concept:name"
    timestamp = "time:timestamp"
    model_version = "model_version:id"
