import copy
import datetime
import os
import sys
from random import randint, uniform
import ast
from datetime import datetime
from enum import Enum
from controllers import configurations as config
from concept_drifts.gradual_drift import gradual_drift
from concept_drifts.incremental_drift import incremental_drift_gs
from concept_drifts.drift_types import add_recurring_drift
from concept_drifts.sudden_drift import sudden_drift
from concept_drifts.without_drift import no_drift
from controllers.control_flow_controller import evolve_tree_randomly
from controllers.event_log_controller import add_duration_to_log
from controllers.noise_controller_new import insert_noise
from controllers.drift_info_collection import DriftInfo, extract_change_moments_to_list
from controllers.drift_info_collection import NoiseInfo
from controllers.drift_info_collection import LogDriftInfo
from controllers.process_tree_controller import generate_tree_from_file, generate_specific_trees
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from controllers.input_parameters import InputParameters
from concept_drifts.change_types import add_sudden_change, add_gradual_change
import time


def generate_logs(file_path_to_own_models=None):
    """ Generation of a set of event logs with different drifts, a corresponding CSV file and respective text files
    :param file_path_to_own_models: file path to own process model, if desired to be used
    :return: collection of event logs with drifts saved in out_folder
    """

    # CREATE DIR TO STORE GENERATED LOGS
    out_folder = creat_output_folder(config.DEFAULT_LOG_COLLECTION_OUTPUT_DIR)

    # READE PARAMETERS FROM A FILE
    par = get_parameters(config.PAR_LOG_COLLECTION)

    # MAIN LOOP
    number_of_logs = select_random(par.Number_event_logs)
    print('Generating', number_of_logs, 'logs')
    collection = LogDriftInfo()
    for log_id in range(1, number_of_logs + 1):
        # SELECT PARAMETERS FOR THE CURRENT LOG
        log_name = "log_" + str(log_id) + '_' + str(int(time.time())) + ".xes"
        tree_one, complexity = generate_initial_tree(par.Process_tree_complexity, file_path_to_own_models)
        tree_list = [tree_one]
        num_traces = select_random(par.Number_traces_per_event_log, option='uniform_int')
        event_log = no_drift(tree=tree_one, nu_traces=num_traces)


        drift_n = select_random(par.Number_drifts_per_log, option='uniform_int')
        for drift_id in range(1, drift_n+1):
            tree_previous = copy.deepcopy(tree_list[-1])
            drift = select_random(par.Drift_types, option='random')
            drift_area_one, drift_area_two = drift_area_selection(par.Drift_area)
            ran_evolve = select_random(par.Process_tree_evolution_proportion, option='uniform')
            tree_new, deleted_acs, added_acs, moved_acs = evolve_tree_randomly(tree_previous, ran_evolve)
            num_traces = select_random(par.Number_traces_per_event_log, option='uniform_int')
            tree_list.append(tree_new)

            # GENERATE LOG WITH A CERTAIN DRIFT TYPE
            if drift == DriftTypes.sudden.value:
                event_log = add_sudden_change(event_log, tree_new, num_traces)
            elif drift == DriftTypes.gradual.value:
                gradual_type = select_random(par.Gradual_drift_type, option='random')
                #event_log = gradual_drift(tree_previous, tree_new, num_traces, drift_area_one, drift_area_two, gr_type)
                event_log = add_gradual_change(event_log, tree_previous, tree_new, num_traces, num_traces/2, gradual_type)
            elif drift == DriftTypes.recurring.value:
                number_of_seasonal_changes = select_random(par.Recurring_drift_number, option='random')
                event_log = add_recurring_drift(event_log, tree_previous, tree_new, num_traces, number_of_seasonal_changes)
            elif drift == DriftTypes.incremental.value:
                # TODO: rewrite the incremental drift generation function (focus on simplification)
                num_models = select_random(par.Incremental_drift_number, option='random')
                result = incremental_drift_gs(tree_previous, drift_area_one, drift_area_two, num_traces, num_models, ran_evolve)
                event_log, deleted_acs, added_acs, moved_acs, tree_list = result
            else:
                event_log = no_drift(tree=tree_previous, nu_traces=num_traces)
                drift = None

            # CREATE DRIFT INFO INSTANCE
            if drift:
                drift_times = extract_change_moments_to_list(event_log)
                drift_input = [log_name, drift_id, 'control-flow', drift, drift_times, added_acs, deleted_acs, moved_acs, tree_list]
                drift_instance = initialize_drift_instance_from_list(drift_input)
                event_log.attributes[InfoTypes.drift_info.value] = drift_instance.drift_info_to_dict()
                collection.add_drift(drift_instance)


        # ADD TIME PERSPECTIVE TO EVENT LOG
        add_duration_to_log(event_log,
                            select_random(par.Timestamp_first_trace),
                            select_random(par.Trace_exp_arrival_sec, option='uniform_int'),
                            select_random(par.Task_exp_duration_sec, option='uniform_int'))

        # # ADD NOISE and CREATE NOISE INFO INSTANCE
        # noise = select_random(par.Noise, option='random')
        # if noise:
        #     event_log = insert_noise(event_log, par.Noisy_trace_prob[0], par.Noisy_event_prob[0])
        #     noise_instance = NoiseInfo(log_name, par.Noisy_trace_prob[0], par.Noisy_event_prob[0])
        #     collection.add_noise(noise_instance)
        #     event_log.attributes[InfoTypes.noise_info.value] = noise_instance.noise_info_to_dict()
        #


        # EXPORT GENERATED LOG
        xes_exporter.apply(event_log, os.path.join(out_folder, log_name))

    collection._temp_save_drift_info_to_csv_file(path=out_folder)
    print('Finished generating collection of', number_of_logs, 'logs in', out_folder)


class InfoTypes(Enum):
    drift_info = "drift:info"
    noise_info = "noise:info"



class DriftTypes(Enum):
    sudden = 'sudden'
    gradual = 'gradual'
    recurring = 'recurring'
    incremental = 'incremental'


def get_parameters(path: str = config.PAR_LOG_COLLECTION):
    parameters_dict = create_dict_with_input_parameters(path)
    parameters = InputParameters(**parameters_dict)
    return parameters


def generate_initial_tree(complexity_options_list: list, file_path_to_own_models):
    complexity = select_random(complexity_options_list, option='random')
    if file_path_to_own_models is None:
        generated_process_tree = generate_specific_trees(complexity)
    else:
        generated_process_tree = generate_tree_from_file(file_path_to_own_models)
    return generated_process_tree, complexity


def select_random(data: list, option: str = 'random') -> any:
    if len(data) == 1:
        data_selected = data[0]
    elif len(data) == 2 and option == 'uniform':
        data_selected = uniform(data[0], data[1])
    elif len(data) == 2 and option == 'uniform_int':
        data_selected = randint(data[0], data[1])
    elif option == 'random':
        data_selected = data[randint(0, len(data) - 1)]
    else:
        data_selected = None
        Warning(f"Check function 'select_random' call: {data, option, data_selected}")

    if isinstance(data, float):
        data_selected = round(data_selected, 2)

    return data_selected


def creat_output_folder(path: str = config.DEFAULT_LOG_COLLECTION_OUTPUT_DIR):
    out_folder = os.path.join(path, str(int(time.time())))
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    return out_folder


def drift_area_selection(data: list, option: float = 0.2) -> any:
    data_length = data[1] - data[0]
    drift_area_one = round(uniform(data[0], (data[0] + (1 - option) * data_length)), 2)
    drift_area_two = round(uniform(drift_area_one + data_length * option, data[1]), 2)

    return drift_area_one, drift_area_two


def create_dict_with_input_parameters(par_file_name: str):
    """ Getting parameters from the text file 'parameters_log_collection' placed in the folder 'Data/parameters'
    :return: parameters for the generation of a set of event logs
    """

    parameter_doc = open(f'{config.DEFAULT_PARAMETER_DIR}/{par_file_name}', 'r')
    parameters_input = parameter_doc.read()
    parameter_doc.close()
    parameters_dict = {}
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


def initialize_drift_instance_from_list(input: list):
    log_id, drift_id, perspective, drift_type, drift_time, added, deleted, moved, trees = input

    drift_instance = DriftInfo()
    if drift_type:
        drift_instance.log_id = log_id
        drift_instance.drift_id = drift_id
        drift_instance.process_perspective = perspective
        drift_instance.drift_type = drift_type
        drift_instance.drift_time = drift_time
        drift_instance.activities_added = added
        drift_instance.activities_deleted = deleted
        drift_instance.activities_moved = moved
        drift_instance.process_trees = trees

    return drift_instance


def main():
    if len(sys.argv) == 1:
        generate_logs()
    elif len(sys.argv) == 2:
        generate_logs(sys.argv[1])


if __name__ == '__main__':
    main()
