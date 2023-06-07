import os
from copy import deepcopy
from dataclasses import dataclass, field
from collections import defaultdict
import pandas as pd
import pm4py
import copy

from src.utilities import InfoTypes
from src.data_classes.class_drift import DriftInfo
from src.data_classes.class_noise import NoiseInfo
from src.utilities import TraceAttributes
import datetime
import re

@dataclass
class Collection:
    """
    Object for keeping information about added drift and noise instances for a generated event log collection
    """
    drifts: list = field(default_factory=list)
    noise: list = field(default_factory=list)
    number_of_drifts: int = 0
    number_of_noises: int = 0
    TP: int = 0
    FP: int = 0
    FN: int = 0

    def add_drift(self, instance: DriftInfo):
        self.drifts.append(instance)
        self.increase_drift_count()
    def add_drift_from_xes(self, list_drift_per_log: list):
        self.drifts.append(list_drift_per_log)
        self.increase_drift_count(list_drift_per_log)

    def add_noise(self, instance: NoiseInfo):
        self.noise.append(instance)
        self.increase_noise_count()

    def increase_drift_count(self):
        self.number_of_drifts += 1

    def increase_drift_count_from_xes(self, list_drift_per_log):
        self.number_of_drifts += len(list_drift_per_log)

    def increase_noise_count(self):
        self.number_of_noises += 1

    def fill_drift_log(self):
        # This method is used to store the dictionary with log attribute levels in the log (xes file)
        param_drift = vars(DriftInfo)


    def extract_drift_info_from_log(self,log,log_name):
        drift_info_list = []
        for k in list(log.attributes["drift:info"]["children"].keys()):  # parses through the drifts: k takes k, drift_2 ...
            DI = DriftInfo()
            DI.set_log_id(log_name)
            DI.set_drift_id(k)
            DI.set_process_perspective(log.attributes["drift:info"]["children"][k]["children"]["process_perspective"])
            DI.set_drift_type(log.attributes["drift:info"]["children"][k]["children"]["drift_type"])
            for c in list(log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"].keys()):

                DI.add_change_info(
                    [int(i) for i in re.findall(r'\d+',log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c]["children"]["change_trace_index"])],
                    log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c][
                        "children"]["change_type"],
                    log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c][
                        "children"]["process_tree_before"],
                    log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c][
                        "children"]["process_tree_after"], #pb with process tree output
                    log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c][
                        "children"]["activities_deleted"],
                    log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c][
                        "children"]["activities_added"],
                    log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c][
                        "children"]["activities_moved"])
                DI.convert_change_trace_index_into_timestamp(log)

            drift_info_list.append(DI)
        self.add_drift(drift_info_list)

        return None
        # extract info xes should return an istance of the class drift_info
        # the variable drifts later on should return contain list of drifts class instances

    def extract_noise_info_from_log(self,log):
        NI = NoiseInfo()
        for attr, val in log.attributes["noise:info"]["children"].items():
            if attr == "log_id":
                NI.set_log_id(val)
            elif attr == "noisy_trace_prob":
                NI.set_noisy_trace_prob(val)
            elif attr == "noisy_event_prob":
                NI.set_noisy_event_prob(val)
        self.add_noise(NI)
        return None

    @staticmethod
    def load_log_names_and_paths(path):
        loaded_event_logs = {}
        for dir_path, dir_names, filenames in os.walk(path):
            for index, filename in enumerate(filenames):
                if filename.endswith('.xes'):
                    loaded_event_logs[filename] = os.sep.join([dir_path])
        return loaded_event_logs


    def Extract_collection_of_drifts (self, path):
        for log_name, log_folder in self.load_log_names_and_paths(path).items():
            log = pm4py.read_xes(os.path.join(log_folder, log_name))
            self.extract_drift_info_from_log(log,log_name)

    def import_drift_and_noise_info_from_flat_file_csv(self, path):
        pass

        return None


    def export_drift_and_noise_info_to_flat_file_csv(self, path):
        dict_nested = dict()
        for drift in self.drifts:
            for attr_key, attr_value in vars(drift).items():
                drift_label = 'drift_' + str(drift.drift_id)
                if isinstance(attr_value, dict):
                    count = 1
                    for attr, value in attr_value.items():
                        if isinstance(value, dict):
                            dict_nested[drift.log_id, drift_label, attr_key + '_' + str(count)] = value
                        else:
                            dict_nested[drift.log_id, drift_label, attr_key + '_' + str(count)] = {attr: value}
                        count += 1
                else:
                    dict_nested[drift.log_id, drift_label, attr_key] = {'1': attr_value}

            # Add noise info
            noise_info_rel = [noise_instance for noise_instance in self.noise if noise_instance.log_id == drift.log_id]
            for index, noise_instance in enumerate(noise_info_rel):
                count = 1
                for attr, value in vars(noise_instance).items():
                    if attr != 'log_id':
                        dict_nested[drift.log_id, 'noise_' + str(index+1), 'parameter_' + str(count)] = {attr: value}
                        count += 1

        flat_file = []
        for key, values in dict_nested.items():
            for k, v in values.items():
                data = list(key)
                data.extend([k, v])
                flat_file.append(data)

        df = pd.DataFrame(flat_file, columns=['log_name', 'drift_or_noise_id', 'drift_attribute', 'drift_sub_attribute', 'value'])
        df.to_csv(f"{path}/drift_info.csv", index=False, sep=';')
        return None

    def convert_change_trace_index_into_timestamp(self, event_log, log_name):
        for drift in self.drifts:
            if drift.log_id == log_name:
                change_info_new = deepcopy(drift.change_info)
                for change_id, change_data in drift.change_info.items():
                    for change_attr, attr_value in change_data.items():
                        if change_attr == 'change_trace_index':
                            if isinstance(attr_value, list) and len(attr_value) == 2:
                                change_info_new[change_id]['change_start'] = event_log[attr_value[0]][0][TraceAttributes.timestamp.value]
                                change_info_new[change_id]['change_end'] = event_log[attr_value[-1]][0][TraceAttributes.timestamp.value]
                            elif isinstance(attr_value, list) and len(attr_value) == 1:
                                change_timestamp = event_log[attr_value[0]][0][TraceAttributes.timestamp.value]
                                change_info_new[change_id]['change_start'] = change_timestamp
                                change_info_new[change_id]['change_end'] = change_timestamp
                            else:
                                Warning("Something is wrong!")
                drift.change_info = change_info_new
        return None

    def add_drift_info_to_log(self, event_log, log_name):
        output_dict_all_drifts = {'value': 'temp', 'children': {}}
        for drift in self.drifts:
            if drift.log_id == log_name:
                output_dict_drift = dict()
                output_dict_drift.update({'value': drift.drift_id, 'children': {}})
                # TODO: improve the line below: make it dynamic
                attr_for_export = ['process_perspective', 'drift_type', 'process_trees', 'change_info']
                for key, value in vars(drift).items():
                    if key in attr_for_export:
                        if isinstance(value, dict):
                            if key == 'change_info':
                                output_dict_drift['children']['change_info'] = {'value': len(value), 'children': {}}
                                for k, v in value.items():
                                    #for kk, vv in v.items():
                                    output_dict_drift['children']['change_info']['children'].update( {'change_id_' + str(k): {'value': 'info', 'children': v}})
                        else:
                            output_dict_drift['children'].update({key: value})

                output_dict_all_drifts['children']['drift_' + str(drift.drift_id)] = output_dict_drift

        event_log.attributes[InfoTypes.drift_info.value] = output_dict_all_drifts

        return event_log


    def evaluate(self,Col_det):
        drift_ids_act = [DI_act[0].log_id for DI_act in self.drifts]
        drift_ids_det = [DI_det[0].log_id for DI_det in Col_det.drifts]
        FP_per_log = 0
        drift_ids_det_left = drift_ids_det.copy()
        change_mom_det = []
        change_mom_det_to_del = list()
        for drift_pos in range(0, len(self.drifts)): #self.drifts is a list of drifts each change moment in a log is stored in an instance and each instance belonging to the same log are saved in the same list
            change_mom_act = self.extract_change_moments(self.drifts[drift_pos])

            if drift_ids_act[drift_pos] in drift_ids_det:
                pos_drift_to_match = drift_ids_det.index(drift_ids_act[drift_pos])
                change_mom_det = Col_det.extract_change_moments(Col_det.drifts[pos_drift_to_match])
                drift_ids_det_left.remove(drift_ids_act[drift_pos])
                for change_inf_act in change_mom_act:
                    change_mom_det_to_del.extend(self.matching(change_inf_act, change_mom_det))
            elif drift_ids_act[drift_pos] not in drift_ids_det:
                self.FN += len(self.extract_change_moments(self.drifts[drift_pos]))  # if there is no log in the detected drift with the same ID as in the actual drift then increase the FN by the number of drifts in the actual drift

        # FP represent the sum of all reamining change moments in the detected drifts that are not available in the actual drift
        cm_all_det = list()
        for cm in Col_det.drifts:
            cm_all_det.extend(Col_det.extract_change_moments(cm))
        self.FP = sum([1 if cm not in change_mom_det_to_del else 0 for cm in cm_all_det])

    @staticmethod
    def extract_change_moments(drifts_in_log: list()): #takes a list of drift instances
        drift_moments = list()
        for drift_instance in drifts_in_log: #is a list containing all the drift instances of a single log
            change_id = 1
            for change_moment_info in list(drift_instance.change_info.values()):
                if change_moment_info["change_type"] == "gradual":
                    drift_moments.append((change_id,drift_instance.drift_type,change_moment_info["change_start"]))
                    change_id+=1
                    drift_moments.append((change_id,drift_instance.drift_type,change_moment_info["change_end"]))
                    change_id+=1
                elif change_moment_info["change_type"] == "sudden":
                    drift_moments.append((change_id,drift_instance.drift_type,change_moment_info["change_start"]))
                    change_id+=1
        return drift_moments # change_moments stores data in this format [(driftID,"drift_type1","TimeStamp1"),driftID,"drift_type1","TimeStamp1"),driftID,"drift_type1","TimeStamp1")]




    def matching(self,change_inf_act,change_mom_det):
        change_mom_det_filtered = self.check_drift_type(change_inf_act, change_mom_det) #return the change moments in the change_moment_det that match the drift type of the actual change moment
        change_mom_det_to_del = []
        if len(change_mom_det_filtered) > 0:
            change_mom_diff = [abs(cm[2]-change_inf_act[2])for cm in change_mom_det_filtered]
            lowest_change_mom_diff_index = change_mom_diff.index(min(change_mom_diff))
            if self.check_latency(change_inf_act[2],change_mom_det_filtered[lowest_change_mom_diff_index][2], 20) == True:
                self.TP+=1 #the drift is in both the actual and the detected
                change_mom_det_to_del.append(change_mom_det_filtered[lowest_change_mom_diff_index]) #remove the matching change from the list of change moments in the detected drifts

            elif self.check_latency(change_inf_act[2],change_mom_det_filtered[lowest_change_mom_diff_index][2], 20) == False:
                self.FN+=1 #The drift is in the actual but not in the detected

        elif len(change_mom_det_filtered) == 0:
            self.FN+=1 #there is no drift of the same type in the detected drift
        return change_mom_det_to_del

    @staticmethod
    def check_latency(cm_act, cm_det, lag):
        if (abs((cm_act-cm_det).days) <= lag):
            return True
        else:
            return False


    @staticmethod
    def check_drift_type(change_inf_act, change_mom_det):
        return [change_inf_det for change_inf_det in change_mom_det if change_inf_det[1] == change_inf_act[1]]




