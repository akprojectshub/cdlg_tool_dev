from Source.input_controller import input_date, input_int_hun, input_int, input_int_max
from pm4py.objects.process_tree import semantics
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.conversion.log import converter as log_converter

from Source.noise_controller import add_noise_to_log


def generate_log_without_drift(tree, nu_logs):
    """ Generation of an event log without any drift

    :param tree: the initial version of the process model
    :param nu_logs: number traces in event log
    :return: event log
    """
    i = 1
    while i <= nu_logs:
        print("\n--- INPUT FOR "+str(i)+". EVENT LOG ---\n")
        datestamp = input_date("Starting date of the first trace in the event log (y/d/m H:M:S like '20/23/8 8:0:0'): ")
        min_duration = input_int("Minimum for the duration of the activities in the event log in seconds (int): ")
        max_duration = input_int_max("Maximum for the duration of the activities in the event log in seconds (int): ", min_duration)
        nu_traces = input_int_hun("Number of traces in the event log (x >= 100): ")
        log = semantics.generate_log(tree, nu_traces)
        result = add_noise_to_log(log, tree, datestamp, min_duration, max_duration)
        xes_exporter.apply(result,
                           "Data/result_data/terminal/event_logs/event_log_" + str(i) + "_without_drift.xes")
        dataframe = log_converter.apply(result, variant=log_converter.Variants.TO_DATA_FRAME)
        dataframe.to_csv("Data/result_data/terminal/event_logs/event_log_" + str(i) + "_without_drift.csv")
        print("Event log 'event_log_" + str(
            i) + "_without_drift' is saved in the folder 'Data/result_data/terminal/event_logs'.")
        i = i + 1
