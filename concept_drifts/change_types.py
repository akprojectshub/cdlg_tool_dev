
from controllers.event_log_controller import *
from pm4py.objects.process_tree import semantics
from controllers.input_controller import input_percentage, input_int, input_end



def add_sudden_change(log, process_tree, num_traces):
    """ Include an additional sudden drift to an event log
    :param log: initial event log
    :param process_tree: evolved tree version used to generate the next process model version
    :param num_traces: number of traces to added to the intial event log from the new process tree
    :return: event log with added additional sudden drift
    """

    log_two = semantics.generate_log(process_tree, num_traces)
    log_extended = combine_two_logs(log, log_two)

    return log_extended