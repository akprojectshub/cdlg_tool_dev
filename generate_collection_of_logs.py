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

    out_folder = 'data/generated_collections/' + str(int(time.time()))
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    parameters_dict = get_parameters(config.PAR_LOG_COLLECTION)
    par = InputParameters(**parameters_dict)

    print('Generating', par.Number_event_logs[0], 'logs')
    with open(os.path.join(out_folder, "collection_info.csv"), 'w', newline='') as log_file:
        writer = csv.writer(log_file)
        writer.writerow(["Event Log", "Drift Perspective", "Complexity", "Drift Type", "Drift Specific Information",
                         "Drift Start Timestamp", "Drift End Timestamp", "Noise Proportion", "Activities Added",
                         "Activities Deleted", "Activities Moved"])
        collection = LogDriftInfo()
        for i in range(par.Number_event_logs[0]):
            parameters_str = "number of traces: " + str(par.Number_traces_per_event_log)

            complexity = par.Complexity_random_tree[randint(0, len(par.Complexity_random_tree) - 1)]  # New Line
            if file_path_to_own_models is None:
                tree_one = generate_specific_trees(complexity.strip())
            else:
                tree_one = generate_tree_from_file(file_path_to_own_models)
            print("The generated tree will have a " + complexity + " complexity")  # New line

            drift = par.Drifts[randint(0, len(par.Drifts) - 1)].strip()
            drift_area_one = round(uniform(par.Drift_area[0], (par.Drift_area[0] + 0.8 * (par.Drift_area[1] - par.Drift_area[0]))), 2)
            drift_area_two = round(uniform(drift_area_one + (par.Drift_area[1] - par.Drift_area[0]) * 0.2, par.Drift_area[1]), 2)
            if len(par.Proportion_random_evolution_sector) == 1:
                ran_evolve = round(float(par.Proportion_random_evolution_sector[0]), 2)
            else:
                ran_evolve = round(uniform(float(par.Proportion_random_evolution_sector[0]),
                                           float(par.Proportion_random_evolution_sector[1])), 2)
            drift_tree = copy.deepcopy(tree_one)
            if drift.casefold() != 'incremental':
                tree_two, deleted_acs, added_acs, moved_acs = evolve_tree_randomly(drift_tree, ran_evolve)
            if drift.casefold() == 'sudden':
                event_log = sudden_drift(tree_one, tree_two, par.Number_traces_per_event_log, drift_area_one)
                parameters_str += "; drift: sudden; change point: " + str(drift_area_one) + "; random evolution: " + str(
                    ran_evolve)
                dr_s = "N/A"
            elif drift.casefold() == 'gradual':
                ra = randint(0, 1)
                if ra == 0:
                    gr_type = 'linear'
                    dr_s = 'linear distribution'
                else:
                    gr_type = 'exponential'
                    dr_s = 'exponential distribution'
                event_log = gradual_drift(tree_one, tree_two, par.Number_traces_per_event_log[0], drift_area_one, drift_area_two, gr_type)
                parameters_str += "; drift: gradual; start point: " + str(drift_area_one) + "; end point: " + str(
                    drift_area_two) + "; distribution: " + gr_type + "; random evolution: " + str(ran_evolve)
            elif drift.casefold() == 'recurring':
                ran_odd = [1, 3, 5]
                pro_first = round(uniform(0.3, 0.7), 2)
                if drift_area_one > 0 and drift_area_two != 1:
                    ra = randint(0, 2)
                    sea_cha = ran_odd[ra]
                    dr_s = str(sea_cha) + " seasonal changes"
                else:
                    sea_cha = randint(1, 6)
                    dr_s = str(sea_cha) + " seasonal changes"
                event_log = recurring_drift(tree_one, tree_two, par.Number_traces_per_event_log[0], sea_cha, pro_first, drift_area_one,
                                            drift_area_two)
                parameters_str += "; drift: recurring; start point: " + str(drift_area_one) + "; end point: " + str(
                    drift_area_two) + "; seasonal changes: " + str(sea_cha) + "; proportion initial version: " + str(
                    pro_first) + "; random evolution: " + str(ran_evolve)
            elif drift.casefold() == 'incremental':
                num_models = randint(2, 5)
                ran_in_evolve = round(ran_evolve / num_models, 2)
                event_log, deleted_acs, added_acs, moved_acs = incremental_drift_gs(tree_one, drift_area_one,
                                                                                    drift_area_two, par.Number_traces_per_event_log[0],
                                                                                    num_models, ran_in_evolve)
                dr_s = str(num_models + 1) + " versions of the process model"
                parameters_str += "; drift: incremental; start point: " + str(drift_area_one) + "; end point: " + str(
                    drift_area_two) + "; number evolving versions: " + str(
                    num_models) + "; random evolution per model: " + str(ran_in_evolve)
            elif drift.casefold() == 'none':
                event_log = no_drift(tree=tree_one, nu_traces=par.Number_traces_per_event_log[0])
                parameters_str += "; drift: None; change point: None; random evolution: None"
                dr_s = "no drift"



            # Add noise
            if par.Noise:
                event_log = insert_noise(event_log, par.Noisy_trace_prob[0], par.Noisy_event_prob[0])

            # Add timestamps to an event log
            add_duration_to_log(event_log, par.Timestamp_first_trace[0], par.Trace_exp_arrival_sec[0], par.Task_exp_duration_sec[0])




            # Create an instance with drift info
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

            # TODO: Create an instance with drift info


            # Export generated event log
            xes_exporter.apply(event_log, os.path.join(out_folder, "log_"+str(i)+".xes"))


            # if drift.casefold() != 'none':
            #     data = "event log: "+"event_log_"+str(i)+"; Complexity:"+str(complexity)+"; perspective: control-flow; type: "+drift+"; specific_information: "+dr_s+"; drift_start: "+str(start_drift) + " (" + str(drift_area_one) + "); drift_end: " + str(end_drift) + "; activities_added: " + str(added_acs) + "; activities_deleted: " + str(deleted_acs) + "; activities_moved: " + str(moved_acs)
            # elif drift.casefold() == 'none':
            #     # set parameters to none, since no drift was specified
            #     data = "event log: "+"event_log_"+str(i)+"; Complexity:"+str(complexity)+"; perspective: control-flow; type: "+drift+"; specific_information: "+dr_s+"; drift_start: None; drift_end: None;" + "activities_added: None; activities_deleted: None; activities_moved: None"
            #     start_drift, end_drift, added_acs, deleted_acs, moved_acs = "None", "None", "None", "None", "None"
            #

            # writer.writerow(["event_log_"+str(i), "control-flow", complexity, drift, dr_s, start_drift, end_drift, added_acs, deleted_acs, moved_acs])
            # file_object = open(os.path.join(out_folder, "log_"+str(i)+".txt"), 'w')
            # file_object.write("--- USED PARAMETERS ---\n")
            # file_object.write(parameters_str+"\n\n")
            # file_object.write("--- DRIFT INFORMATION ---\n")
            # file_object.write(data)
            # file_object.close()
        ptml_exporter.apply(tree_one, os.path.join(out_folder, "initial_version.ptml"))
        print('Finished generating collection of', par.Number_event_logs, 'logs in', out_folder)







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

    # If list has only one value, return it
    # for key, value in parameters_dict.items():
    #     if len(value) == 1:
    #         parameters_dict[key] = value[0]


    return parameters_dict


def get_parameters_old():
    """ Getting parameters from the text file 'parameters_log_collection' placed in the folder 'Data/parameters'
    :return: parameters for the generation of a set of event logs
    """
    doc = open('data/parameters/parameters_log_collection', 'r')
    one = doc.readline().split(' ')[1]
    tree_complexity = one[0:len(one) - 1].split(";")  ## new added line
    num_logs = int(doc.readline().split(' ')[1])
    num_traces = int(doc.readline().split(' ')[1])
    one = doc.readline().split(' ')[1]
    drifts = one[0:len(one) - 1].split(';')
    drift_area = doc.readline().split(' ')[1].split('-')
    proportion_random_evolution = doc.readline().split(' ')[1].split('-')
    nos = doc.readline().split(' ')[1]
    if nos.strip() == 'None' or nos.strip() == '0':
        noise = 0
    else:
        noise = nos.split('-')

    return tree_complexity, num_logs, num_traces, drifts, drift_area, proportion_random_evolution, noise



# class AttrDict(dict):
#     """Provide dictionary with items accessible as object attributes."""
#     def __getattr__(self, attr: str) -> any:
#         try:
#             return self[attr]
#         except KeyError as exception:
#             raise AttributeError(f'AttrDict has no key {attr!r}') from exception
#
#     def __setattr__(self, attr: str, value: any) -> None:
#         self[attr] = value
#
#     def __delattr__(self, attr: str) -> any:
#         try:
#             del self[attr]
#         except KeyError as exception:
#             raise AttributeError(f'AttrDict has no key {attr!r}') from exception




def main():
    if len(sys.argv) == 1:
        generate_logs()
    elif len(sys.argv) == 2:
        generate_logs(sys.argv[1])


if __name__ == '__main__':
    main()