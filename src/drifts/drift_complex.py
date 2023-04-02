from controllers.event_log_controller import *
from pm4py.objects.process_tree import semantics
from controllers.control_flow_controller import evolve_tree_randomly
from src.utilities import select_random, ChangeTypes
from src.drifts.change_type import combine_two_logs_with_certain_change_type
from src.drifts.drift_simple import combine_two_logs
import src.input_parameters as config

def add_recurring_drift(event_log, drift_instance, par):

    tree_previous = drift_instance.get_previous_process_tree()
    ran_evolve = select_random(par.Process_tree_evolution_proportion, option='uniform')
    tree_new, deleted_acs, added_acs, moved_acs = evolve_tree_randomly(tree_previous, ran_evolve)
    axillary_order_1 = [tree_previous, tree_new, deleted_acs, added_acs, moved_acs]
    axillary_order_2 = [tree_new, tree_previous, added_acs, deleted_acs, moved_acs]

    number_of_seasonal_changes = select_random(par.Recurring_drift_number, option='random')
    for i in range(0, number_of_seasonal_changes):
        if i % 2 == 0:
            event_log, drift_instance = combine_two_logs_with_certain_change_type(event_log, drift_instance, par,
                                                                                  axillary_order_1)
        else:
            event_log, drift_instance = combine_two_logs_with_certain_change_type(event_log, drift_instance, par,
                                                                                  axillary_order_2)

    return event_log, drift_instance





def add_incremental_drift(event_log, drift_instance, par):

    num_models = select_random(par.Incremental_drift_number, option='random')
    for i in range(1, num_models+1):
        event_log, drift_instance = combine_two_logs_with_certain_change_type(event_log, drift_instance, par)

    return event_log, drift_instance


