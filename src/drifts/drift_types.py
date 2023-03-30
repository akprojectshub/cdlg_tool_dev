from controllers.event_log_controller import *
from pm4py.objects.process_tree import semantics
from controllers.control_flow_controller import evolve_tree_randomly
from src.utilities import select_random, ChangeTypes


def add_recurring_drift(event_log, drift_instance, par):

    tree_previous = drift_instance.get_previous_process_tree()
    ran_evolve = select_random(par.Process_tree_evolution_proportion, option='uniform')
    tree_ev, deleted_acs, added_acs, moved_acs = evolve_tree_randomly(tree_previous, ran_evolve)
    drift_instance.add_process_tree(tree_ev)

    number_of_seasonal_changes = select_random(par.Recurring_drift_number, option='random')
    for i in range(1, number_of_seasonal_changes + 1):
        if i % 2 == 0:
            change_trace_index = len(event_log) + 1
            drift_instance.add_change_info(change_trace_index,
                                           ChangeTypes.sudden.value,
                                           tree_ev, tree_previous,
                                           added_acs, deleted_acs, moved_acs)
            num_traces = select_random(par.Number_traces_per_process_model_version, option='uniform_int')
            log_1 = semantics.generate_log(tree_previous, num_traces)
            event_log = combine_two_logs(event_log, log_1)
        else:
            change_trace_index = len(event_log) + 1
            drift_instance.add_change_info(change_trace_index,
                                           ChangeTypes.sudden.value,
                                           tree_previous, tree_ev,
                                           deleted_acs, added_acs, moved_acs)
            num_traces = select_random(par.Number_traces_per_process_model_version, option='uniform_int')
            log_2 = semantics.generate_log(tree_ev, num_traces)
            event_log = combine_two_logs(event_log, log_2)

    return event_log, drift_instance





def add_incremental_drift(event_log, drift_instance, par):
    """ Generation of an event log with an incremental drift for gold standard generation

    :param ran_in_evolve: proportion of the process model version to be evolved
    :param process_tree: initial model
    :param start_point: starting point for the incremental drift
    :param end_point: ending point for the incremental drift
    :param nu_traces: number traces in event log
    :param number_incremental_changes: number of intermediate models
    :return: event log with incremental drift
    """
    tree_previous = drift_instance.get_previous_process_tree()
    num_models = select_random(par.Incremental_drift_number, option='random')
    for i in range(1, num_models+1):
        num_traces = select_random(par.Number_traces_per_process_model_version, option='uniform_int')
        ran_evolve = select_random([0.05, 0.2], option='uniform')
        # ran_evolve = select_random(par.Process_tree_evolution_proportion, option='uniform')
        tree_ev, deleted_acs, added_acs, moved_acs = evolve_tree_randomly(tree_previous, ran_evolve)
        drift_instance.add_process_tree(tree_ev)
        change_trace_index = len(event_log) + 1
        drift_instance.add_change_info(change_trace_index,
                                       ChangeTypes.sudden.value,
                                       tree_previous, tree_ev,
                                       deleted_acs, added_acs, moved_acs)
        log_add = semantics.generate_log(tree_ev, num_traces)
        event_log = combine_two_logs(event_log, log_add)
        tree_previous = deepcopy(tree_ev)

    return event_log, drift_instance


