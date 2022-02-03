from mpmath.libmp.backend import xrange
from pm4py.objects.log.obj import EventLog
from pm4py.objects.process_tree.obj import ProcessTree

from ConceptDrifts.gradual_drift import additional_gradual_drift_in_log, gradual_drift
from ConceptDrifts.incremental_drift import log_with_incremental_drift_two_models_random, \
    log_with_incremental_drift_two_models_imported, additional_incremental_drift_in_log, \
    additional_incremental_drift_in_log_imported
from ConceptDrifts.recurring_drift import additional_recurring_drift_in_log, recurring_drift
from ConceptDrifts.sudden_drift import sudden_drift, additional_sudden_drift_in_log
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.process_tree import semantics

from Source.control_flow_controller import change_tree_on_control_flow
from Source.input_controller import input_int, input_drift, input_percentage, input_date, input_typ_gradual, \
    generate_tree_out_of_file, input_int_hun, input_int_max, input_yes_no, input_im, input_tree_one, input_comp, input_season
from Source.noise_controller import add_noise_to_log
from Source.process_tree_controller import visualise_tree, generate_specific_trees


def generate_logs_with_models(tree_one, tree_two, nu_logs, incremental_ran, parameters=None):
    """ Generation of event logs with different concept drifts from two models

    :param nu_logs: number of event logs to be generated
    :param parameters: the possible changed parameters for the generation of random process trees
    :param incremental_ran: boolean if incremental drift with random process trees
    :param tree_one: first process tree
    :param tree_two: second process tree
    """
    for i in xrange(1, nu_logs + 1):
        print("\n--- INPUT " + str(i) + ". EVENT LOG ---")
        datestamp = input_date("Starting date of the first trace in the event log (y/d/m H:M:S like '20/23/8 8:0:0'): ")
        min_duration = input_int("Minimum for the duration of the activities in the event log in seconds (int): ")
        max_duration = input_int_max("Maximum for the duration of the activities in the event log in seconds (int): ",
                                     min_duration)
        drift_type = input_drift("Type of concept drift [sudden, gradual, recurring, incremental]: ")
        log = EventLog()

        if drift_type == 'sudden':
            nu_traces = input_int_hun("Number of traces in the event log (x >= 100): ")
            time_of_drift_perc = input_percentage("starting point of the drift (0 < x < 1): ")
            log = sudden_drift(tree_one, tree_two, nu_traces, time_of_drift_perc)

        elif drift_type == 'gradual':
            nu_traces = input_int_hun("Number of traces in the event log (x >= 100): ")
            time_of_drift_start_perc = input_percentage("Starting point of the drift (0 < x < 1): ")
            time_of_drift_end_perc = input_percentage("Ending point of the drift (0 < x < 1): ")
            gradual_type = input_typ_gradual("Method for distributing the traces during the gradual drift [linear, exponential]: ")
            log = gradual_drift(tree_one, tree_two, nu_traces, time_of_drift_start_perc, time_of_drift_end_perc, gradual_type)

        elif drift_type == 'recurring':
            nu_traces = input_int_hun("Number of traces in the event log (x >= 100): ")
            sector_log = input_yes_no("Do you want the recurring drift to persist throughout the event log [yes, no]? ")
            if sector_log == 'yes':
                start_point = 0
                end_point = 1
                number_of_seasonal_changes = input_int("Number of seasonal changes of the model versions (int): ")
            else:
                start_point = input_percentage("Starting point of the drift (0 < x < 1): ")
                end_point = input_percentage("Ending point of the drift (0 < x < 1): ")
                number_of_seasonal_changes = input_season(start_point, end_point)
            proportion_first = input_percentage("Proportion of the initial version of the model in the final log (0 < x < 1): ")
            log = recurring_drift(tree_one, tree_two, nu_traces, number_of_seasonal_changes, proportion_first, start_point, end_point)

        elif drift_type == 'incremental':
            if incremental_ran:
                nu_models = input_int("Number of evolving model versions in the event log (int): ")
                log = log_with_incremental_drift_two_models_random(tree_one, tree_two, nu_models,
                                                                   parameters)

            else:
                nu_models = input_int("Number of evolving model versions in the event log (int): ")
                j = 1
                trees = []
                while j <= nu_models:
                    tree_ev = generate_tree_out_of_file(
                        "File path of the " + str(
                            j) + ". evolved model version, which has to be 'pnml', 'bpmn' or 'ptml' (e.g. 'Data/test_data/bpmn/model_00.bpmn'): ")
                    trees.append(tree_ev)
                    j = j + 1
                nu_old_model = input_int_hun("Number of traces from the initial model version in the event log (x >= 100): ")
                log_old = semantics.generate_log(tree_one, nu_old_model)
                log = log_with_incremental_drift_two_models_imported(log_old, tree_two, trees, nu_models)

        result = add_additional_drift_and_noise_in_log(log, tree_one, tree_two, datestamp, min_duration,
                                                       max_duration,
                                                       drift_type, i)
        xes_exporter.apply(result,
                           "Data/result_data/terminal/event_logs/event_log_" + str(i) + "_with_" + drift_type + "_drift.xes")
        print("Event log 'event_log_" + str(
            i) + "_with_" + drift_type + "_drift' is saved in the folder 'Data/result_data/event_logs'.")
        if drift_type == 'incremental':
            print(
                "Evolved process model versions are saved in the folder 'Data/result_data/terminal/generated_models/evolved_versions_incremental_for_log_" + str(
                    i) + "'.")
        else:
            print("Evolved model versions 'evolved_model_for_log_" + str(
                i) + "' is saved in the folder 'Data/result_data/terminal/generated_models'.")


def add_additional_drift_and_noise_in_log(log, tree_one, tree_two, datestamp, min_duration, max_duration,
                                          drift_type_one, step):
    """ Introduction of additional drift and noise into an event log

    :param log: event log
    :param tree_one: initial process tree version
    :param tree_two: evolved process tree version
    :param datestamp: Starting date of the event log
    :param min_duration: minimum duration of activities
    :param max_duration: maximum duration of activities
    :param drift_type_one: additional drift type
    :param step: number of event log
    :return: event log
    """
    addi_drift = input_yes_no("Do you want to add an additional drift to the event log [yes, no]? ")
    drift_step = 2
    trees = [tree_two]
    tree_ev = ProcessTree()
    tree = ProcessTree()
    while addi_drift == 'yes':

        print("\n--- INFORMATION FOR ADDITIONAL DRIFT IN THE EVENT LOG ---\n"
              "Please note that by incautiously setting parameters the previously created drift can be destroyed.\n"
              "It can be decided whether the additional drift is placed at the end or in the event log.\n"
              "If the additional drift for the sudden, gradual and recurring type is added at the end of the log, the number of traces will change.\n"
              "If incremental drift is selected, the number of traces in the resulting event log may change regardless of whether it is set in or at the end of the event log.\n"
              "For the evolution of the process model version, it can be decided between evolving the first or last imported model, importing an new model, or generating an random model.\n")
        drift_type = input_drift(
            "Type of " + str(
                drift_step) + ". concept drift in the event log [sudden, gradual, recurring, incremental]: ")
        str_imp = input_im(
            "Importing a new model version for the drift, generating a random model or evolving an already existing model [import, random, evolve]: ")
        if str_imp == 'import' and drift_type != 'incremental':
            tree_ev = generate_tree_out_of_file(
                "File path of the model version, which has to be 'pnml', 'bpmn' or 'ptml' (e.g. 'Data/test_data/bpmn/model_00.bpmn'): ")
            tree = tree_one
        elif str_imp == 'random' and drift_type != 'incremental':
            str_clp = input_comp("Complexity of the process tree to be generated [simple, middle, complex]: ")
            tree_ev = generate_specific_trees(str_clp)
        elif str_imp == 'evolve':
            str_tree_kind = input_tree_one(
                "Process model version for the evolution of the additional " + drift_type + " drift [first_version, last_version]: ")
            if str_tree_kind == 'first_version':
                visualise_tree(tree_one)
                tree = tree_one
            else:
                length = len(trees)
                visualise_tree(trees[length - 1])
                tree = trees[length - 1]
            if drift_type != 'incremental':
                tree_ev = change_tree_on_control_flow(tree)

        if drift_type == 'sudden':
            log = additional_sudden_drift_in_log(log, tree_ev)

        elif drift_type == 'gradual':
            log = additional_gradual_drift_in_log(log, tree, tree_ev)

        elif drift_type == 'recurring':
            log = additional_recurring_drift_in_log(log, tree, tree_ev)

        elif drift_type == 'incremental':
            nu_models = input_int("Number of evolving versions (int): ")
            if str_imp == 'import':
                j = 1
                trees_one = []
                while j <= nu_models:
                    tree_evo = generate_tree_out_of_file(
                        "File path of the " + str(
                            j) + ". evolved model version, which has to be 'pnml', 'bpmn' or 'ptml' (e.g. 'Data/test_data/bpmn/model_00.bpmn'): ")
                    trees_one.append(tree_evo)
                    j = j + 1
                tree_ev = trees_one[len(trees_one) - 1]
                log = additional_incremental_drift_in_log_imported(log, tree_ev, trees_one, nu_models-1)
            elif str_imp == "random":
                str_clp = input_comp("Complexity of the process tree to be generated [simple, middle, complex]: ")
                j = 1
                trees_one = []
                while j <= nu_models:
                    tree_evo = generate_specific_trees(str_clp)
                    trees_one.append(tree_evo)
                    j = j + 1
                tree_ev = trees_one[len(trees_one) - 1]
                log = additional_incremental_drift_in_log_imported(log, tree_ev, trees_one, nu_models-1)
            else:
                log, tree_ev = additional_incremental_drift_in_log(log, tree, nu_models, step, drift_type_one, drift_step)
        trees.append(tree_ev)
        drift_step = drift_step + 1
        addi_drift = input_yes_no("Do you want to add an additional drift to the event log [yes, no]? ")

    return add_noise_to_log(log, tree_one, datestamp, min_duration, max_duration)
