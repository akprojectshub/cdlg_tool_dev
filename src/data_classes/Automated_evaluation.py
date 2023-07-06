from src.data_classes.evaluation_LP import getTP_FP
from class_collection import *
from src.data_classes.evaluation_LP import calcPrecisionRecall,F1_Score
import numpy as np
import csv




#TODO: pull again the latest version (join the main branch with my transporter to update the transporter with the main)
#TODO: ADD Aknowledgment part


#TODO: NAMING ALWAYS IN LOWER CASES
#TODO: REmove the examples
#TODO: provide documentation for everything in datacalss file, drifts, and input_parameters (noise_controllers_new, utilities) ---> found in a screenshot that he sent me
#TODO: generate collection of logs should also be documented
#TODO: move file with parameters names to the utilities file that alexander created
#TODO: change drift type also randomly in the automated evaluation in the testing file
#TODO: add if statement in the testing (if main ... )
#TODO: resturcuture the testing so that the testing is a single block
#TODO: Add more modification when testing(hear again minute 36)
#TODO: add testing for the lag (hear minute 41)
#TODO: add the accuracy (hear again minute 45)

#TODO: testing that our tool works for generating collection of logs for different parameters. Our tool should work for all input parameters that can be providied when generating logs

#### FOCUS ON THE PREVIOUS POINTS FOR NOW
#TODO: write a readme file (This is more tehcnical)
#TODO: write a word documentation file (look at the repository link he sent me on slack )
#TODO: he wants to write an aggregated method





#TODO: NAMING ALWAYS IN LOWER CASES


def extract_log_ids(col_act, col_det):
    """Returns a dictionary containing the log ids of the actual and detected collection of logs stored in separate lists
           Args:
               col_act(List[DriftInfo]): A list storing all the actual drift instances
               col_det(List[DriftInfo]): A list storing all the detected drift instances

           Returns:
               Dict[str,List[str]]: two lists storing the log ids of the actual and detected collection of logs


           Examples:
               >>> expected_log_ids([DriftInfo(log_id='log_1_1687271372.xes', drift_id='drift_1', process_perspective='control-flow', drift_type='gradual', process_trees=defaultdict(<class 'dict'>, {'0': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ), 'Random activity 1' )"}), change_info=defaultdict(<class 'dict'>, {'1': {'change_type': 'gradual', 'change_trace_index': [2091, 2977], 'process_tree_before': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ) )", 'process_tree_after': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ), 'Random activity 1' )", 'activities_deleted': '[]', 'activities_added': '[Random activity 1]', 'activities_moved': '[]', 'change_start': datetime.datetime(2022, 8, 16, 19, 23, 34, 675168), 'change_end': datetime.datetime(2023, 10, 18, 22, 5, 57, 264767)}})), DriftInfo(log_id='log_1_1687271372.xes', drift_id='drift_2', process_perspective='control-flow', drift_type='sudden', process_trees=defaultdict(<class 'dict'>, {'0': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ), 'Random activity 2' )"}), change_info=defaultdict(<class 'dict'>, {'1': {'change_type': 'sudden', 'change_trace_index': [5685], 'process_tree_before': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ) )", 'process_tree_after': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ), 'Random activity 2' )", 'activities_deleted': '[]', 'activities_added': '[Random activity 1, Random activity 2]', 'activities_moved': '[]', 'change_start': datetime.datetime(2027, 2, 3, 23, 40, 2, 11904), 'change_end': datetime.datetime(2027, 2, 3, 23, 40, 2, 11904)}})), DriftInfo(log_id='log_1_1687271372.xes', drift_id='drift_3', process_perspective='control-flow', drift_type='sudden', process_trees=defaultdict(<class 'dict'>, {'0': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ) )"}), change_info=defaultdict(<class 'dict'>, {'1': {'change_type': 'sudden', 'change_trace_index': [7086], 'process_tree_before': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ) )", 'process_tree_after': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ) )", 'activities_deleted': '[]', 'activities_added': '[Random activity 1]', 'activities_moved': '[]', 'change_start': datetime.datetime(2028, 10, 21, 5, 18, 56, 285320), 'change_end': datetime.datetime(2028, 10, 21, 5, 18, 56, 285320)}}))],
               >>>[DriftInfo(log_id='log_1_1687271372.xes', drift_id='drift_1', process_perspective='control-flow', drift_type='gradual', process_trees=defaultdict(<class 'dict'>, {'0': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ), 'Random activity 1' )"}), change_info=defaultdict(<class 'dict'>, {'1': {'change_type': 'gradual', 'change_trace_index': [2091, 2977], 'process_tree_before': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ) )", 'process_tree_after': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ), 'Random activity 1' )", 'activities_deleted': '[]', 'activities_added': '[Random activity 1]', 'activities_moved': '[]', 'change_start': datetime.datetime(2022, 8, 16, 19, 23, 34, 675168), 'change_end': datetime.datetime(2023, 10, 18, 22, 5, 57, 264767)}})), DriftInfo(log_id='log_1_1687271372.xes', drift_id='drift_2', process_perspective='control-flow', drift_type='sudden', process_trees=defaultdict(<class 'dict'>, {'0': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ), 'Random activity 2' )"}), change_info=defaultdict(<class 'dict'>, {'1': {'change_type': 'sudden', 'change_trace_index': [5685], 'process_tree_before': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ) )", 'process_tree_after': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ), 'Random activity 2' )", 'activities_deleted': '[]', 'activities_added': '[Random activity 1, Random activity 2]', 'activities_moved': '[]', 'change_start': datetime.datetime(2027, 2, 3, 23, 40, 2, 11904), 'change_end': datetime.datetime(2027, 2, 3, 23, 40, 2, 11904)}})), DriftInfo(log_id='log_1_1687271372.xes', drift_id='drift_3', process_perspective='control-flow', drift_type='sudden', process_trees=defaultdict(<class 'dict'>, {'0': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ) )"}), change_info=defaultdict(<class 'dict'>, {'1': {'change_type': 'sudden', 'change_trace_index': [7086], 'process_tree_before': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ) )", 'process_tree_after': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ) )", 'activities_deleted': '[]', 'activities_added': '[Random activity 1]', 'activities_moved': '[]', 'change_start': datetime.datetime(2028, 10, 21, 5, 18, 56, 285320), 'change_end': datetime.datetime(2028, 10, 21, 5, 18, 56, 285320)}}))])

               >>> {'actual logs': ['log_1_1687271372.xes', 'log_2_1687271374.xes'], 'detected logs': ['log_1_1687271372.xes', 'log_2_1687271374.xes']}
           """

    log_ids_det_act = {}
    log_ids_det_act["actual logs"] = [DI_act[0].log_id for DI_act in col_act.drifts]
    log_ids_det_act["detected logs"] = [DI_det[0].log_id for DI_det in col_det.drifts]
    return log_ids_det_act

def extract_change_trace_index(drifts_in_log: list()):  # takes a list of drift instances
    """Returns a list of tuples storing information about all the drift changepoints in a single log

    Args:
        drifts_in_log (List[DriftInfo]): list of drift instances in a log
    Returns:
        List[Tuple[int,str,List[int]]]: List of tuples, each tuple contains the id, drift type, and the change trace indexes for each changepoint
        in the log
    Examples:
        >>> extract_change_trace_index([DriftInfo(log_id='log_1_1687271372.xes', drift_id='drift_1', process_perspective='control-flow', drift_type='gradual', process_trees=defaultdict(<class 'dict'>, {'0': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ), 'Random activity 1' )"}), change_info=defaultdict(<class 'dict'>, {'1': {'change_type': 'gradual', 'change_trace_index': [2091, 2977], 'process_tree_before': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ) )", 'process_tree_after': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ), 'Random activity 1' )", 'activities_deleted': '[]', 'activities_added': '[Random activity 1]', 'activities_moved': '[]', 'change_start': datetime.datetime(2022, 8, 16, 19, 23, 34, 675168), 'change_end': datetime.datetime(2023, 10, 18, 22, 5, 57, 264767)}})), DriftInfo(log_id='log_1_1687271372.xes', drift_id='drift_2', process_perspective='control-flow', drift_type='sudden', process_trees=defaultdict(<class 'dict'>, {'0': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ), 'Random activity 2' )"}), change_info=defaultdict(<class 'dict'>, {'1': {'change_type': 'sudden', 'change_trace_index': [5685], 'process_tree_before': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ) )", 'process_tree_after': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ), 'Random activity 2' )", 'activities_deleted': '[]', 'activities_added': '[Random activity 1, Random activity 2]', 'activities_moved': '[]', 'change_start': datetime.datetime(2027, 2, 3, 23, 40, 2, 11904), 'change_end': datetime.datetime(2027, 2, 3, 23, 40, 2, 11904)}})), DriftInfo(log_id='log_1_1687271372.xes', drift_id='drift_3', process_perspective='control-flow', drift_type='sudden', process_trees=defaultdict(<class 'dict'>, {'0': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ) )"}), change_info=defaultdict(<class 'dict'>, {'1': {'change_type': 'sudden', 'change_trace_index': [7086], 'process_tree_before': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ) )", 'process_tree_after': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ) )", 'activities_deleted': '[]', 'activities_added': '[Random activity 1]', 'activities_moved': '[]', 'change_start': datetime.datetime(2028, 10, 21, 5, 18, 56, 285320), 'change_end': datetime.datetime(2028, 10, 21, 5, 18, 56, 285320)}}))])
        >>> [(1, 'recurring', [2832]), (2, 'recurring', [4390, 5206]), (3, 'recurring', [7064]), (1, 'gradual', [8469, 9116])]
    """
    drift_change_index = list()
    for drift_instance in drifts_in_log:  # is a list containing all the drift instances of a single log
        change_id = 1
        for trace_index_info in list(drift_instance.change_info.values()):
            drift_change_index.append((change_id, drift_instance.drift_type, trace_index_info["change_trace_index"]))
            change_id+=1
    return drift_change_index




def list_of_change_indexes (drift_change_index:list[tuple]):
    """Returns a list containing all the change trace indexes of a log
    Args:
        drift_change_index (List[Tuple[int,str,List[int]]]): List of tuples, each tuple contains the id, drift type, and the change trace indexes for each changepoint
        in the log
    Returns:
        List[int]: List of change trace indexes

    Examples:
        >>> [(1, 'recurring', [2832]), (2, 'recurring', [4390, 5206]), (3, 'recurring', [7064]), (1, 'gradual', [8469, 9116])]
        >>> [2832, 4390, 5206, 7064]
    """

    list_of_change_indexes = list()
    for change_index_info in drift_change_index:
        list_of_change_indexes.extend(change_index_info[2])
    return list_of_change_indexes


def filter_list_change_indexes(change_index_infos : list(), drift_type:str):
    """Returns a list containing all the change moments that match a specific drift type
    Args:
        drift_change_index_infos (List[Tuple[int,str,List[int]]]): List of tuples, each tuple contains the id, drift type, and the change trace indexes for each change moment
        in the log
        drift_type (str): The drift_type that will be used to filter the drift_change_index_infos list
    Returns:
        List[int]: List of change trace indexes sharing the same drift type

    Examples:
        >>> change_index_det [(1, 'gradual', [2091, 2977]), (1, 'sudden', [5685]), (1, 'sudden', [7086])]
        >>> change_index_det_filtered [(1, 'gradual', [2091, 2977])]
    """
    return [ci for ci in change_index_infos if ci[1]==drift_type]


def fill_data_frame_row(df,dict_val):
    df.loc[len(df)] = list(dict_val.values())
    return None

def fill_evaluation_row_dic(log_name,drift_type,detected_cp,actual_cp,lag,TP,FP,FN_TP,precision,recall,f1_score):
    evaluation_row = {#'collection_name': collection_name,
                      'log_name': log_name,
                      'drift_type':drift_type,
                      #'noise_level': noise_level,
                      #'complexity': complexity,
                      #'method': option,
                      #'window_size': 'na',
                      'detected_cp': detected_cp,
                      'actual_cp': actual_cp,
                      #'log_size': len(event_log),
                      'lag': lag,
                      #'lag_indices': lag_indices,
                      'TP': TP,
                      'FP': FP,
                      'FN_TP': FN_TP,
                      'Precision': precision,
                      'Recall': recall,
                      'F1_score': f1_score}
    return evaluation_row


def create_evaluation_report_file():
    columns = [#'collection_name',
               'log_name',
               'drift_type',
               #'noise_level',
               #'complexity',
               #'method',
               #'window_size',
               'detected_cp',
               'actual_cp',
               'lag',
               #'lag_indices',
               'TP',
               'FP',
               'FN_TP',
               'Precision',
               'Recall',
               'F1_score']
    report = pd.DataFrame(columns=columns)

    return report


def get_precision(TP, FP):
    """Returns the precision
    Args:
       TP(int): True positive value
       FP(int): False positive value
    Returns:
        Float: Return the precision or np.nan if division by 0

    Examples:
        >>> get_precision(2,0)
        >>> 1.0
    """

    precision = np.where((TP + FP) > 0, np.divide(TP, TP + FP), np.nan)
    return precision

def get_recall(TP, FN_TP):
    """Returns the recall
    Args:
       TP(int): True positive value
       FN_TP(int): False negative value
    Returns:
        Float: Return the recall or np.nan if division by 0

    Examples:
        >>> get_recall(4,0)
        >>> 1.0
    """
    recall = np.where(FN_TP > 0, np.divide(TP , FN_TP), np.nan)
    return recall

def get_f1_score(precision, recall):

    """Returns the F1 score
    Args:
       precision(float): Precision
       recall(float): Recall
    Returns:
        Float: Return the f1 score or np.nan if division by 0

    Examples:
        >>> get_recall(1.0,1.0)
        >>> 1.0
    """

    try:
        f1_score = (2*precision*recall)/(precision+recall)
        return f1_score
    except ZeroDivisionError:
        print("Calculation of F1-Score resulted in division by 0.")
        f1_score = np.NaN

    return str(f1_score)

def get_total_evaluation_results(evaluation_report: pd.DataFrame):

    """Returns an aggregated version of the evaluation report
    Args:
       pd.DataFrame: A dataframe storing the log_name, drift_type, detected_cp,actual_cp,lag,TP,FP,FN_TP,Precision,Recall,F1_score

    Returns:
        pd.DataFrame: An aggregate version of the input dataframe with rows grouped by lag value and the drift_type
    """

    aggregations = {
        'TP': 'sum',
        'FP': 'sum',
        'FN_TP': 'sum'}
    grouping = ['lag', 'drift_type']
    evaluation_report_agg = evaluation_report.groupby(grouping).agg(aggregations)
    evaluation_report_agg = evaluation_report_agg.assign(Precision=lambda x: get_precision(x['TP'], x['FP']))
    evaluation_report_agg = evaluation_report_agg.assign(Recall=lambda x: get_recall(x['TP'], x['FN_TP']))
    evaluation_report_agg = evaluation_report_agg.assign(F1_score=lambda x: get_f1_score(x['Precision'], x['Recall']))

    return evaluation_report_agg



def evaluate_lp_method(col_act,col_det,lag):
    """Returns data (TP,FP,FN,Precision,Recall, and F1 score) resulting of the matching process between the two collection of logs provided
    Args:
        col_act(List[DriftInfo]): A list storing all the actual drift instances
        col_det(List[DriftInfo]): A list storing all the detected drift instances
        lag (int): The maximal distance a detected change point can have to an actual change point, whilst still counting as a true positive.
        TODO: Should be changed later when we specify how the lag will be defined for now it's an int
    Returns:
        Tuple[Dict[str,Dict[str,int]],Dict[str,float]]: A tuple storing two dictionaries. The first dictionary stores the TP, FP and FN for each log id and for each drift type.
                                                        The second dictionary stores the precision, recall and f1score for each drift type.
        DataFrame[log_name,drift_type,detected_cp,actual_cp,lag,TP, FP, precision, recall, and F1]: A data frame storing the metrics resulting from the matching process between two collection of logs


    Examples:
        >>> evaluate_lp_method([DriftInfo(log_id='log_1_1687271372.xes', drift_id='drift_1', process_perspective='control-flow', drift_type='gradual', process_trees=defaultdict(<class 'dict'>, {'0': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ), 'Random activity 1' )"}), change_info=defaultdict(<class 'dict'>, {'1': {'change_type': 'gradual', 'change_trace_index': [2091, 2977], 'process_tree_before': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ) )", 'process_tree_after': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ), 'Random activity 1' )", 'activities_deleted': '[]', 'activities_added': '[Random activity 1]', 'activities_moved': '[]', 'change_start': datetime.datetime(2022, 8, 16, 19, 23, 34, 675168), 'change_end': datetime.datetime(2023, 10, 18, 22, 5, 57, 264767)}})), DriftInfo(log_id='log_1_1687271372.xes', drift_id='drift_2', process_perspective='control-flow', drift_type='sudden', process_trees=defaultdict(<class 'dict'>, {'0': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ), 'Random activity 2' )"}), change_info=defaultdict(<class 'dict'>, {'1': {'change_type': 'sudden', 'change_trace_index': [5685], 'process_tree_before': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ) )", 'process_tree_after': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ), 'Random activity 2' )", 'activities_deleted': '[]', 'activities_added': '[Random activity 1, Random activity 2]', 'activities_moved': '[]', 'change_start': datetime.datetime(2027, 2, 3, 23, 40, 2, 11904), 'change_end': datetime.datetime(2027, 2, 3, 23, 40, 2, 11904)}})), DriftInfo(log_id='log_1_1687271372.xes', drift_id='drift_3', process_perspective='control-flow', drift_type='sudden', process_trees=defaultdict(<class 'dict'>, {'0': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ) )"}), change_info=defaultdict(<class 'dict'>, {'1': {'change_type': 'sudden', 'change_trace_index': [7086], 'process_tree_before': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ) )", 'process_tree_after': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ) )", 'activities_deleted': '[]', 'activities_added': '[Random activity 1]', 'activities_moved': '[]', 'change_start': datetime.datetime(2028, 10, 21, 5, 18, 56, 285320), 'change_end': datetime.datetime(2028, 10, 21, 5, 18, 56, 285320)}}))],
        >>> [DriftInfo(log_id='log_1_1687271372.xes', drift_id='drift_1', process_perspective='control-flow', drift_type='gradual', process_trees=defaultdict(<class 'dict'>, {'0': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ), 'Random activity 1' )"}), change_info=defaultdict(<class 'dict'>, {'1': {'change_type': 'gradual', 'change_trace_index': [2091, 2977], 'process_tree_before': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ) )", 'process_tree_after': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ), 'Random activity 1' )", 'activities_deleted': '[]', 'activities_added': '[Random activity 1]', 'activities_moved': '[]', 'change_start': datetime.datetime(2022, 8, 16, 19, 23, 34, 675168), 'change_end': datetime.datetime(2023, 10, 18, 22, 5, 57, 264767)}})), DriftInfo(log_id='log_1_1687271372.xes', drift_id='drift_2', process_perspective='control-flow', drift_type='sudden', process_trees=defaultdict(<class 'dict'>, {'0': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ), 'Random activity 2' )"}), change_info=defaultdict(<class 'dict'>, {'1': {'change_type': 'sudden', 'change_trace_index': [5685], 'process_tree_before': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ) )", 'process_tree_after': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ), 'Random activity 2' )", 'activities_deleted': '[]', 'activities_added': '[Random activity 1, Random activity 2]', 'activities_moved': '[]', 'change_start': datetime.datetime(2027, 2, 3, 23, 40, 2, 11904), 'change_end': datetime.datetime(2027, 2, 3, 23, 40, 2, 11904)}})), DriftInfo(log_id='log_1_1687271372.xes', drift_id='drift_3', process_perspective='control-flow', drift_type='sudden', process_trees=defaultdict(<class 'dict'>, {'0': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ) )"}), change_info=defaultdict(<class 'dict'>, {'1': {'change_type': 'sudden', 'change_trace_index': [7086], 'process_tree_before': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e' ) ), 'c' ) )", 'process_tree_after': "->( 'a', X( ->( 'b', ->( ->( 'd', 'f' ), 'e', 'Random activity 1' ) ), 'c' ) )", 'activities_deleted': '[]', 'activities_added': '[Random activity 1]', 'activities_moved': '[]', 'change_start': datetime.datetime(2028, 10, 21, 5, 18, 56, 285320), 'change_end': datetime.datetime(2028, 10, 21, 5, 18, 56, 285320)}}))],
        >>> 100)

        >>> ({'log_1_1687271372.xes': {'sudden': {'TP': 2, 'FP': 0, 'TP_FP': 2}, 'gradual': {'TP': 2, 'FP': 0, 'TP_FP': 1}}, 'log_2_1687271374.xes': {'recurring': {'TP': 4, 'FP': 0, 'TP_FP': 3}, 'gradual': {'TP': 2, 'FP': 0, 'TP_FP': 1}}}, {'log_1_1687271372.xes': {'sudden': {'Precision': 1.0, 'Recall': 1.0, 'F1 score': 1.0}, 'gradual': {'Precision': 1.0, 'Recall': 1.0, 'F1 score': 1.0}}, 'log_2_1687271374.xes': {'recurring': {'Precision': 1.0, 'Recall': 1.0, 'F1 score': 1.0}, 'gradual': {'Precision': 1.0, 'Recall': 1.0, 'F1 score': 1.0}}})

    """

    evaluation_report = create_evaluation_report_file()
    TP_FP_dict = dict()
    Precision_Recall_f1score = dict()

    log_ids_act = extract_log_ids(col_act, col_det)["actual logs"]
    log_ids_det = extract_log_ids(col_act, col_det)["detected logs"]
    log_ids_det_left = log_ids_det.copy()
    for drift_pos in range(0,len(col_act.drifts)):  # col_act.drifts is a list of drifts each change moment in a log is stored in an instance and each instance belonging to the same log are saved in the same list
        change_index_act = extract_change_trace_index(col_act.drifts[drift_pos])
        TP_FP_dict[log_ids_act[drift_pos]]={}
        Precision_Recall_f1score[log_ids_act[drift_pos]]={}

        if log_ids_act[drift_pos] in log_ids_det:
            pos_drift_to_match = log_ids_det.index(log_ids_act[drift_pos])
            change_index_det = extract_change_trace_index(col_det.drifts[pos_drift_to_match])
            log_ids_det_left.remove(log_ids_act[drift_pos])
            act_drift_types = list(set([cindex_det[1] for cindex_det in change_index_act ]))
            for drift_type in act_drift_types:
                print(drift_type)
                change_index_det_filtered = filter_list_change_indexes(change_index_det,drift_type)
                print("change_index_det_filtered",change_index_det_filtered)
                change_index_act_filtered = filter_list_change_indexes(change_index_act,drift_type)
                print("change_index_act_filtered",change_index_act_filtered)

                TP_FP_dict[log_ids_act[drift_pos]][drift_type] = {"TP":getTP_FP(list_of_change_indexes(change_index_det_filtered),list_of_change_indexes(change_index_act_filtered),lag)[0],
                                                                  "FP":getTP_FP(list_of_change_indexes(change_index_det_filtered),list_of_change_indexes(change_index_act_filtered),lag)[1],
                                                                  "TP_FP":len(list_of_change_indexes(change_index_det_filtered))}
                Precision_Recall_f1score[log_ids_act[drift_pos]][drift_type] = {"Precision": calcPrecisionRecall(list_of_change_indexes(change_index_det_filtered), list_of_change_indexes(change_index_act_filtered), lag, zero_division=np.NaN,count_duplicate_detections = True)[0],
                                                                                "Recall":calcPrecisionRecall(list_of_change_indexes(change_index_det_filtered), list_of_change_indexes(change_index_act_filtered), lag, zero_division=np.NaN,count_duplicate_detections = True)[1],
                                                                                "F1 score":F1_Score(list_of_change_indexes(change_index_det_filtered), list_of_change_indexes(change_index_act_filtered), lag, zero_division=np.NaN)}

                evaluation_row = fill_evaluation_row_dic(col_act.drifts[drift_pos][0].log_id,
                                                             drift_type,
                                                             list_of_change_indexes(change_index_det_filtered),
                                                             list_of_change_indexes(change_index_act_filtered),
                                                             lag,
                                                             TP_FP_dict[log_ids_act[drift_pos]][drift_type]["TP"],
                                                             TP_FP_dict[log_ids_act[drift_pos]][drift_type]["FP"],
                                                             len(list_of_change_indexes(change_index_det_filtered)),
                                                             Precision_Recall_f1score[log_ids_act[drift_pos]][drift_type]["Precision"],
                                                             Precision_Recall_f1score[log_ids_act[drift_pos]][drift_type]["Recall"],
                                                             Precision_Recall_f1score[log_ids_act[drift_pos]][drift_type]["F1 score"])



                fill_data_frame_row(evaluation_report,evaluation_row)


    evaluation_report.to_csv(output_path+"/evaluation_report.csv",sep = ";")
    evaluation_report_agg = get_total_evaluation_results(evaluation_report)
    evaluation_report_agg.to_csv(output_path+"/evaluation_report_agg.csv",sep = ",")

    return (TP_FP_dict, Precision_Recall_f1score)



def Automated_evaluation (col_act, col_det, lag): #Eval type returns what type of evaluation is needed (TS or TR)
    global TP
    global FP
    global output_path
    output_path = "C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/Evaluation reports"
    # TODO: have a fixed path for the storage of evaluation report (output_path)
    TP = 0
    FP = 0
    return evaluate_lp_method(col_act,col_det,lag) #lag should be in percentage and the difference should be in seconds when taking the diff of timestamps

