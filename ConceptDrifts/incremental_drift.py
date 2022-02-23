import copy
import os

from Source.control_flow_controller import change_tree_on_control_flow_incremental, \
    change_tree_on_control_flow_incremental_random, evolve_tree_randomly, evolve_tree_randomly_gs
from Source.input_controller import input_int, input_ra_ch, input_int_hun, input_percentage, input_end
from Source.event_log_controller import *
from pm4py.objects.process_tree import semantics
from Source.process_tree_controller import generate_tree
from pm4py.objects.process_tree.exporter import exporter as ptml_exporter


def incremental_drift_doc(tree_one, nu_traces_initial, nu_traces_int, nu_traces_evl, nu_models,
                          proportion_random_evolution):
    """ Generation of an event log with an incremental drift from the parameters saved in the textfile 'parameters_incremental_drift'

    :param proportion_random_evolution: proportion of the process model version to be evolved
    :param tree_one: initial model
    :param nu_traces_initial: number traces for the initial model
    :param nu_traces_int: number traces for the evolutionary models
    :param nu_traces_evl: number traces for the final model
    :param nu_models: number of intermediate models
    :return: event log with incremental drift
    """
    result = semantics.generate_log(tree_one, nu_traces_initial)
    i = 0
    trees = [tree_one]
    deleted_acs = []
    added_acs = []
    moved_acs = []
    while i < nu_models:
        drift_tree = copy.deepcopy(trees[i])
        tree_ev, deleted_ac, added_ac, moved_ac = evolve_tree_randomly_gs(drift_tree, proportion_random_evolution)
        deleted_acs.extend(deleted_ac)
        added_acs.extend(added_ac)
        moved_acs.extend(moved_ac)
        trees.append(tree_ev)
        log = semantics.generate_log(trees[i + 1], nu_traces_int)
        result = combine_two_logs(result, log)
        i = i + 1
    drift_tree = copy.deepcopy(trees[len(trees) - 1])
    tree_two, deleted_ac, added_ac, moved_ac = evolve_tree_randomly_gs(drift_tree, proportion_random_evolution)
    deleted_acs.extend(deleted_ac)
    added_acs.extend(added_ac)
    moved_acs.extend(moved_ac)
    log_final = semantics.generate_log(tree_two, nu_traces_evl)
    result = combine_two_logs(result, log_final)
    l = 0
    for x in trees:
        if l >= 0:
            ptml_exporter.apply(x, "Data/result_data/doc/"+str(l)+"_version_incremental_drift.ptml")
        l = l + 1
    ptml_exporter.apply(tree_two, "Data/result_data/doc/"+str(l)+"_version_incremental_drift.ptml")
    return result, deleted_acs, added_acs, moved_acs


def incremental_drift_gs(tree_one, start_point, end_point, nu_traces, nu_models, proportion_random_evolution):
    """ Generation of an event log with an incremental drift for gold standard generation

    :param proportion_random_evolution: proportion of the process model version to be evolved
    :param tree_one: initial model
    :param start_point: starting point for the incremental drift
    :param end_point: ending point for the incremental drift
    :param nu_traces: number traces in event log
    :param nu_models: number of intermediate models
    :return: event log with incremental drift
    """
    deleted_acs = []
    added_acs = []
    moved_acs = []
    start_traces = int(round((nu_traces * start_point) + 0.0001))
    drift_traces = int(round(((nu_traces - start_traces - (nu_traces * (1 - end_point))) / (nu_models - 1)) + 0.0001))
    end_traces = nu_traces - start_traces - (drift_traces * (nu_models - 1))
    result = semantics.generate_log(tree_one, start_traces)
    i = 0
    trees = [tree_one]
    while i < nu_models - 1:
        drift_tree = copy.deepcopy(trees[i])
        tree_ev, deleted_ac, added_ac, moved_ac = evolve_tree_randomly_gs(drift_tree, proportion_random_evolution)
        deleted_acs.extend(deleted_ac)
        added_acs.extend(added_ac)
        moved_acs.extend(moved_ac)
        trees.append(tree_ev)
        log = semantics.generate_log(trees[i + 1], drift_traces)
        result = combine_two_logs(result, log)
        i = i + 1
    drift_tree = copy.deepcopy(trees[i])
    tree_ev, deleted_ac, added_ac, moved_ac = evolve_tree_randomly_gs(drift_tree, proportion_random_evolution)
    deleted_acs.extend(deleted_ac)
    added_acs.extend(added_ac)
    moved_acs.extend(moved_ac)
    log = semantics.generate_log(tree_ev, end_traces)
    result = combine_two_logs(result, log)
    return result, deleted_acs, added_acs, moved_acs


def log_with_incremental_drift_two_models_random(tree_one, tree_two, nu_models, parameters):
    """ Generation of an event log with an incremental drift from two random process model version

    :param parameters: parameters for the generated process tree
    :param nu_models: number of evolving models
    :param tree_one: process tree one
    :param tree_two: process tree two
    :return: event log with incremental drift
    """

    nu_old_model = input_int_hun("Number of traces from initial version in the event log (x >= 100): ")
    log_old = semantics.generate_log(tree_one, nu_old_model)
    logs_combined = EventLog()
    if nu_models > 0:
        nu_evo_model = input_int("Number of traces from 1. evolved version in the log (int): ")
        log_first = semantics.generate_log(generate_tree(parameters), nu_evo_model)
        logs_combined = combine_two_logs(log_old, log_first)
    i = 2
    while i <= nu_models:
        nu_ev_model = input_int("Number of traces from " + str(i) + ". evolved version in the log (int): ")
        log_evolved = semantics.generate_log(generate_tree(parameters), nu_ev_model)
        logs_combined = combine_two_logs(logs_combined, log_evolved)
        i = i + 1
    nu_new_model = input_int("Number of traces from the final version  (second imported model) in the log (int): ")
    log_new = semantics.generate_log(tree_two, nu_new_model)
    logs_combined = combine_two_logs(logs_combined, log_new)
    return logs_combined


def log_with_incremental_drift_two_models_imported(log_old, tree_two, trees, nu_models):
    """ Generation of an event log with an incremental drift from two given process model versions

    :param trees: first process tree version
    :param nu_models: number of evolving model version
    :param log_old: first part of event log from initial model version
    :param tree_two: last evolved process tree version
    :return: event log with incremental drift
    """
    logs_combined = EventLog()
    if nu_models > 0:
        nu_evo_model = input_int("Number of traces from 1. evolved version in the log (int): ")
        log_first = semantics.generate_log(trees[0], nu_evo_model)
        logs_combined = combine_two_logs(log_old, log_first)
    i = 1
    while i < nu_models:
        nu_ev_model = input_int("Number of traces from " + str(i + 1) + ". evolved model version in the log (int): ")
        log_evolved = semantics.generate_log(trees[i], nu_ev_model)
        logs_combined = combine_two_logs(logs_combined, log_evolved)
        i = i + 1
    nu_new_model = input_int("Number of traces from the new resulting version in the log (int): ")
    log_new = semantics.generate_log(tree_two, nu_new_model)
    logs_combined = combine_two_logs(logs_combined, log_new)
    return logs_combined


def log_with_incremental_drift_one_model(tree, nu_models, step):
    """ Generation of an event log with an incremental drift from on process tree version

    :param tree: initial process tree version
    :param nu_models: number of evolving model versions
    :param step: number of event log
    :return: event log with incremental drift
    """
    nu_old_model = input_int("Number of traces from initial model version in the log (x >= 100): ")
    log_old = semantics.generate_log(tree, nu_old_model)
    return incremental_drift_one_model(tree, log_old, nu_models, step, 'incremental')


def additional_incremental_drift_in_log_imported(log, tree_two, trees, nu_models):
    add_end = input_end("Adding the additional recurring drift at the end of the log or into the log [end, into]? ")
    if add_end == 'into':
        pro_old_model = input_percentage("Proportion of the previously generated log in the new log (0 < x < 1): ")
        log_old = get_part_of_log(log, pro_old_model)
        return log_with_incremental_drift_two_models_imported(log_old, tree_two, trees, nu_models)
    else:
        return log_with_incremental_drift_two_models_imported(log, tree_two, trees, nu_models)


def additional_incremental_drift_in_log(log, tree, nu_models, step, drift_type, drift_step):
    """

    :param drift_step: number of drift in log
    :param drift_type: first drift in the log
    :param log: event log including a drift
    :param tree: first process model
    :param nu_models: number of evolving models
    :param step: number of event log
    :return: event log with incremental drift
    """
    add_end = input_end("Adding the additional recurring drift at the end of the log or into the log [end, into]? ")
    if add_end == 'into':
        pro_old_model = input_percentage("Proportion of the previously generated log in the new log (0 < x < 1): ")
        log_old = get_part_of_log(log, pro_old_model)
        return incremental_drift_one_model(tree, log_old, nu_models, step,
                                           drift_type + "_and_incremental_" + str(drift_step))
    else:
        return incremental_drift_one_model(tree, log, nu_models, step,
                                           drift_type + "_and_incremental_" + str(drift_step))


def incremental_drift_one_model(tree, log_old, nu_models, step, str_incremental):
    """ Generation of an event log with an incremental drift from on process tree version

    :param tree: initial process tree version
    :param log_old: existing event log
    :param nu_models: number of evolving tree versions
    :param step: number of event log
    :param str_incremental: identifier for folder
    :return:
    """
    trees = list()
    trees.append(tree)
    ran = input_ra_ch('Evolution of the process tree controlled or random [controlled, random]: ')
    if ran == 'random':
        trees.append(change_tree_on_control_flow_incremental_random(trees[0], 1))
        nu_evo_model = input_int("Number of traces from 1. evolved model version in the log (int): ")
        log_first = semantics.generate_log(trees[1], nu_evo_model)
        logs_combined = combine_two_logs(log_old, log_first)
        i = 2
        while i <= nu_models:
            trees.append(change_tree_on_control_flow_incremental_random(trees[i - 1], i))
            nu_ev_model = input_int("Number of traces from " + str(i) + ". evolved model version in the event log (int): ")
            log_evolved = semantics.generate_log(trees[i], nu_ev_model)
            logs_combined = combine_two_logs(logs_combined, log_evolved)
            i = i + 1
    else:
        print("\n--- INFORMATION FOR THE INCREMENTAL EVOLUTION ---\n"
              "The following main operators are available for the evolution of the process tree versions:\n"
              "\t- change_activity: all procedures to change activities [add_ac, swap_acs, delete_ac, change_ac]\n"
              "\t- change_operator: all procedures to change operators [replace_op, swap_ops]\n"
              "\t- change_tree_fragment: all procedures to change a tree fragment [add_fragment, delete_fragment, swap_fragment, move_fragment]\n"
              "\t- delete_silent_ac: delete an undesired silent activity\n"
              "The process tree opened as a picture provides orientation for evolution.\n"
              "After each completed evolution, the new process tree version appears, which must be used as a guide for further versions.\n"
              "The number of traces for the evolved model version is set in the event log directly after its evolution.\n"
              "To achieve each desired process tree version, multiple sub-development may need to be performed.\n"
              "Please note that if the input is not correct, the tree version will not change (depth starts with 0 at the parent node).\n"
              "Moreover, a node with an 'xor loop' operator can only have at least two and at most three children.\n"
              "The following activities are contained in the tree: " + str(tree._get_leaves()) + "\n")
        trees.append(change_tree_on_control_flow_incremental(trees[0], 1))
        nu_evo_model = input_int("Number of traces from 1. evolved model version in the log (int): ")
        log_first = semantics.generate_log(trees[1], nu_evo_model)
        logs_combined = combine_two_logs(log_old, log_first)
        i = 2
        while i <= nu_models:
            trees.append(change_tree_on_control_flow_incremental(trees[i - 1], i))
            nu_ev_model = input_int("Number of traces from " + str(i) + ". evolved model version in the event log (int): ")
            log_evolved = semantics.generate_log(trees[i], nu_ev_model)
            logs_combined = combine_two_logs(logs_combined, log_evolved)
            i = i + 1
    j = 1
    if not os.path.exists(
            'Data/result_data/terminal/generated_models/evolved_versions_' + str_incremental + '_for_log_' + str(step)):
        os.makedirs(
            'Data/result_data/terminal/generated_models/evolved_versions_' + str_incremental + '_for_log_' + str(step))
    while j < len(trees):
        ptml_exporter.apply(trees[j],
                            "Data/result_data/terminal/generated_models/evolved_versions_" + str_incremental + "_for_log_" + str(
                                step) + "/evolved_version_" + str(j) + ".ptml")
        j = j + 1
    length = len(trees)
    return logs_combined, trees[length - 1]
