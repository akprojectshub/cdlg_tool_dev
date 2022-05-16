import copy
import datetime
import csv
import os
import sys
from random import randint, uniform

from ConceptDrifts.gradual_drift import gradual_drift
from ConceptDrifts.incremental_drift import incremental_drift_gs
from ConceptDrifts.recurring_drift import recurring_drift
from ConceptDrifts.sudden_drift import sudden_drift
from controllers.control_flow_controller import evolve_tree_randomly
from controllers.event_log_controller import add_duration_to_log, get_timestamp_log
from controllers.noise_controller import add_noise_gs
from controllers.process_tree_controller import generate_tree_from_file, generate_specific_trees
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.process_tree.exporter import exporter as ptml_exporter
import time

def generate_logs(file_path_one=None):
    """ Generation of a set of event logs with different drifts, a corresponding CSV file and respective text files

    :param file_path_one: file path to own process model, if desired to be used
    :return: collection of event logs with drifts saved in out_folder
    """
    out_folder = 'data/generated_collections/' + str(int(time.time()))
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    tree_complexity, num_logs, num_traces, drifts, drift_area, proportion_random_evolution, noise, date, min_sec, max_sec = get_parameters()
    if file_path_one is None:
        tree_one = generate_specific_trees(tree_complexity.strip())
    else:
        tree_one = generate_tree_from_file(file_path_one)
    print('Generating', num_logs, 'logs')
    with open(os.path.join(out_folder, "collection_info.csv"), 'w', newline='') as log_file:
        writer = csv.writer(log_file)
        writer.writerow(["Event Log", "Drift Perspective", "Drift Type", "Drift Specific Information", "Drift Start Timestamp", "Drift End Timestamp", "Noise Proportion", "Activities Added", "Activities Deleted", "Activities Moved"])
        for i in range(num_logs):
            parameters = "number of traces: "+str(num_traces)
            drift = drifts[randint(0, len(drifts)-1)].strip()
            drift_area_one = round(uniform(float(drift_area[0].strip()), (float(drift_area[0].strip())+0.8*(float(drift_area[1].strip())-float(drift_area[0].strip())))), 2)
            drift_area_two = round(uniform(drift_area_one + (float(drift_area[1].strip())-float(drift_area[0].strip())) * 0.2, float(drift_area[1].strip())), 2)
            if len(proportion_random_evolution) == 1:
                ran_evolve = round(float(proportion_random_evolution[0].strip()), 2)
            else:
                ran_evolve = round(uniform(float(proportion_random_evolution[0].strip()), float(proportion_random_evolution[1].strip())), 2)
            drift_tree = copy.deepcopy(tree_one)
            if drift != 'incremental':
                tree_two, deleted_acs, added_acs, moved_acs = evolve_tree_randomly(drift_tree, ran_evolve)
            if drift == 'sudden':
                event_log = sudden_drift(tree_one, tree_two, num_traces, drift_area_one)
                parameters += "; drift: sudden; change point: "+str(drift_area_one) + "; random evolution: "+str(ran_evolve)
                dr_s = "N/A"
            elif drift == 'gradual':
                ra = randint(0, 1)
                if ra == 0:
                    gr_type = 'linear'
                    dr_s = 'linear distribution'
                else:
                    gr_type = 'exponential'
                    dr_s = 'exponential distribution'
                event_log = gradual_drift(tree_one, tree_two, num_traces, drift_area_one, drift_area_two, gr_type)
                parameters += "; drift: gradual; start point: "+str(drift_area_one)+"; end point: "+str(drift_area_two)+"; distribution: "+gr_type + "; random evolution: "+str(ran_evolve)
            elif drift == 'recurring':
                ran_odd = [1, 3, 5]
                pro_first = round(uniform(0.3, 0.7), 2)
                if drift_area_one > 0 and drift_area_two != 1:
                    ra = randint(0, 2)
                    sea_cha = ran_odd[ra]
                    dr_s = str(sea_cha)+" seasonal changes"
                else:
                    sea_cha = randint(1, 6)
                    dr_s = str(sea_cha)+" seasonal changes"
                event_log = recurring_drift(tree_one, tree_two, num_traces, sea_cha, pro_first, drift_area_one, drift_area_two)
                parameters += "; drift: recurring; start point: "+str(drift_area_one)+"; end point: "+str(drift_area_two)+"; seasonal changes: "+str(sea_cha)+"; proportion initial version: "+str(pro_first) + "; random evolution: "+str(ran_evolve)
            elif drift == 'incremental':
                num_models = randint(2, 5)
                ran_in_evolve = round(ran_evolve/num_models, 2)
                event_log, deleted_acs, added_acs, moved_acs = incremental_drift_gs(tree_one, drift_area_one, drift_area_two, num_traces, num_models, ran_in_evolve)
                dr_s = str(num_models+1) + " versions of the process model"
                parameters += "; drift: incremental; start point: "+str(drift_area_one)+"; end point: "+str(drift_area_two) + "; number evolving versions: " + str(num_models) + "; random evolution per model: "+str(ran_in_evolve)
            noise_prop = 0
            noise_ha = True
            if noise != 0:
                noise_prop = round(uniform(float(noise[0].strip()), float(noise[1].strip())), 4)
                if noise_prop != 0:
                    ran_no = randint(0, 1)
                    if ran_no == 0:
                        event_log, noise_ha = add_noise_gs(event_log, tree_one, noise_prop, 'changed_model', 0, 1)
                    else:
                        event_log, noise_ha = add_noise_gs(event_log, tree_one, noise_prop, 'random_model', 0, 1)
            if not noise_ha:
                noise_prop = 0.0
            add_duration_to_log(event_log, date, min_sec, max_sec)
            start_drift = get_timestamp_log(event_log, num_traces, drift_area_one)
            if drift == 'sudden':
                end_drift = "N/A"
            else:
                end_drift = str(get_timestamp_log(event_log, num_traces, drift_area_two)) + " (" + str(drift_area_two) + ")"
            data = "event log: "+"event_log_"+str(i)+"; perspective: control-flow; type: "+drift+"; specific_information: "+dr_s+"; drift_start: "+str(start_drift) + " (" + str(drift_area_one) + "); drift_end: " + end_drift + "; noise_level: " + str(noise_prop) + "; activities_added: " + str(added_acs) + "; activities_deleted: " + str(deleted_acs) + "; activities_moved: " + str(moved_acs)
            event_log.attributes['drift info'] = data
            xes_exporter.apply(event_log, os.path.join(out_folder, "log_"+str(i)+".xes"))
            writer.writerow(["event_log_"+str(i), "control-flow", drift, dr_s, start_drift, end_drift, noise_prop, added_acs, deleted_acs, moved_acs])
            file_object = open(os.path.join(out_folder, "log_"+str(i)+".txt"), 'w')
            file_object.write("--- USED PARAMETERS ---\n")
            file_object.write(parameters+"\n\n")
            file_object.write("--- DRIFT INFORMATION ---\n")
            file_object.write(data)
            file_object.close()
    ptml_exporter.apply(tree_one, os.path.join(out_folder, "initial_version.ptml"))
    print('Finished generating collection of', num_logs, 'logs in', out_folder)


def get_parameters():
    """ Getting parameters from the text file 'parameters_logs' placed in the folder 'Data/parameters'

    :return: parameters for the generation of a set of event logs
    """
    doc = open('data/parameters/parameters_log_collection', 'r')
    one = doc.readline().split(' ')[1]
    tree_complexity = one[0:len(one) - 1]
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
    dates = doc.readline().split(' ')
    date = datetime.datetime.strptime(dates[1] + " " + dates[2][0:len(dates[2]) - 1], '%y/%d/%m %H:%M:%S')
    min_sec = int(doc.readline().split(' ')[1])
    max_sec = int(doc.readline().split(' ')[1])
    return tree_complexity, num_logs, num_traces, drifts, drift_area, proportion_random_evolution, noise, date, min_sec, max_sec


def main():
    if len(sys.argv) == 1:
        generate_logs()
    elif len(sys.argv) == 2:
        generate_logs(sys.argv[1])


if __name__ == '__main__':
    main()
