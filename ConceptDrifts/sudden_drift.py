from Source.event_log_controller import *
from pm4py.objects.process_tree import semantics
from Source.input_controller import input_percentage, input_int, input_end


def sudden_drift(tree_one, tree_two, nu_traces, change_point):
    """ Generation of an event log with a sudden drift

    :param tree_one: the initial version of the process model
    :param tree_two: the evolved version of the process model
    :param nu_traces: number traces in event log
    :param change_point: change point of the drift
    :return: event log with sudden drift
    """
    log_one_traces = int(round(nu_traces * change_point))
    log_two_traces = nu_traces - log_one_traces
    log_one = semantics.generate_log(tree_one, log_one_traces)
    log_two = semantics.generate_log(tree_two, log_two_traces)
    logs_combined = combine_two_logs(log_one, log_two)
    return logs_combined


def additional_sudden_drift_in_log(log, tree_two):
    """ Including an additional sudden drift into an event log

    :param log: event log including a drift
    :param tree_two: evolved tree version
    :return:  event log with an additional sudden drift
    """
    add_end = input_end("Adding the additional recurring drift at the end of the log or into the log [end, into]? ")
    if add_end == 'into':
        drift_time = input_percentage("Starting point of the drift (0 < x < 1): ")
        log_two_traces = (length_of_log(log) - int(round(length_of_log(log) * drift_time + 0.0001)))
        log_two = semantics.generate_log(tree_two, log_two_traces)
        result_log = replace_traces_of_log(log, log_two, drift_time)
        return result_log
    else:
        nu_add_traces = input_int(
            "Number of additional traces from the new model to be added at the end of the event log (int): ")
        log_two = semantics.generate_log(tree_two, nu_add_traces)
        return combine_two_logs(log, log_two)
