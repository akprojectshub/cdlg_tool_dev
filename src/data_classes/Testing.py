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

from class_collection import *

                                            ##########################################
                                            ######## Testing (perfect case) ##########
                                            ##########################################

# Actual: collection of logs; Detected: Collection of logs

"""if __name__ == '__main__':
    #Testing: Automated Evaluation
    Col_act = Collection()
    Col_det = Collection()
    Col_act.Extract_collection_of_drifts("C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/actual")
    Col_det.Extract_collection_of_drifts("C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/detected")
    Automated_evaluation(Col_act, Col_det, "index_based",100)"""

# Actual: csv file; Detected: Collection of logs
if __name__ == '__main__':
    Col_act = Collection()
    Col_act.import_drift_and_noise_info_from_flat_file_csv("C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/actual/drift_info.csv")
    #print("csv",Col_act.drifts[1])

    #print("################################")
    Col_det = Collection()
    Col_det.Extract_collection_of_drifts("C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/detected")

    #print(len(Col_act.drifts))
    #print(len(Col_det.drifts))
    #print("fold",Col_det.drifts[1])
    Automated_evaluation(Col_act, Col_det, "index_based",100)

# Actual: collection of logs; Detected: csv file
"""if __name__ == '__main__':
    Col_act = Collection()
    Col_act.import_drift_and_noise_info_from_flat_file_csv("C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/actual")
    Col_det = Collection()
    Col_det.Extract_collection_of_drifts("C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/detected/drift_info.csv")
    print(Automated_evaluation(Col_act, Col_det, "index_based",100))

"""


# Actual: csv file; Detected: csv file

"""if __name__ == '__main__':
    Col_act = Collection()
    Col_act.import_drift_and_noise_info_from_flat_file_csv("C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/actual/drift_info.csv")
    Col_det = Collection()
    Col_det.Extract_collection_of_drifts("C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/detected/drift_info.csv")
    print(Automated_evaluation(Col_act, Col_det, "index_based",100))

"""


                                            ##########################################
                                            ######## Testing (noisy case) ##########
                                            ##########################################



