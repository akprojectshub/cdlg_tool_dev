from src.data_classes.evaluation_LP import getTP_FP
from class_collection import *
from src.data_classes.evaluation_LP import calcPrecisionRecall
import numpy as np

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


def extract_log_ids(Col_act, Col_det):
    log_ids_det_act = {}
    log_ids_det_act["actual logs"] = [DI_act[0].log_id for DI_act in Col_act.drifts]
    log_ids_det_act["detected logs"] = [DI_det[0].log_id for DI_det in Col_det.drifts]
    return log_ids_det_act


def calculate_FP_ts_method(Col_det, change_mom_det_to_del:list):
    global FP

    cm_all_det = list()
    for cm in Col_det.drifts:
        cm_all_det.extend(extract_change_moments(cm))
    FP += sum([1 if cm not in change_mom_det_to_del else 0 for cm in cm_all_det])

    return None



def evaluate_using_timestamps(Col_act, Col_det):

    global TP
    global FP

    log_ids_act = extract_log_ids(Col_act, Col_det)["actual logs"]
    log_ids_det = extract_log_ids(Col_act, Col_det)["detected logs"]
    log_ids_det_left = log_ids_det.copy()
    change_mom_det_to_del = list()
    for drift_pos in range(0,
                           len(Col_act.drifts)):  # Col_act.drifts is a list of drifts each change moment in a log is stored in an instance and each instance belonging to the same log are saved in the same list
        change_mom_act = extract_change_moments(Col_act.drifts[drift_pos])

        if log_ids_act[drift_pos] in log_ids_det:
            pos_drift_to_match = log_ids_det.index(log_ids_act[drift_pos])
            change_mom_det = extract_change_moments(Col_det.drifts[pos_drift_to_match])
            log_ids_det_left.remove(log_ids_act[drift_pos])
            for change_inf_act in change_mom_act:
                change_mom_det_to_del.extend(matching(change_inf_act, change_mom_det))
        #elif drift_ids_act[drift_pos] not in drift_ids_det:
        #    Col_act.FN += len(Col_act.extract_change_moments(Col_act.drifts[
        #                                                   drift_pos]))  # if there is no log in the detected drift with the same ID as in the actual drift then increase the FN by the number of drifts in the actual drift
    # FP represent the sum of all reamining change moments in the detected drifts that are not available in the actual drift
    calculate_FP_ts_method(Col_det, change_mom_det_to_del)
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
    print(drift_change_index)
    for change_index_info in drift_change_index:
        list_of_change_indexes.extend(change_index_info[2])
    return list_of_change_indexes


def filter_list_change_indexes(change_index_infos : list(), drift_type):
    return [ci for ci in change_index_infos if ci[1]==drift_type]





def evaluate_lp_method(Col_act,Col_det,lag):
    TP_FP_dict = dict()
    Precision_Recall = dict()

    log_ids_act = extract_log_ids(Col_act, Col_det)["actual logs"]
    log_ids_det = extract_log_ids(Col_act, Col_det)["detected logs"]
    log_ids_det_left = log_ids_det.copy()
    for drift_pos in range(0,len(Col_act.drifts)):  # Col_act.drifts is a list of drifts each change moment in a log is stored in an instance and each instance belonging to the same log are saved in the same list
        change_index_act = extract_change_trace_index(Col_act.drifts[drift_pos])
        """TP_FP_dict[log_ids_act[drift_pos]] = {"gradual":{"TP":0,"FP":0},
                                           "sudden":{"TP":0, "FP":0},
                                           "incremental":{"TP":0, "FP":0},
                                           "recurring":{"TP":0, "FP":0}}
    
            Precision_Recall[log_ids_act[drift_pos]] = {"gradual":{"Precision":0,"Recall":0},
                                           "sudden":{"Precision":0, "Recall":0},
                                           "incremental":{"Precision":0, "Recall":0},
                                           "recurring":{"Precision":0, "Recall":0}}
        """
        TP_FP_dict[log_ids_act[drift_pos]]={}
        Precision_Recall[log_ids_act[drift_pos]]={}


        if log_ids_act[drift_pos] in log_ids_det:
            pos_drift_to_match = log_ids_det.index(log_ids_act[drift_pos])
            change_index_det = extract_change_trace_index(Col_det.drifts[pos_drift_to_match])
            log_ids_det_left.remove(log_ids_act[drift_pos])
            act_drift_types = list(set([cindex_det[1] for cindex_det in change_index_act ]))
            for drift_type in act_drift_types:
                change_index_det_filtered = filter_list_change_indexes(change_index_det,drift_type)
                change_index_act_filtered = filter_list_change_indexes(change_index_act,drift_type)
                TP_FP_dict[log_ids_act[drift_pos]][drift_type] = {"TP":getTP_FP(list_of_change_indexes(change_index_det_filtered),list_of_change_indexes(change_index_act_filtered),lag)[0],
                                                                  "FP":getTP_FP(list_of_change_indexes(change_index_det_filtered),list_of_change_indexes(change_index_act_filtered),lag)[1]}

                Precision_Recall[log_ids_act[drift_pos]][drift_type] = {"Precision": calcPrecisionRecall(list_of_change_indexes(change_index_det_filtered), list_of_change_indexes(change_index_act_filtered), lag, zero_division=np.NaN,count_duplicate_detections = True)[0],
                                                                        "Recall":calcPrecisionRecall(list_of_change_indexes(change_index_det_filtered), list_of_change_indexes(change_index_act_filtered), lag, zero_division=np.NaN,count_duplicate_detections = True)[1]}
    return (TP_FP_dict, Precision_Recall)



global TP
global FP

def Automated_evaluation (Col_act, Col_det, eval_type): #Eval type returns what type of evaluation is needed (TS or TR)

    if eval_type == "TS":
        return evaluate_using_timestamps(Col_act, Col_det)
    elif eval_type =="TR":
        return evaluate_lp_method(Col_act,Col_det,20) #lag should be in percentage and the difference should be in seconds when taking the diff of timestamps
