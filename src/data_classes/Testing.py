import pm4py
import os
from copy import deepcopy
from dataclasses import dataclass, field
from collections import defaultdict
import pandas as pd
import pm4py
import copy

from src.utilities import InfoTypes
from src.data_classes.class_drift import DriftInfo
from src.data_classes.class_noise import NoiseInfo
from src.utilities import TraceAttributes
import datetime
import re

from class_collection import *

Col_act = Collection()
Col_det = Collection()

Col_act.Extract_collection_of_drifts("C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/experiments_all_types_v3_1685372669_actual")
Col_det.Extract_collection_of_drifts("C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/experiments_all_types_v3_1685372669_detected")


Col_act.evaluate(Col_det)

print(Col_act.TP)
print(Col_act.FN)
print(Col_act.FP)
