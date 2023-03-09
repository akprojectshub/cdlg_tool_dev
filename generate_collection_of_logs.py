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
from concept_drifts.recurring_drift import recurring_drift
from concept_drifts.sudden_drift import sudden_drift
from concept_drifts.without_drift import no_drift
from controllers.control_flow_controller import evolve_tree_randomly
from controllers.event_log_controller import add_duration_to_log, get_timestamp_log
from controllers.noise_controller_new import insert_noise
from controllers.drift_info_collection import DriftInfo
from controllers.drift_info_collection import NoiseInfo
from controllers.drift_info_collection import LogDriftInfo
from controllers.process_tree_controller import generate_tree_from_file, generate_specific_trees
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.process_tree.exporter import exporter as ptml_exporter
from controllers.drift_info_xes_file import store_drift
from controllers.drift_info_xes_file import store_noise
from controllers.input_parameters import InputParameters
import time


def generate_logs(file_path_to_own_models=None):
    """ Generation of a set of event logs with different drifts, a corresponding CSV file and respective text files
    :param file_path_to_own_models: file path to own process model, if desired to be used
    :return: collection of event logs with drifts saved in out_folder
    """

    # CREATE DIR TO STORE GENERATED LOGS
    out_folder = os.path.join(config.DEFAULT_LOG_COLLECTION_OUTPUT_DIR, str(int(time.time())))
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    # READE PARAMETERS FROM A FILE
    parameters_dict = get_parameters(config.PAR_LOG_COLLECTION)
    par = InputParameters(**parameters_dict)

    # MAIN LOOP
    print('Generating', par.Number_event_logs[0], 'logs')
    collection = LogDriftInfo()
    for i in range(par.Number_event_logs[0]):

        tree_one, complexity = generate_initial_tree(par.Complexity_random_tree, file_path_to_own_models)
        drift = select_random(par.Drifts, option='random')
        drift_area_one, drift_area_two = drift_area_selection(par.Drift_area)
        ran_evolve = select_random(par.Proportion_random_evolution_sector, option='uniform')
        drift_tree = copy.deepcopy(tree_one)
        if drift.casefold() != 'incremental':
            tree_two, deleted_acs, added_acs, moved_acs = evolve_tree_randomly(drift_tree, ran_evolve)
        if drift.casefold() == 'sudden':
            event_log = sudden_drift(tree_one, tree_two, par.Number_traces_per_event_log, drift_area_one)
        elif drift.casefold() == 'gradual':

            # ra = randint(0, 1)
            # if ra == 0:
            #     gr_type = 'linear'
            # else:
            #     gr_type = 'exponential'
            #
            # event_log = gradual_drift(tree_one, tree_two, par.Number_traces_per_event_log[0], drift_area_one, drift_area_two, gr_type)

            gr_type = select_random(par.GRADUAL_DRIFT_TYPE, option='random')
            event_log = gradual_drift(tree_one, tree_two, par.Number_traces_per_event_log[0], drift_area_one, drift_area_two, gr_type)

        elif drift.casefold() == 'recurring':
            ran_odd = [1, 3, 5]
            pro_first = round(uniform(0.3, 0.7), 2)
            if drift_area_one > 0 and drift_area_two != 1:
                ra = randint(0, 2)
                sea_cha = ran_odd[ra]
            else:
                sea_cha = randint(1, 6)
            event_log = recurring_drift(tree_one, tree_two, par.Number_traces_per_event_log[0], sea_cha, pro_first, drift_area_one,
                                        drift_area_two)

        elif drift.casefold() == 'incremental':
            num_models = randint(2, 5)
            ran_in_evolve = round(ran_evolve / num_models, 2)
            event_log, deleted_acs, added_acs, moved_acs = incremental_drift_gs(tree_one, drift_area_one,
                                                                                drift_area_two, par.Number_traces_per_event_log[0],
                                                                                num_models, ran_in_evolve)
        elif drift.casefold() == 'none':
            event_log = no_drift(tree=tree_one, nu_traces=par.Number_traces_per_event_log[0])

        # ADD NOISE
        if par.Noise:
            event_log = insert_noise(event_log, par.Noisy_trace_prob[0], par.Noisy_event_prob[0])

        # ADD TIMESTAMPS
        add_duration_to_log(event_log, par.Timestamp_first_trace[0], par.Trace_exp_arrival_sec[0], par.Task_exp_duration_sec[0])

        # CREATE DRIFT INFO INSTANCE
        start_drift = get_timestamp_log(event_log, par.Number_traces_per_event_log[0], drift_area_one)
        if drift == 'sudden':
            end_drift = "N/A"
        else:
            end_drift = str(
                get_timestamp_log(event_log, par.Number_traces_per_event_log[0], drift_area_two)) + " (" + str(
                drift_area_two) + ")"

        if drift.casefold() != "none": #if there is a drift
            DI = DriftInfo(str(i), collection.number_of_drifts, "control-flow", drift, [start_drift, end_drift], added_acs, deleted_acs, moved_acs)
        collection.add_drift(DI)
        collection.increase_drift_count()
        event_log.attributes["drift:info"] = DI.drift_info_to_dict()

        # TODO: CREATE NOISE INFO INSTANCE


        # EXPORT GENERATED LOG
        xes_exporter.apply(event_log, os.path.join(out_folder, "log_"+str(i)+".xes"))
    print('Finished generating collection of', par.Number_event_logs[0], 'logs in', out_folder)


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
    drift_area_one = round(uniform(data[0], (data[0] + (1-option) * data_length)), 2)
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