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
from src.data_classes.evaluation_LP import getTP_FP
import src.data_classes.helpers_LP
import copy
from src.data_classes.Automated_evaluation import Automated_evaluation
import random

from class_collection import *


path_detected_collection = "C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/detected"
path_actual_collection = "C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/actual"

path_actual_csv_file = "C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/actual/drift_info.csv"
path_detected_csv_file = "C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/detected/drift_info.csv"
                                            ##########################################
                                            ######## Testing (perfect case) ##########
                                            ##########################################

"""# Actual: collection of logs; Detected: Collection of logs
# Testing: Automated Evaluation
Col_act = Collection()
Col_det = Collection()
Col_act.Extract_collection_of_drifts(path_actual_collection)
Col_det.Extract_collection_of_drifts(path_detected_collection)
Automated_evaluation(Col_act, Col_det, "index_based", 100)

# Actual: csv file; Detected: Collection of logs
Col_act = Collection()
Col_act.import_drift_and_noise_info_from_flat_file_csv(path_actual_csv_file)
# print("csv",Col_act.drifts[1])

Col_det = Collection()
Col_det.Extract_collection_of_drifts(path_detected_collection)

# print(len(Col_act.drifts))
# print(len(Col_det.drifts))
# print("fold",Col_det.drifts[1])
Automated_evaluation(Col_act, Col_det, "index_based", 100)

# Actual: collection of logs; Detected: csv file
Col_act = Collection()
Col_act.import_drift_and_noise_info_from_flat_file_csv(path_actual_collection)
Col_det = Collection()
Col_det.Extract_collection_of_drifts(path_detected_csv_file)
print(Automated_evaluation(Col_act, Col_det, "index_based", 100))

# Actual: csv file; Detected: csv file

Col_act = Collection()
Col_act.import_drift_and_noise_info_from_flat_file_csv(path_actual_csv_file)
Col_det = Collection()
Col_det.Extract_collection_of_drifts(path_detected_csv_file)
print(Automated_evaluation(Col_act, Col_det, "index_based", 100))


"""
                                            ##########################################
                                            ######## Testing (noisy case) ############
                                            ##########################################


def insert_trace_index_noise(trace_index,probability_of_changing_trace, percentage_of_change):
    if random.random() < probability_of_changing_trace:
        if random.random() >= 0.5:
            trace_index = trace_index * (1+percentage_of_change)
        elif random.random() < 0.5:
            trace_index = trace_index * (1-percentage_of_change)
    return trace_index

import copy

probability_of_changing_trace = 1
percentage_of_change = 0.7

Col_act = Collection()
Col_act.Extract_collection_of_drifts("C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/actual")
Col_act_modified = copy.copy(Col_act)

#print("Before Change",Col_act.drifts[0][0].change_info["1"]["change_trace_index"])


for drifts_pos in range(0,len(Col_act.drifts)):
    for drift_pos in range(0,len(Col_act.drifts[drifts_pos])):
        for change_info_key in list(Col_act.drifts[drifts_pos][drift_pos].change_info.keys()):
            for change_trace_index_pos in range(0,len(Col_act.drifts[drifts_pos][drift_pos].change_info[change_info_key]["change_trace_index"])):
                Col_act_modified.drifts[drifts_pos][drift_pos].change_info[change_info_key]["change_trace_index"][change_trace_index_pos] = insert_trace_index_noise(Col_act.drifts[drifts_pos][drift_pos].change_info[change_info_key]["change_trace_index"][change_trace_index_pos],probability_of_changing_trace, percentage_of_change)


#print("After_change", Col_act_modified.drifts[0][0].change_info["1"]["change_trace_index"])




# Testing: Automated Evaluation
Col_act = Collection()
Col_det = Collection()
Col_det.Extract_collection_of_drifts(path_detected_collection)
Automated_evaluation(Col_act_modified, Col_det, 100)

