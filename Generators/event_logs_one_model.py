from mpmath.libmp.backend import xrange
from pm4py.objects.log.obj import EventLog
from pm4py.objects.process_tree.obj import ProcessTree

from ConceptDrifts.gradual_drift import additional_gradual_drift_in_log, gradual_drift
from ConceptDrifts.incremental_drift import log_with_incremental_drift_one_model, additional_incremental_drift_in_log
from ConceptDrifts.recurring_drift import additional_recurring_drift_in_log, recurring_drift
from ConceptDrifts.sudden_drift import sudden_drift, additional_sudden_drift_in_log
from pm4py.objects.log.exporter.xes import exporter as xes_exporter

from Source.control_flow_controller import change_tree_on_control_flow
from Source.input_controller import input_drift, input_int, input_date, input_percentage, \
    input_typ_gradual, input_int_hun, input_yes_no, input_tree, input_int_max, input_season
from Source.noise_controller import add_noise_to_log
from Source.process_tree_controller import visualise_tree
from pm4py.objects.process_tree.exporter import exporter as ptml_exporter


def generate_logs_with_model(tree_one, nu_logs):
    """ Generation of event logs with different concept drifts from one model

    :param nu_logs: number of event logs to be generated
    :param tree_one: the initial model version
    """

    for i in xrange(1, nu_logs + 1):

        print("\n--- INPUT " + str(i) + ". EVENT LOG ---")
        datestamp = input_date("Starting date of the first trace in the event log (y/d/m H:M:S like '20/23/8 8:0:0'): ")
        min_duration = input_int("Minimum for the duration of the activities in the event log in seconds (int) {default: 1}: ")
        max_duration = input_int_max("Maximum for the duration of the activities in the event log in seconds (int) {default: }: ",
                                     min_duration)
        drift_type = input_drift("Type of concept drift [sudden, gradual, recurring, incremental]: ")
        log = EventLog()
        tree_two = ProcessTree()

        if drift_type == 'sudden':
            nu_traces = input_int_hun("Number of traces in the event log (x >= 100): ")
            drift_time = input_percentage("Starting point of the drift (0 < x < 1): ")
            tree_two = change_tree_on_control_flow(tree_one)
            log = sudden_drift(tree_one, tree_two, nu_traces, drift_time)

        elif drift_type == 'gradual':
            nu_traces = input_int_hun("Number of traces in the event log (x >= 100): ")
            drift_time_start = input_percentage("Starting point of the drift (0 < x < 1): ")
            drift_time_end = input_percentage("Ending point of the drift (0 < x < 1): ")
            distribution_type = input_typ_gradual("Method for distributing the traces during the gradual drift [linear, exponential]: ")
            tree_two = change_tree_on_control_flow(tree_one)
            log = gradual_drift(tree_one, tree_two, nu_traces, drift_time_start, drift_time_end, distribution_type)

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

            proportion_first = input_percentage(
                "Proportion of the first model version in the drift sector of the log (0 < x < 1): ")
            tree_two = change_tree_on_control_flow(tree_one)
            log = recurring_drift(tree_one, tree_two, nu_traces, number_of_seasonal_changes, proportion_first,
                                  start_point, end_point)

        elif drift_type == 'incremental':
            nu_models = input_int("Number of evolving versions (int): ")
            log, tree_two = log_with_incremental_drift_one_model(tree_one, nu_models, i)

        result = add_additional_drift_and_noise_in_log(log, tree_one, tree_two, datestamp, min_duration, max_duration,
                                                       drift_type, i)
        xes_exporter.apply(result,
                           "Data/result_data/terminal/event_logs/event_log_" + str(
                               i) + "_with_" + drift_type + "_drift.xes")
        print("Event log 'event_log_" + str(
            i) + "_with_" + drift_type + "_drift' is saved in the folder 'Data/result_data/terminal/event_logs'.")
        if drift_type == 'incremental':
            print(
                "Evolved process models are saved in the folder 'Data/result_data/terminal/generated_models/evolved_versions_incremental_for_log_" + str(
                    i) + "'.")
        else:
            ptml_exporter.apply(tree_two,
                                "Data/result_data/terminal/generated_models/evolved_version_for_log_" + str(
                                    i) + ".ptml")
            print("Evolved model is saved in the folder 'Data/result_data/terminal/generated_models'.")


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
    while addi_drift == 'yes':

        print("\n--- INFORMATION FOR ADDITIONAL DRIFT IN THE EVENT LOG ---\n"
              "Please note that by incautiously setting parameters the previously created drift can be destroyed.\n"
              "It can be decided whether the additional drift is placed at the end or in the event log.\n"
              "If the additional drift for the sudden, gradual and recurring type is added at the end of the log, the number of traces will change.\n"
              "If incremental drift is selected, the number of traces in the resulting event log may change regardless of whether it is set in or at the end of the event log.\n"
              "For the evolution of the process model version, it can be decided between the initial version or the last evolved version.\n")
        drift_type = input_drift(
            "Type of " + str(
                drift_step) + ". concept drift in the event log [sudden, gradual, recurring, incremental]: ")

        str_tree_kind = input_tree(
            "Process model version for the evolution of the additional " + drift_type + " drift [initial_version, evolved_version]: ")
        if str_tree_kind == 'initial_version':
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
            nu_models = input_int("Number of evolving models (int): ")
            log, tree_ev = additional_incremental_drift_in_log(log, tree, nu_models, step, drift_type_one, drift_step)
        if drift_type != 'incremental':
            ptml_exporter.apply(tree_two,
                                "Data/result_data/terminal/generated_models/"+str(drift_step)+"_evolved_version_for_log_" + str(
                                    step) + ".ptml")
        trees.append(tree_ev)
        drift_step = drift_step + 1
        addi_drift = input_yes_no("Do you want to add an additional drift to the event log [yes, no]? ")

    return add_noise_to_log(log, tree_one, datestamp, min_duration, max_duration)
