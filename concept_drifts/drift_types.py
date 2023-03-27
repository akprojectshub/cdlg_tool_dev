from pm4py.objects.log.obj import EventLog
from pm4py.objects.process_tree import semantics
from random import randint
from controllers.event_log_controller import combine_two_logs


def add_recurring_drift(event_log, tree_one, tree_two, nu_traces, number_of_seasonal_changes):

    # TODO: make this parameter controllable by a user through the parameter file
    num_trace_per_sublog = randint(int(nu_traces*0.5), nu_traces)
    #num_trace_per_sublog = int(round(nu_traces / number_of_seasonal_changes, -1))


    log_1 = semantics.generate_log(tree_one, num_trace_per_sublog)
    log_2 = semantics.generate_log(tree_two, num_trace_per_sublog)
    event_log_with_recurring_drift = combine_two_logs(event_log, log_1)

    for i in range(number_of_seasonal_changes):
        if i % 2 == 0:
            event_log_with_recurring_drift = combine_two_logs(event_log_with_recurring_drift, log_2)
        else:
            event_log_with_recurring_drift = combine_two_logs(event_log_with_recurring_drift, log_1)

    return event_log_with_recurring_drift
