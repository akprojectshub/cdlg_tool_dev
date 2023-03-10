from controllers.drift_info_collection import DriftInfo
from controllers.drift_info_collection import NoiseInfo
from controllers.drift_info_collection import LogDriftInfo
from dataclasses import dataclass

from controllers.drift_info_collection import DriftInfo
from controllers.drift_info_collection import NoiseInfo
from controllers.drift_info_collection import LogDriftInfo
import datetime
import pm4py

class DriftInfo:
    log_id: int
    drift_id: int # One drift per log so drift_id is always 1

    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)
    def __post_init__(self):
        if self.process_perspective not in ["control-flow"]:
            raise ValueError("wrong value inserted for process_perspective")

        if self.drift_type not in ["sudden", "gradual", "incremental", "recurring"]:
            raise ValueError("wrong drift type")

        if (type(self.log_id) != str):
            raise TypeError

        if (type(self.drift_id) != int):
            raise TypeError

        if (type(self.process_perspective) != str):
            raise TypeError

        if (type(self.drift_type) != str):
            raise TypeError

        if (type(self.drift_time) != list): #should be a list
            raise TypeError

        if (type(self.activities_added) != list): #should be a list:
            raise TypeError

        if (type(self.activities_deleted) != list): #should be a list
            raise TypeError

        if (type(self.activities_moved) != list): #should be a list
            raise TypeError

        if self.drift_type == "sudden" and len(self.drift_time)>1:
            self.drift_time.remove('N/A')

        if self.drift_type !="sudden" and type(self.drift_time[1]).__name__!='datetime':
            self.drift_time[1] = datetime.datetime.strptime(self.drift_time[1][0:len(self.drift_time[1])-6].strip(),"%Y-%m-%d %H:%M:%S.%f")

        self.drift_id=0 #Once we generate multiple drifts this should be changed

    def drift_info_to_dict(self):
        DI = vars(self)
        keys_list = list(DI.keys())
        values_list = list(DI.values())
        type_list = [type(i).__name__ for i in DI.values()]
        d = dict()
        d["value"] = True  ## By default need to add this as a parameter

        d_final =  {"value":True, "children":{}}

        for i in range(0, len(type_list)):
            if type_list[i] == 'list':
                d[keys_list[i]] = {keys_list[i] + "_" + str(j+1): values_list[i][j] for j in
                                   range(0, len(values_list[i]))}
                d_final["children"][keys_list[i]] = {"value":values_list[i],"children":d[keys_list[i]]}

            elif type_list[i] != 'list':
                d[keys_list[i]] = values_list[i]
                d_final["children"][keys_list[i]] = values_list[i]

        return d_final
    @staticmethod
    def extract_info_xes(log):

        d = dict()
        xes = log.attributes["drift:info"]["children"]

        for key, value in xes.items():
            if value == 0 and key!="drift_id":
                d[key] = []
            elif (type(value).__name__!='dict'):
                d[key] = value
            else:
                d[key] = list(value["children"].values())
        return d





trial = DriftInfo(1,2)
print(trial.log_id)