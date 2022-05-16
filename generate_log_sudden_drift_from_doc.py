import copy
import datetime
import os
import sys

from ConceptDrifts.sudden_drift import sudden_drift
from controllers.control_flow_controller import evolve_tree_randomly
from controllers.event_log_controller import add_duration_to_log, get_timestamp_log
from controllers.noise_controller import add_noise_doc
from controllers.process_tree_controller import generate_specific_trees, generate_tree_from_file
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
import time

out_folder = 'data/generated_logs'

def generate_log_with_sudden_drift(file_path_one=None, file_path_two=None):
    """ Generation of an event log with a sudden drift

    :param file_path_one: file path to own process model, if desired to be used
    :param file_path_two: file path to second own process model, if desired to be used
    :return: event log with sudden drift saved in out_file
    """
    out_file = os.path.join(out_folder, 'param_log_sudden_' + str(int(time.time())) + '.xes')

    tree_complexity, date, min_sec, max_sec, num_traces, change_point, proportion_random_evolution, start_sector_noise, end_sector_noise, proportion_noise_in_sector, type_noise = get_parameters()
    deleted_acs = []
    added_acs = []
    moved_acs = []
    if file_path_one is None:
        tree_one = generate_specific_trees(tree_complexity.strip())
        drift_tree = copy.deepcopy(tree_one)
        tree_two, deleted_acs, added_acs, moved_acs = evolve_tree_randomly(drift_tree, proportion_random_evolution)
    elif file_path_one is not None and file_path_two is None:
        tree_one = generate_tree_from_file(file_path_one)
        drift_tree = copy.deepcopy(tree_one)
        tree_two, deleted_acs, added_acs, moved_acs = evolve_tree_randomly(drift_tree, proportion_random_evolution)
    else:
        tree_one = generate_tree_from_file(file_path_one)
        tree_two = generate_tree_from_file(file_path_two)
    event_log = sudden_drift(tree_one, tree_two, num_traces, change_point)
    if start_sector_noise is None:
        add_duration_to_log(event_log, date, min_sec, max_sec)
    else:
        event_log = add_noise_doc(event_log, tree_one, proportion_noise_in_sector, type_noise, start_sector_noise,
                                  end_sector_noise)
        add_duration_to_log(event_log, date, min_sec, max_sec)
    start_drift = get_timestamp_log(event_log, num_traces, change_point)
    if file_path_two is None:
        drift_data = "perspective: control-flow; type: sudden; drift_moment: "+str(start_drift)+" (" + str(change_point) + "); activities_added: "+str(added_acs)+"; activities_deleted: "+str(deleted_acs)+"; activities_moved: "+str(moved_acs)
    else:
        drift_data = "perspective: control-flow; type: sudden; drift_moment: "+str(start_drift)+" (" + str(change_point) + ")"
    event_log.attributes['drift_info:'] = drift_data
    if start_sector_noise is not None:
        start_noise = get_timestamp_log(event_log, num_traces, start_sector_noise)
        end_noise = get_timestamp_log(event_log, num_traces, end_sector_noise)
        noise_data = "noise proportion: "+str(proportion_noise_in_sector) + "; start point: " + str(start_noise) + " (" + str(start_sector_noise) + "); end point: " + str(end_noise) + " (" + str(end_sector_noise) + "); noise type: "+type_noise
        event_log.attributes['noise info:'] = noise_data
    xes_exporter.apply(event_log, out_file)
    print('exported log to', out_file)

def get_parameters():
    """ Getting parameters from the text file 'parameters_sudden_drift' placed in the folder 'Data/parameters'

    :return: parameters for the generation of an event log with a sudden drift
    """
    doc = open('Data/parameters/parameters_sudden_drift', 'r')
    one = doc.readline().split(' ')[1]
    tree_complexity = one[0:len(one) - 1]
    dates = doc.readline().split(' ')
    date = datetime.datetime.strptime(dates[1] + " " + dates[2][0:len(dates[2]) - 1], '%y/%d/%m %H:%M:%S')
    min_sec = int(doc.readline().split(' ')[1])
    max_sec = int(doc.readline().split(' ')[1])
    nu_traces = int(doc.readline().split(' ')[1])
    change_point = float(doc.readline().split(' ')[1])
    proportion_random_evolution = float(doc.readline().split(' ')[1])
    one = doc.readline().split(' ')[1]
    if one == 'None\n':
        start_sector_noise = None
        end_sector_noise = None
        proportion_noise_in_sector = None
        type_noise = None
    else:
        start_sector_noise = float(one[0:len(one) - 1])
        one = doc.readline().split(' ')[1]
        end_sector_noise = float(one[0:len(one) - 1])
        one = doc.readline().split(' ')[1]
        proportion_noise_in_sector = float(one[0:len(one) - 1])
        one = doc.readline().split(' ')[1]
        type_noise = one[0:len(one) - 1]
    return tree_complexity, date, min_sec, max_sec, nu_traces, change_point, proportion_random_evolution, start_sector_noise, end_sector_noise, proportion_noise_in_sector, type_noise


def main():
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    if len(sys.argv) == 1:
        generate_log_with_sudden_drift()
    elif len(sys.argv) == 2:
        generate_log_with_sudden_drift(sys.argv[1])
    else:
        generate_log_with_sudden_drift(sys.argv[1], sys.argv[2])


if __name__ == '__main__':
    main()
