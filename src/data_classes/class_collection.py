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

    def add_drift(self, List_DriftInfo: list):
        self.drifts.append(List_DriftInfo)
        self.increase_drift_count(len(List_DriftInfo))

    def add_noise(self, instance: NoiseInfo):
        self.noise.append(instance)
        self.increase_noise_count()

    def increase_drift_count(self, nbr_drift_per_log):
        self.number_of_drifts += nbr_drift_per_log

    def increase_noise_count(self):
        self.number_of_noises += 1

    def fill_drift_log(self):
        # This method is used to store the dictionary with log attribute levels in the log (xes file)
        param_drift = vars(DriftInfo)

    def extract_drift_and_noise_info(self, path):
        loaded_event_logs = self.load_log_names_and_paths(path)
        for log_name, log_folder in loaded_event_logs.items():
            log = pm4py.read_xes(os.path.join(log_folder, log_name))
            DI = DriftInfo().extract_info_xes(log,log_name)
            #NI = NoiseInfo.extract_info_xes(os.path.join(log_folder, log_name),log)
            self.drifts.append(DI)
            self.increase_drift_count() # Question:Should drift count be incremented here (doesn't take into account multiple drifts per log ?
            #self.noise.append(NI)
            self.increase_noise_count()

        return self

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
                    log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c][
                        "children"]["change_trace_index"],
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
                        "children"]["activities_moved"],
                    log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c][
                        "children"]["change_start"],
                    log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c][
                        "children"]["change_end"])
            x = deepcopy(DI) # Should find a solution to avoid doing this
            drift_info_list.append(x)
        self.add_drift(drift_info_list)

        return drift_info_list  # should be an isntance of the class itself
        # extract info xes should return an istance of the class drift_info
        # the variable drifts later on should return contain list of drifts class instances

    #def extract_drift_info_from_log_collection(self,collection_folder_path):


    @staticmethod
    def load_log_names_and_paths(path):
        loaded_event_logs = {}
        for dir_path, dir_names, filenames in os.walk(path):
            for index, filename in enumerate(filenames):
                if filename.endswith('.xes'):
                    loaded_event_logs[filename] = os.sep.join([dir_path])
        return loaded_event_logs


    def Generate_collection_of_drifts (self, path):
        for log_name, log_folder in self.load_log_names_and_paths(path).items():
            log = pm4py.read_xes(os.path.join(log_folder, log_name))
            self.extract_drift_info_from_log(log,log_name)





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
        df.to_csv(f"{path}/drift_info.csv", index=False)
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





    def evaluate_new(self,Col_det):
        drift_ids_act = [DI_act[0].log_id for DI_act in self.drifts]
        drift_ids_det = [DI_det[0].log_id for DI_det in Col_det.drifts]

        drift_ids_det_left = drift_ids_det.copy()
        for drift_pos in range(0, len(self.drifts)):
            change_mom_act = self.extract_change_moments(self.drifts[drift_pos])
            if drift_ids_act[drift_pos] in drift_ids_det:
                pos_drift_to_match = drift_ids_det.index(drift_ids_act[drift_pos])
                change_mom_det = Col_det.extract_change_moments(Col_det.drifts[pos_drift_to_match])
                drift_ids_det_left.remove(drift_ids_act[drift_pos])
                for change_inf_act in change_mom_act:
                    change_mom_det = self.matching_new(change_inf_act, change_mom_det)

            elif drift_ids_act[drift_pos] not in drift_ids_det:
                self.FN += len(self.extract_change_moments(self.drifts[drift_pos]))  # if there is no log in the detected drift with the same ID as in the actual drift then increase the FN by the number of drifts in the actual drift
            self.FP += len(change_mom_det)  # All the change moments in the detected drift that didn't match but with the same logid as on log in the actual logs
        self.FP += len([cm for log_id in drift_ids_det_left for cm in Col_det.extract_change_moments(Col_det.drifts[drift_ids_det.index(log_id)])]) #All the log_ids in the dected that are not in the actual

    @staticmethod
    def extract_change_moments(drifts_in_log: list()): #takes a list of drift instances
        drift_moments = list()

        for drift_instance in drifts_in_log: #is a list containing all the drift instances of a single log
            change_id = 1
            for change_moment_info in list(drift_instance.change_info.values()):
                if change_moment_info["change_type"] == "gradual":
                    drift_moments.append((change_id,drift_instance.drift_type,change_moment_info["change_start"],change_moment_info["change_end"]))
                    change_id+=1
                elif change_moment_info["change_type"] == "sudden":
                    drift_moments.append((change_id,drift_instance.drift_type,change_moment_info["change_start"]))
                    change_id+=1
        return drift_moments # change_moments stores data in this format [(driftID,"drift_type1","TimeStamp1"),driftID,"drift_type1","TimeStamp1"),driftID,"drift_type1","TimeStamp1")]




    def matching_new(self,change_inf_act,change_mom_det):

        change_mom_det_filtered = [change_inf_det for change_inf_det in change_mom_det if change_inf_det[1] == change_inf_act[1]] #return the change moments in the change_moment_det that match the drift type of the actual change moment
        if len(change_mom_det_filtered) > 0:
            change_mom_diff = [abs(cm[2]-change_inf_act[2])for cm in change_mom_det_filtered]
            lowest_change_mom_diff_index = change_mom_diff.index(min(change_mom_diff))
            if self.check_latency(change_inf_act[2],change_mom_det_filtered[lowest_change_mom_diff_index][2], 2) == True:
                self.TP+=1 #the drift is in both the actual and the detected
                change_mom_det.remove(change_mom_det_filtered[lowest_change_mom_diff_index]) #remove the matching change from the list of change moments in the detected drifts

            elif self.check_latency(change_inf_act[2],change_mom_det_filtered[lowest_change_mom_diff_index][2], 2) == False:
                self.FN+=1 #The drift is in the actual but not in the detected

        elif len(change_mom_det_filtered) == 0:
            self.FN+=1 #there is no drift of the same type in the detected drift
        return change_mom_det

    @staticmethod
    def check_latency(cm_act, cm_det, lag):
        if (abs((cm_act-cm_det).days) <= lag):
            return True
        else:
            return False


    @staticmethod
    def check_drift_type(cm_act, cm_det):
        if (list(cm_act.keys())[0] == list(cm_det.keys())[0]):
            return True
        else:
            return False



#Test
"""
Col_act = Collection()
Col_det = Collection()

Col_act.Generate_collection_of_drifts("C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/experiments_all_types_v3_1685372669_actual")
Col_det.Generate_collection_of_drifts("C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/experiments_all_types_v3_1685372669_detected")




Col_act.evaluate_new(Col_det)

print(Col_act.TP)
print(Col_act.FN)
print(Col_act.FP)
"""


#####################################################################
#Thnings to DO:
#Change the parameters names
#specify a class that contains the parameter names ("children","change_info"...)
#make sure the function evaluate now works with a list of tupple ans input and that the comparision is done for logs with the same ID (DONE)
#make sure that process_tree stored in DriftInfo returns the correct result (sudden should retunr two process trees)


#Things I changed:
# I changed the command add drift so that it takes into account multiple drifts per log
# I changed the method add_change_info in the class_drift added change_start and change_end as parameters ---> Because of this generate collection of logs do not work anymore


