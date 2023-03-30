import os
from copy import deepcopy
from dataclasses import dataclass

import pandas as pd
import pm4py

from src.utilities import InfoTypes
from src.data_classes.class_drift import DriftInfo
from src.data_classes.class_noise import NoiseInfo
from src.utilities import TraceAttributes

@dataclass
class Collection:
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


    def _old_temp_save_drift_info_to_csv_file(self, path):
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


    def export_drfit_and_noise_info_to_flat_file_csv(self, path):
        # TODO: this is a temporal function that needs to be revised and checked
        dict_nested = dict()
        for drift in self.drifts:
            for attr_key, attr_value in vars(drift).items():
                drift_label = 'drift_' + str(drift.drift_id)
                if isinstance(attr_value, dict):
                    for attr, value in attr_value.items():
                        if isinstance(value, dict):
                            for a, v in value.items():
                                dict_nested[drift.log_id, drift_label, attr_key] = value
                        else:
                            dict_nested[drift.log_id, drift_label, attr_key] = {attr: value}
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
        df.to_csv(f"{path}/aggregated_drift_info.csv", index=False)

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
                            elif isinstance(attr_value, int):
                                print(vars(drift))
                                print(len(event_log), attr_value)
                                change_info_new[change_id]['change_start'] = event_log[attr_value][0][TraceAttributes.timestamp.value]
                                change_info_new[change_id]['change_end'] = event_log[attr_value][0][TraceAttributes.timestamp.value]
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
                                output_dict_drift['children']['change_info'] = {'value': 'temp', 'children': {}}
                                for k, v in value.items():

                                    output_dict_drift['children']['change_info'].update({'value': k, 'children': v})
                        else:
                            output_dict_drift['children'].update({key: value})

                output_dict_all_drifts['children']['drift_' + str(drift.drift_id)] = output_dict_drift


        event_log.attributes[InfoTypes.drift_info.value] = output_dict_all_drifts

        return event_log
