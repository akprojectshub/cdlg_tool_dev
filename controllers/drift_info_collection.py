from dataclasses import dataclass, fields, field
import datetime
import glob, os
import pandas as pd
import numpy as np
import pandas as pd
import pm4py
from collections import defaultdict
from copy import deepcopy

@dataclass
class DriftInfo:
    log_id: str = str
    drift_id: int = np.NAN
    process_perspective: str = 'none'
    drift_type: str = 'none'
    drift_time: list = list
    activities_added: list = list
    activities_deleted: list = list
    activities_moved: list = list
    process_trees: dict = field(default_factory=lambda: defaultdict(dict))
    change_info: dict = field(default_factory=lambda: defaultdict(dict))

    def set_log_id(self, log_name):
        self.log_id = log_name
        return None

    def set_drift_id(self, drift_id):
        self.drift_id = drift_id
        return None

    def set_drift_type(self, drift_type):
        self.drift_type = drift_type
        return None

    def add_process_tree(self, process_tree):
        process_tree_id = str(len(self.process_trees))
        self.process_trees[process_tree_id] = deepcopy(process_tree)
        return None

    def add_change_info(self, change_trace_index, change_type, tree_previous, tree_new, deleted_acs, added_acs,
                        moved_acs):
        change_id = str(len(self.change_info))
        self.change_info[change_id] = {'change_type': change_type,
                                       'change_trace_index': change_trace_index,
                                       'process_tree_before': tree_previous,
                                       'process_tree_after': tree_new,
                                       'activities_deleted': deleted_acs,
                                       'activities_added': added_acs,
                                       'activities_moved': moved_acs}
        return None


    def get_previous_process_tree(self):
        max_process_tree_id = str(max([int(key) for key in self.process_trees.keys()]))
        previous_process_tree = deepcopy(self.process_trees[max_process_tree_id])
        return previous_process_tree


def drift_info_to_dict(self):
    DI = vars(self)
    keys_list = list(DI.keys())
    values_list = list(DI.values())
    # TODO@Zied: please do not use methods starting with _ or __
    type_list = [type(i).__name__ for i in DI.values()]
    d = dict()
    d["value"] = True  ## By default need to add this as a parameter

    d_final = {"value": True, "children": {}}

    for i in range(0, len(type_list)):
        if type_list[i] == 'list':
            d[keys_list[i]] = {keys_list[i] + "_" + str(j + 1): values_list[i][j] for j in
                               range(0, len(values_list[i]))}
            d_final["children"][keys_list[i]] = {"value": values_list[i], "children": d[keys_list[i]]}

        elif type_list[i] != 'list':
            d[keys_list[i]] = values_list[i]
            d_final["children"][keys_list[i]] = values_list[i]

    return d_final


@staticmethod
def extract_info_xes(log):
    d = dict()
    xes = log.attributes["drift:info"]["children"]

    for key, value in xes.items():
        if value == 0 and key != "drift_id":
            d[key] = []
        # TODO@Zied: please do not use methods starting with _ or __
        elif (type(value).__name__ != 'dict'):
            d[key] = value
        else:
            d[key] = list(value["children"].values())
    return d


@dataclass
class NoiseInfo:
    """
        Object for keeping information about added noise to a generated event log
    """
    log_id: str = str
    noisy_trace_prob: float = np.NAN
    noisy_event_prob: float = np.NAN

    def noise_info_to_dict(self):
        NI = vars(self)
        keys_list = list(NI.keys())
        values_list = list(NI.values())
        # TODO@Zied: please do not use methods starting with _ or __
        type_list = [type(i).__name__ for i in NI.values()]
        d = dict()
        d["value"] = True  ## By default need to add this as a parameter

        d_final = {"value": True, "children": {}}

        for i in range(0, len(type_list)):
            if type_list[i] == 'list':
                d[keys_list[i]] = {keys_list[i] + "_" + str(j): values_list[i][j] for j in
                                   range(0, len(values_list[i]))}
                d_final["children"][keys_list[i]] = {"value": len(values_list[i]), "children": d[keys_list[i]]}

            elif type_list[i] != 'list':
                d[keys_list[i]] = values_list[i]
                d_final["children"][keys_list[i]] = values_list[i]
        return d_final

    @staticmethod
    def extract_info_xes(log):
        d = dict()
        xes = log.attributes["noise:info"]["children"]

        for key, value in xes.items():
            if value == 0 and key != "drift_id":
                d[key] = []
            # TODO@Zied: please do not use methods starting with _ or __
            elif (type(value).__name__ != 'dict'):
                d[key] = value
            else:
                d[key] = list(value["children"].values())
        return d


@dataclass
class LogDriftInfo:
    """
    Object for keeping information about added drift and noise instances for a generated event log
    """
    drifts = list()
    noise = list()
    number_of_drifts: int = 0
    number_of_noises: int = 0

    def add_drift(self, instance: DriftInfo):
        self.drifts.append(instance)
        self.increase_drift_count()

    def add_noise(self, instance: NoiseInfo):
        self.noise.append(instance)
        self.increase_noise_count()

    def increase_drift_count(self):
        self.number_of_drifts += 1

    def increase_noise_count(self):
        self.number_of_noises += 1

    def fill_drift_log(
            self):  # This method is used to store the dictionary with log attribute levels in the log (xes file)
        param_drift = vars(DriftInfo)

    def extract_drift_and_noise_info(self, path):

        loaded_event_logs = self.load_log_names_and_paths(path)
        for log_name, log_folder in loaded_event_logs.items():
            log = pm4py.read_xes(os.path.join(log_folder, log_name))
            DI = DriftInfo.extract_info_xes(log)
            NI = NoiseInfo.extract_info_xes(log)
            self.drifts.append(DI)
            self.increase_drift_count()
            self.noise.append(NI)
            self.increase_noise_count()

        return self

    @staticmethod
    def load_log_names_and_paths(path):
        loaded_event_logs = {}
        for dir_path, dir_names, filenames in os.walk(path):
            for index, filename in enumerate(filenames):
                if filename.endswith('.xes'):
                    loaded_event_logs[filename] = os.sep.join([dir_path])
        return loaded_event_logs

    def _temp_save_drift_info_to_csv_file(self, path):
        # TODO: this is a temporal function that needs to be revised and checked
        dict_nested = dict()
        for drift in self.drifts:
            for attr, value in vars(drift).items():
                if attr != 'log_id' and attr != 'drift_id':
                    if isinstance(value, list):
                        temp_dict = {}
                        for i, v in enumerate(value):
                            temp_dict[str(i + 1)] = v
                        dict_nested[drift.log_id, drift.drift_id, attr] = temp_dict
                    else:
                        dict_nested[drift.log_id, drift.drift_id, attr] = {'1': value}

        flat_file = []
        for key, values in dict_nested.items():
            for k, v in values.items():
                data = list(key)
                data.extend([k, v])
                flat_file.append(data)

        df = pd.DataFrame(flat_file, columns=['log_name', 'drift_id', 'attribute', 'attribute_value', 'value'])
        df.to_csv(f"{path}/aggregated_drift_info.csv", index=False)

        return None


def extract_change_moments_to_dict(created_log):
    change_moments = {}
    current_model_version = created_log[0].attributes['model:version']
    change_id = 0
    for trace in created_log:
        change_moment = trace[0]['time:timestamp']
        version = trace.attributes['model:version']
        if version != current_model_version:
            change_id += 1
            change_moments['change_' + str(change_id)] = change_moment  # .strftime("%Y-%m-%d, %H:%M:%S")
            current_model_version = version
    return {"value": "timestamps", "children": change_moments}


def extract_change_moments_to_list(created_log):
    change_moments = []
    current_model_version = created_log[0].attributes['model:version']
    change_id = 0
    for trace in created_log:
        change_moment = trace[0]['time:timestamp']
        version = trace.attributes['model:version']
        if version != current_model_version:
            change_id += 1
            change_moments.append(change_moment)  # .strftime("%Y-%m-%d, %H:%M:%S"))
            current_model_version = version
    return change_moments
