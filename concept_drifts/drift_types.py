from pm4py.objects.log.obj import EventLog
from pm4py.objects.process_tree import semantics
from random import randint
from controllers.event_log_controller import combine_two_logs
import copy
from controllers.control_flow_controller import change_tree_on_control_flow_incremental, \
    change_tree_on_control_flow_incremental_random, evolve_tree_randomly
from controllers.input_controller import input_int, input_ra_ch, input_int_hun, input_percentage, input_end
from controllers.event_log_controller import *
from pm4py.objects.process_tree import semantics
from controllers.process_tree_controller import generate_tree, visualise_tree
from pm4py import play_out
from pm4py.algo.simulation.playout.process_tree.variants.topbottom import Parameters
from controllers.control_flow_controller import evolve_tree_randomly
from controllers.utilities import select_random, ChangeTypes


def add_recurring_drift(event_log, drift_instance, par):

    tree_previous = drift_instance.get_previous_process_tree()
    number_of_seasonal_changes = select_random(par.Recurring_drift_number, option='random')
    # TODO: make this parameter controllable by a user through the parameter file
    num_traces = select_random(par.Number_traces_per_process_model_version, option='uniform_int')
    num_trace_per_sublog = randint(int(num_traces*0.5), num_traces)
    #num_trace_per_sublog = int(round(nu_traces / number_of_seasonal_changes, -1))
    ran_evolve = select_random(par.Process_tree_evolution_proportion, option='uniform')
    tree_ev, deleted_acs, added_acs, moved_acs = evolve_tree_randomly(tree_previous, ran_evolve)

    drift_instance.add_process_tree(tree_ev)


    log_2 = play_out(tree_ev, parameters={Parameters.NO_TRACES: num_trace_per_sublog})
    log_1 = play_out(tree_previous, parameters={Parameters.NO_TRACES: num_trace_per_sublog})

    event_log_with_added_recurring_drift = combine_two_logs(event_log, log_2)
    change_trace_index = len(event_log) + 1
    drift_instance.add_change_info(change_trace_index,
                                   ChangeTypes.sudden.value,
                                   tree_previous, tree_ev,
                                   deleted_acs, added_acs, moved_acs)


    for i in range(2, number_of_seasonal_changes + 1):
        if i % 2 == 0:
            event_log_with_recurring_drift = combine_two_logs(event_log_with_added_recurring_drift, log_1)
            change_trace_index = len(event_log_with_added_recurring_drift) + 1
            drift_instance.add_change_info(change_trace_index,
                                           ChangeTypes.sudden.value,
                                           tree_ev, tree_previous,
                                           added_acs, deleted_acs, moved_acs)
        else:
            event_log_with_recurring_drift = combine_two_logs(event_log_with_added_recurring_drift, log_2)
            change_trace_index = len(event_log_with_added_recurring_drift) + 1
            drift_instance.add_change_info(change_trace_index,
                                           ChangeTypes.sudden.value,
                                           tree_previous, tree_ev,
                                           deleted_acs, added_acs, moved_acs)

    return event_log_with_recurring_drift, drift_instance





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
    tree_ev = deepcopy(tree_previous)
    for i in range(1, num_models+1):
        num_traces = select_random(par.Number_traces_per_process_model_version, option='uniform_int')
        ran_evolve = select_random([0.05, 0.2], option='uniform')
        # ran_evolve = select_random(par.Process_tree_evolution_proportion, option='uniform')
        tree_ev, deleted_acs, added_acs, moved_acs = evolve_tree_randomly(tree_ev, ran_evolve)
        log_add = play_out(tree_ev, parameters={Parameters.NO_TRACES: num_traces})
        drift_instance.add_process_tree(tree_ev)
        change_trace_index = len(event_log) + 1
        drift_instance.add_change_info(change_trace_index,
                                       ChangeTypes.sudden.value,
                                       tree_previous, tree_ev,
                                       deleted_acs, added_acs, moved_acs)
        event_log = combine_two_logs(event_log, log_add)

    return event_log, drift_instance


