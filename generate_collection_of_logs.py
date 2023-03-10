import copy
import datetime
import csv
import os
import sys
from random import randint, uniform
import ast
from datetime import datetime
from controllers import configurations as config
from concept_drifts.gradual_drift import gradual_drift
from concept_drifts.incremental_drift import incremental_drift_gs
from concept_drifts.recurring_drift import recurring_drift, recurring_drift_new
from concept_drifts.sudden_drift import sudden_drift
from concept_drifts.without_drift import no_drift
from controllers.control_flow_controller import evolve_tree_randomly
from controllers.event_log_controller import add_duration_to_log, get_timestamp_log
from controllers.noise_controller_new import insert_noise
from controllers.drift_info_collection import DriftInfo, extract_change_moments
from controllers.drift_info_collection import NoiseInfo
from controllers.drift_info_collection import LogDriftInfo
from controllers.process_tree_controller import generate_tree_from_file, generate_specific_trees
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from controllers.input_parameters import InputParameters
import time


def generate_logs(file_path_to_own_models=None):
    """ Generation of a set of event logs with different drifts, a corresponding CSV file and respective text files
    :param file_path_to_own_models: file path to own process model, if desired to be used
    :return: collection of event logs with drifts saved in out_folder
    """

    # CREATE DICTIONARY TO STORE LOG ATTRIBUTE DATA
    drift_dic_attr = {}
    noise_dic_attr = {}

    # CREATE DIR TO STORE GENERATED LOGS
    out_folder = os.path.join(config.DEFAULT_LOG_COLLECTION_OUTPUT_DIR, str(int(time.time())))
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    # READE PARAMETERS FROM A FILE
    parameters_dict = get_parameters(config.PAR_LOG_COLLECTION)
    par = InputParameters(**parameters_dict)

    # MAIN LOOP
    number_of_logs = select_random(par.Number_event_logs)
    print('Generating', number_of_logs, 'logs')
    collection = LogDriftInfo()
    for i in range(number_of_logs):
        drift_dic_attr["log_id"] = i
        noise_dic_attr["log_id"] = i
        # SELECT PARAMETERS FOR THE CURRENT LOG
        num_traces = select_random(par.Number_traces_per_event_log, option='uniform_int')
        tree_one, complexity = generate_initial_tree(par.Process_tree_complexity, file_path_to_own_models)
        drift = select_random(par.Drift_types, option='random')
        drift_area_one, drift_area_two = drift_area_selection(par.Drift_area)
        ran_evolve = select_random(par.Process_tree_evolution_proportion, option='uniform')
        drift_tree = copy.deepcopy(tree_one)
        tree_two, deleted_acs, added_acs, moved_acs = evolve_tree_randomly(drift_tree, ran_evolve)

        # GENERATE LOG WITH A CERTAIN DRIFT TYPE
        # TODO: create ENUM class for different drift type?
        if drift == 'sudden':
            event_log = sudden_drift(tree_one, tree_two, num_traces, drift_area_one)
            drift_dic_attr["tree"] = [tree_one, tree_two]
        elif drift == 'gradual':
            gr_type = select_random(par.Gradual_drift_type, option='random')
            event_log = gradual_drift(tree_one, tree_two, num_traces, drift_area_one, drift_area_two, gr_type)
            drift_dic_attr["tree"] = [tree_one, tree_two]
        elif drift == 'recurring':
            number_of_seasonal_changes = select_random(par.Recurring_drift_number, option='random')
            event_log = recurring_drift_new(tree_one, tree_two, num_traces, number_of_seasonal_changes)
            drift_dic_attr["tree"] = [tree_one, tree_two]
        elif drift == 'incremental':
            num_models = select_random(par.Incremental_drift_number, option='random')
            ran_in_evolve = round(ran_evolve / num_models, 2)
            # TODO: write a new incremental drift generation function
            event_log, deleted_acs, added_acs, moved_acs, tree_list = incremental_drift_gs(tree_one, drift_area_one,
                                                                                           drift_area_two, num_traces,
                                                                                           num_models, ran_in_evolve)

            drift_dic_attr["Tree"] = tree_list
            drift_dic_attr["deleted_acs"] = deleted_acs
            drift_dic_attr["added_acs"] = added_acs
            drift_dic_attr["moved_acs"] = moved_acs
        else:
            event_log = no_drift(tree=tree_one, nu_traces=num_traces)
        drift_dic_attr["drift_type"] = drift  # Store the drift_type in the dictionary

        # TODO@Zied: please update the DriftInfo class s.t. the attribute 'drift_time' takes the following dict
        change_moments_dict = extract_change_moments(event_log)
        drift_dic_attr["drift_time"] = change_moments_dict  # Store the drift_time in the dictionary

        # ADD NOISE
        if par.Noise:
            event_log = insert_noise(event_log, par.Noisy_trace_prob[0], par.Noisy_event_prob[0])

        # ADD TIMESTAMPS
        add_duration_to_log(event_log, par.Timestamp_first_trace[0], par.Trace_exp_arrival_sec[0],
                            par.Task_exp_duration_sec[0])

        # CREATE DRIFT INFO INSTANCE
        # TODO@Zied: please update
        drift_dic_attr["drift_id"] = collection.number_of_drifts
        drift_dic_attr["process_perspective"] = "control-flow"
        if drift.casefold() != "none":  # if there is a drift
            drift_dic_attr["drift"] = True
            DI = DriftInfo(drift_dic_attr)
        else:
            drift_dic_attr["drift"] = False
            DI = DriftInfo(drift_dic_attr)

        collection.add_drift(DI)
        collection.increase_drift_count()
        event_log.attributes["drift:info"] = DI.drift_info_to_dict()

        # CREATE NOISE INFO INSTANCE
        # TODO@Zied: please add

        # EXPORT GENERATED LOG
        xes_exporter.apply(event_log, os.path.join(out_folder, "log_" + str(i) + ".xes"))
    print('Finished generating collection of', number_of_logs, 'logs in', out_folder)


def generate_initial_tree(complexity_options_list: list, file_path_to_own_models):
    complexity = select_random(complexity_options_list, option='random')
    if file_path_to_own_models is None:
        generated_process_tree = generate_specific_trees(complexity.strip())
    else:
        generated_process_tree = generate_tree_from_file(file_path_to_own_models)
    print(f"Used process tree complexity: {complexity}")
    return generated_process_tree, complexity


def select_random(data: list, option: str = 'random') -> any:
    if len(data) == 1:
        data_selected = data[0]
    elif len(data) == 2 and option == 'uniform':
        data_selected = uniform(data[0], data[1])
    elif len(data) == 2 and option == 'uniform_int':
        data_selected = randint(data[0], data[1])
    elif len(data) == 2 and option == 'random':
        data_selected = data[randint(0, len(data) - 1)]
    else:
        data_selected = None
        Warning(f"Check function 'select_random' call: {data, option, data_selected}")

    if isinstance(data, float):
        data_selected = round(data_selected, 2)

    return data_selected


def drift_area_selection(data: list, option: float = 0.2) -> any:
    data_length = data[1] - data[0]
    drift_area_one = round(uniform(data[0], (data[0] + (1 - option) * data_length)), 2)
    drift_area_two = round(uniform(drift_area_one + data_length * option, data[1]), 2)

    return drift_area_one, drift_area_two


def get_parameters(par_file_name: str):
    """ Getting parameters from the text file 'parameters_log_collection' placed in the folder 'Data/parameters'
    :return: parameters for the generation of a set of event logs
    """

    parameter_doc = open(f'{config.DEFAULT_PARAMETER_DIR}/{par_file_name}', 'r')
    parameters_input = parameter_doc.read()
    parameter_doc.close()
    parameters_dict = {}
    count = 0
    for line in parameters_input.split('\n'):
        if line:
            par = line.split(': ')[0]
            value = line.split(': ')[1]
            if '/' in value:
                value = [datetime.strptime(v, '%Y/%m/%d %H:%M:%S') for v in value.split(',')]
            elif '-' in value:
                value = value.split('-')
            else:
                value = value.split(', ')

            try:
                value = [ast.literal_eval(v) for v in value]
            except:
                pass
            parameters_dict[par] = value

    return parameters_dict


def main():
    if len(sys.argv) == 1:
        generate_logs()
    elif len(sys.argv) == 2:
        generate_logs(sys.argv[1])


if __name__ == '__main__':
    main()
