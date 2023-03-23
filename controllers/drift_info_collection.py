from dataclasses import dataclass, fields
import datetime
import glob, os
from datetime import timedelta
import numpy as np
import pm4py


@dataclass
class DriftInfo:
    """
        Object for keeping information about added drift to a generated event log
       :param drift information: log_id, drift_id, process_perspective, drift_type ...
       :return: a drift class object
    """
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
        """
              Converts the drift info class object to a dictionary. The purpose is to make it easier later on to store log level data in an xes file
             :return: a dictionary containing the drift information in a structure that is recognised by xes files
        """
        DI = vars(self)
        keys_list = list(DI.keys())
        values_list = list(DI.values())
        # TODO@Zied: please do not use methods starting with _ or __
        type_list = [str(type(i)).split(" ")[1][:-1].replace("'","") for i in DI.values()]
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
        """
            Stores drift information from a log into a dictionary
            :param a log
            :return: a dictionary containing the drift information
        """

        d = dict()
        xes = log.attributes["drift:info"]["children"]

        for key, value in xes.items():
            if value == 0 and key != "drift_id":
                d[key] = []
            # TODO@Zied: please do not use methods starting with _ or __

            elif (str(type(value)).split(" ")[1][:-1].replace("'", "") != 'dict'):
                d[key] = value
            else:
                d[key] = list(value["children"].values())
        return d


@dataclass
class NoiseInfo:
    """
        Object for keeping information about added noise to a generated event log
        :param noise information
        :return a noise class object
    """
    log_id: int = np.NAN
    noisy_trace_prob: float = np.NAN
    noisy_event_prob: float = np.NAN


    def noise_info_to_dict(self):
        """
              Converts the noise info class object to a dictionary. The purpose is to make it easier later on to store log level data in an xes file
             :return: a dictionary containing the noise information in a structure that is recognised by xes files
        """
        NI = vars(self)
        keys_list = list(NI.keys())
        values_list = list(NI.values())
        # TODO@Zied: please do not use methods starting with _ or __
        type_list = [str(type(i)).split(" ")[1][:-1].replace("'","") for i in NI.values()]
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
        """
                   Stores noise information from a log into a dictionary
                   :param a log
                   :return: a dictionary containing the noise information
        """
        d = dict()
        xes = log.attributes["noise:info"]["children"]

        for key, value in xes.items():
            if value == 0 and key != "drift_id":
                d[key] = []
            # TODO@Zied: please do not use methods starting with _ or __
            elif (str(type(value)).split(" ")[1][:-1].replace("'", "")!= 'dict'):
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
        """
        stores drift instances in a list and increments the counter that counts the number of drift classes instantiated so far
        :param drift instance
        """
        self.drifts.append(instance)
        self.increase_drift_count()

    def add_noise(self,  instance: NoiseInfo):
        """
        stores noise instances in a list and increments the counter that counts the number of noise classes instantiated so far
        :param noise instance
        """

        self.noise.append(instance)
        self.increase_noise_count()

    def increase_drift_count(self):
        """
        Increments the counter that counts the number of drift classes instantiated so far
        """
        self.number_of_drifts += 1

    def increase_noise_count(self):
        """
        Increments the counter that counts the number of noise classes instantiated so far
        """
        self.number_of_noises += 1

    def extract_drift_and_noise_info(self, path):
        """
        Create drift and noise instances for each log in a folder, stores them in lists and increment the drift and noise counters
        :param string path to a folder containing the generated logs stored in xes files
        :return
        """

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
        """
        Extracts all the log generated file paths and their names within a specified folder
        :param path leading to a folder containings the generated log in xes files
        :return a dictionary with every xes log file name and the path leading to it
        """
        loaded_event_logs = {}
        for dir_path, dir_names, filenames in os.walk(path):
            for index, filename in enumerate(filenames):
                if filename.endswith('.xes'):
                    loaded_event_logs[filename] = os.sep.join([dir_path])
        return loaded_event_logs

    @staticmethod
    def drift_time_check(tool_class, user_class, delta):
        # Path to a gold standard log, path to user generated log
        tool_drift_t = tool_class.drift_time
        user_drift_t = user_class.drift_time
        # First condition on the drift seasonality number
        if (len(tool_drift_t) != len(user_drift_t)):
            print(
                "Not the same number of seasonal changes considered in the log generated by the tool and the log generated by the user")
        else:
            for i in range(0, len(tool_drift_t)):
                print(abs(timedelta.total_seconds(tool_drift_t[i] - user_drift_t[i])))
                if (abs(timedelta.total_seconds(tool_drift_t[i] - user_drift_t[i])) > delta):
                    print("Drift time dicrepancy drift time " + str(i) + " doesn't match the golden standard")
                    return False
                else:
                    print("Drift time match")
                    return True


    @staticmethod
    def Precision(tool_class, user_class):
        # Precision = TruePositives / (TruePositives + FalsePositives)
        act_aff_tool = list()
        act_aff_tool.extend(tool_class.activities_added)
        act_aff_tool.extend(tool_class.activities_deleted)
        act_aff_tool.extend(tool_class.activities_moved)
        act_aff_tool = set(act_aff_tool)

        act_aff_user = list()
        act_aff_user.extend(user_class.activities_added)
        act_aff_user.extend(user_class.activities_deleted)
        act_aff_user.extend(user_class.activities_moved)
        act_aff_user = set(act_aff_user)

        TP = len(act_aff_tool.intersection(act_aff_user))
        FP = sum([1 for i in act_aff_user if i not in act_aff_tool])
        return TP / (FP + TP)

    @staticmethod
    def Recall(tool_class, user_class):
        # recall = TruePositives / (TruePositives + FalseNEgatives)
        act_aff_tool = list()
        act_aff_tool.extend(tool_class.activities_added)
        act_aff_tool.extend(tool_class.activities_deleted)
        act_aff_tool.extend(tool_class.activities_moved)
        act_aff_tool = set(act_aff_tool)

        act_aff_user = list()
        act_aff_user.extend(user_class.activities_added)
        act_aff_user.extend(user_class.activities_deleted)
        act_aff_user.extend(user_class.activities_moved)
        act_aff_user = set(act_aff_user)

        TP = len(act_aff_tool.intersection(act_aff_user))
        FN = sum([1 for i in act_aff_tool if i not in act_aff_user])
        return TP / (TP + FN)


def extract_change_moments_to_dict(created_log):
    """
        Returns a dictionary that contains all the change moments in a log
    """
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
    """
        Returns a list that contains all the change moments in a log
    """
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
