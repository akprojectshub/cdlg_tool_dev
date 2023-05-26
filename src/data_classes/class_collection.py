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


@dataclass
class Collection:
    """
    Object for keeping information about added drift and noise instances for a generated event log collection
    """
    drifts: list = field(default_factory=list)
    noise: list = field(default_factory=list)
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

    def fill_drift_log(self):
        # This method is used to store the dictionary with log attribute levels in the log (xes file)
        param_drift = vars(DriftInfo)

    def extract_drift_and_noise_info(self, path):
        loaded_event_logs = self.load_log_names_and_paths(path)
        print(loaded_event_logs)
        for log_name, log_folder in loaded_event_logs.items():
            log = pm4py.read_xes(os.path.join(log_folder, log_name))
            DI = DriftInfo().extract_info_xes(log,log_name)
            #NI = NoiseInfo.extract_info_xes(os.path.join(log_folder, log_name),log)
            self.drifts.append(DI)
            self.increase_drift_count() # Question:Should drift count be incremented here (doesn't take into account multiple drifts per log ?
            #self.noise.append(NI)
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



    def evaluate(self,Coll_det):
        TP = 0
        FN = 0
        FP = 0
        type_cm_det_all  = [j for i in Coll_det.drifts for j in self.extract_change_moments(i)]
        type_cm_act_all = [j for i in self.drifts for j in self.extract_change_moments(i)]#stores the type and change moment of all drifts in the collection


        for i in type_cm_act_all:
            drift_type_act = list(i.keys())[0]
            cms_det = [i for i in type_cm_det_all if list(i.keys())[0]==drift_type_act] ##cms_det contains all the drift_type:change_moments in the collection with drift_type= drift_type_act
            if (self.matching(i,cms_det)[1] =="TP"):
                del type_cm_det_all[self.matching(i,cms_det)[0]]
                TP+=1
            elif(self.matching(i,cms_det)[1] == "FN"):
                FN+=1
        FP = len( type_cm_det_all)


        return {"TP":TP,"FN":FN,"FP":FP}


    @staticmethod
    def extract_change_moments(d):
        l = list()
        for i in d: #is a list containing all the drift instances of a single log
            l = list()
            for v in list(i.change_info.values()):
                if v["change_type"] == "gradual":
                    l.append({i.drift_type:v["change_start"]})
                    l.append({i.drift_type:v["change_end"]})
                elif v["change_type"] == "sudden":
                    l.append({i.drift_type:v["change_start"]})

        return l # l stores data in this format [{"drift_type1":"CM1"},{"drift_type1":"CM2"},{"drift_type2":"CM1"}]


    def matching(self,cm_act, cms_det:list):
        r = [None, None] # this is the list returned by the matching method ["index of the change moment to delete in the  type_cm_det_all", "TP or
        index_min_diff = [abs(list(i.values())[0]-list(cm_act.values())[0]) for i in cms_det].index(min([abs(list(i.values())[0]-list(cm_act.values())[0]) for i in list(cms_det)]))
        if self.check_latency(cm_act, cms_det[index_min_diff], 12) == True and self.check_drift_type(cm_act, cms_det[index_min_diff])== True:
            r = [index_min_diff, "TP"]
        elif self.check_latency(cm_act, cms_det[index_min_diff], 12) == False or self.check_drift_type(cm_act, cms_det[index_min_diff])== False:
            r =  [None,"FN"]
        return r


    @staticmethod
    def check_latency(cm_act, cm_det, alpha):
        if ((abs(list(cm_act.values())[0]- list(cm_det.values())[0])).days <=alpha):
            return True
        else:
            return False


    @staticmethod
    def check_drift_type(cm_act, cm_det):
        if (list(cm_act.keys())[0] == list(cm_det.keys())[0]):
            return True
        else:
            return False






actual = Collection().extract_drift_and_noise_info("C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/experiments_all_types_v3_1684672207_actual")

detected = Collection().extract_drift_and_noise_info("C:/Users/ziedk/OneDrive/Bureau/Process Mining Git/output/experiments_all_types_v3_1684672207_detected")

print(actual.evaluate(detected))

