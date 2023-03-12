from dataclasses import dataclass, fields
import datetime
import glob, os

import numpy as np
import pm4py


@dataclass
class DriftInfo:
    log_id: int = np.NAN
    drift_id: int = np.NAN
    process_perspective: str = 'none'
    drift_type: str = 'none'
    drift_time: list = list
    activities_added: list = list
    activities_deleted: list = list
    activities_moved: list = list
    process_trees: list = list


    def drift_info_to_dict(self):
        DI = vars(self)
        keys_list = list(DI.keys())
        values_list = list(DI.values())
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
    log_id: int = np.NAN
    noisy_trace_prob: float = np.NAN
    noisy_event_prob: float = np.NAN


    def noise_info_to_dict(self):
        NI = vars(self)
        keys_list = list(NI.keys())
        values_list = list(NI.values())
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

    def add_noise(self, ninf):
        self.noise.append(ninf)
        self.increase_drift_count()

    def increase_drift_count(self):
        self.number_of_drifts += 1

    def increase_noise_count(self):
        self.number_of_noises += 1

    def fill_drift_log(
            self):  # This method is used to store the dictionary with log attribute levels in the log (xes file)
        param_drift = vars(DriftInfo)

    @staticmethod
    def extract_drift_xes_all(path):  # The path specified here must be a path to a folder without a slash at the end
        loaded_event_logs = {}
        for dir_path, dir_names, filenames in os.walk(path):
            for index, filename in enumerate(filenames):
                if filename.endswith('.xes'):
                    loaded_event_logs[filename] = os.sep.join([dir_path])

        read_class = list()

        for p in [v + "/" + k for k, v in loaded_event_logs.items()]:
            log = pm4py.read_xes(p)
            DI = DriftInfo(DriftInfo.extract_info_xes(log))
            read_class.append(DI)
        return read_class

    @staticmethod
    def extract_noise_xes_all(path):  # The path specified here must be a path to a folder without a slash at the end
        loaded_event_logs = {}
        for dir_path, dir_names, filenames in os.walk(path):
            for index, filename in enumerate(filenames):
                if filename.endswith('.xes'):
                    loaded_event_logs[filename] = os.sep.join([dir_path])

        read_class = list()

        for p in [v + "/" + k for k, v in loaded_event_logs.items()]:
            log = pm4py.read_xes(p)
            NI = DriftInfo(NoiseInfo.extract_info_xes(log))
            read_class.append(NI)
        return read_class


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
