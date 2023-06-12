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
from class_collection import *


def Automated_evaluation (Col_act, Col_det, eval_type): #Eval type returns what type of evaluation is needed (TS or TR)
    global TP
    global FP
    TP = 0
    FP = 0
    if eval_type == "TS":
        return evaluate_using_timestamps(Col_act, Col_det)
    elif eval_type =="TR":
        return evaluate_lp_method(Col_act,Col_det,20)


def extract_change_moments(drifts_in_log: list()):  # takes a list of drift instances
    drift_moments = list()
    for drift_instance in drifts_in_log:  # is a list containing all the drift instances of a single log
        change_id = 1
        for change_moment_info in list(drift_instance.change_info.values()):
            if change_moment_info["change_type"] == "gradual":
                drift_moments.append((change_id, drift_instance.drift_type, change_moment_info["change_start"]))
                change_id += 1
                drift_moments.append((change_id, drift_instance.drift_type, change_moment_info["change_end"]))
                change_id += 1
            elif change_moment_info["change_type"] == "sudden":
                drift_moments.append((change_id, drift_instance.drift_type, change_moment_info["change_start"]))
                change_id += 1
    return drift_moments  # change_moments stores data in this format [(driftID,"drift_type1","TimeStamp1"),driftID,"drift_type1","TimeStamp1"),driftID,"drift_type1","TimeStamp1")]


def matching(change_inf_act, change_mom_det):

    global TP
    global FP

    change_mom_det_filtered = check_drift_type(change_inf_act,change_mom_det)  # return the change moments in the change_moment_det that match the drift type of the actual change moment
    change_mom_det_to_del = []
    if len(change_mom_det_filtered) > 0:
        change_mom_diff = [abs(cm[2] - change_inf_act[2]) for cm in change_mom_det_filtered]
        lowest_change_mom_diff_index = change_mom_diff.index(min(change_mom_diff))
        if check_latency(change_inf_act[2], change_mom_det_filtered[lowest_change_mom_diff_index][2], 20) == True:
            TP += 1  # the drift is in both the actual and the detected
            change_mom_det_to_del.append(change_mom_det_filtered[
                                             lowest_change_mom_diff_index])  # remove the matching change from the list of change moments in the detected drifts

    #    elif Col_act.check_latency(change_inf_act[2], change_mom_det_filtered[lowest_change_mom_diff_index][2],
    #                            20) == False:
    #        Col_act.FN += 1  # The drift is in the actual but not in the detected

    #elif len(change_mom_det_filtered) == 0:
    #    Col_act.FN += 1  # there is no drift of the same type in the detected drift
    return change_mom_det_to_del


def check_latency(cm_act, cm_det, lag):
    if (abs((cm_act - cm_det).days) <= lag):
        return True
    else:
        return False


def check_drift_type(change_inf_act, change_mom_det):
    return [change_inf_det for change_inf_det in change_mom_det if change_inf_det[1] == change_inf_act[1]]




def evaluate_using_timestamps(Col_act, Col_det):

    global TP
    global FP

    drift_ids_act = [DI_act[0].log_id for DI_act in Col_act.drifts]
    drift_ids_det = [DI_det[0].log_id for DI_det in Col_det.drifts]
    drift_ids_det_left = drift_ids_det.copy()
    change_mom_det_to_del = list()
    for drift_pos in range(0,
                           len(Col_act.drifts)):  # Col_act.drifts is a list of drifts each change moment in a log is stored in an instance and each instance belonging to the same log are saved in the same list
        change_mom_act = extract_change_moments(Col_act.drifts[drift_pos])

        if drift_ids_act[drift_pos] in drift_ids_det:
            pos_drift_to_match = drift_ids_det.index(drift_ids_act[drift_pos])
            change_mom_det = extract_change_moments(Col_det.drifts[pos_drift_to_match])
            drift_ids_det_left.remove(drift_ids_act[drift_pos])
            for change_inf_act in change_mom_act:
                change_mom_det_to_del.extend(matching(change_inf_act, change_mom_det))
        #elif drift_ids_act[drift_pos] not in drift_ids_det:
        #    Col_act.FN += len(Col_act.extract_change_moments(Col_act.drifts[
        #                                                   drift_pos]))  # if there is no log in the detected drift with the same ID as in the actual drift then increase the FN by the number of drifts in the actual drift
    # FP represent the sum of all reamining change moments in the detected drifts that are not available in the actual drift
    cm_all_det = list()
    for cm in Col_det.drifts:
        cm_all_det.extend(extract_change_moments(cm))
    FP += sum([1 if cm not in change_mom_det_to_del else 0 for cm in cm_all_det])
    return {"TP":TP,"FP":FP}

###### LP Method Functions #####
def extract_change_trace_index(drifts_in_log: list()):  # takes a list of drift instances
    drift_change_index = list()
    for drift_instance in drifts_in_log:  # is a list containing all the drift instances of a single log
        change_id = 1
        for trace_index_info in list(drift_instance.change_info.values()):
            drift_change_index.append((change_id, drift_instance.drift_type, trace_index_info["change_trace_index"]))
            change_id+=1
    return drift_change_index

def list_of_change_indexes (drift_change_index:list[tuple]):
    list_of_change_indexes = list()
    for change_index_info in drift_change_index:
        list_of_change_indexes.extend(change_index_info[2])
    return list_of_change_indexes



def evaluate_lp_method(Col_act,Col_det,lag):

    global TP
    global FP

    drift_ids_act = [DI_act[0].log_id for DI_act in Col_act.drifts]
    drift_ids_det = [DI_det[0].log_id for DI_det in Col_det.drifts]
    drift_ids_det_left = drift_ids_det.copy()
    for drift_pos in range(0,len(Col_act.drifts)):  # Col_act.drifts is a list of drifts each change moment in a log is stored in an instance and each instance belonging to the same log are saved in the same list
        change_index_act = extract_change_trace_index(Col_act.drifts[drift_pos])
        print(change_index_act)

        if drift_ids_act[drift_pos] in drift_ids_det:
            pos_drift_to_match = drift_ids_det.index(drift_ids_act[drift_pos])
            change_index_det = extract_change_trace_index(Col_det.drifts[pos_drift_to_match])
            drift_ids_det_left.remove(drift_ids_act[drift_pos])

            TP += getTP_FP(list_of_change_indexes(change_index_det),list_of_change_indexes(change_index_act),lag)[0]
            FP += getTP_FP(list_of_change_indexes(change_index_det),list_of_change_indexes(change_index_act),lag) [1]
    return {"TP":TP,"FP":FP}











