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
from controllers.utilities import select_random


def add_recurring_drift(event_log, tree_previous, par):


    number_of_seasonal_changes = select_random(par.Recurring_drift_number, option='random')
    # TODO: make this parameter controllable by a user through the parameter file
    num_traces = select_random(par.Number_traces_per_process_model_version, option='uniform_int')
    num_trace_per_sublog = randint(int(num_traces*0.5), num_traces)
    #num_trace_per_sublog = int(round(nu_traces / number_of_seasonal_changes, -1))
    ran_evolve = select_random(par.Process_tree_evolution_proportion, option='uniform')
    tree_ev, deleted_acs, added_acs, moved_acs = evolve_tree_randomly(tree_previous, ran_evolve)
    log_2 = play_out(tree_ev, parameters={Parameters.NO_TRACES: num_trace_per_sublog})
    log_1 = play_out(tree_previous, parameters={Parameters.NO_TRACES: num_trace_per_sublog})

    event_log_with_added_recurring_drift = combine_two_logs(event_log, log_2)

    for i in range(2, number_of_seasonal_changes + 1):
        if i % 2 == 0:
            event_log_with_recurring_drift = combine_two_logs(event_log_with_added_recurring_drift, log_2)
        else:
            event_log_with_recurring_drift = combine_two_logs(event_log_with_added_recurring_drift, log_1)


    # log_1 = semantics.generate_log(tree_one, num_trace_per_sublog)
    # log_2 = semantics.generate_log(tree_two, num_trace_per_sublog)
    # event_log_with_recurring_drift = combine_two_logs(event_log, log_1)
    #
    # for i in range(number_of_seasonal_changes):
    #     if i % 2 == 0:
    #         event_log_with_recurring_drift = combine_two_logs(event_log_with_recurring_drift, log_2)
    #     else:
    #         event_log_with_recurring_drift = combine_two_logs(event_log_with_recurring_drift, log_1)

    return event_log_with_recurring_drift, deleted_acs, added_acs, moved_acs, tree_ev





def add_incremental_drift(event_log, tree_previous, par):
    """ Generation of an event log with an incremental drift for gold standard generation

    :param ran_in_evolve: proportion of the process model version to be evolved
    :param process_tree: initial model
    :param start_point: starting point for the incremental drift
    :param end_point: ending point for the incremental drift
    :param nu_traces: number traces in event log
    :param number_incremental_changes: number of intermediate models
    :return: event log with incremental drift
    """

    num_models = select_random(par.Incremental_drift_number, option='random')
    ran_evolve = select_random(par.Process_tree_evolution_proportion, option='uniform')
    tree_ev, deleted_acs, added_acs, moved_acs = evolve_tree_randomly(tree_previous, ran_evolve)
    num_traces = select_random(par.Number_traces_per_process_model_version, option='uniform_int')

    deleted_acs = []
    added_acs = []
    moved_acs = []
    trees = []
    for i in range(1, num_models+1):
        tree_ev, deleted_ac, added_ac, moved_ac = evolve_tree_randomly(tree_ev, ran_evolve)
        deleted_acs.extend(deleted_ac)
        added_acs.extend(added_ac)
        moved_acs.extend(moved_ac)
        trees.append(tree_ev)
        log_add = play_out(tree_ev, parameters={Parameters.NO_TRACES: num_traces})
        # Justus' implementation
        #log_add = semantics.generate_log(tree_ev, nu_traces)
        event_log_ext = combine_two_logs(event_log, log_add)

    return event_log_ext, deleted_acs, added_acs, moved_acs, trees