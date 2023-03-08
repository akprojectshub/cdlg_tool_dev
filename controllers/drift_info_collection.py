from dataclasses import dataclass
import datetime
import glob, os
import pm4py

@dataclass
class DriftInfo:
    log_id: int
    drift_id: int # One drift per log so drift_id is always 1
    process_perspective:str
    drift_type: str
    drift_time:dict # With one timestamp or two timestamps according to the drift type so that the drift instantiation class is done in a single line
    activities_added:dict # {"act added 1": ,...}
    activities_deleted:dict
    activities_moved:dict
    log_inf: bool = False

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



@dataclass
class NoiseInfo:
    """
        Object for keeping information about added noise to a generated event log
    """
    log_id: int  # unique name of the log to which the drift belongs
    noise_id: int  # unique per log
    noise_perspective: str  # control-flow
    noise_type: str  # like random_model
    noise_proportion: float  # 0.05
    noise_start: datetime.datetime  # timestamp like 2020-03-27 05:32:12
    noise_end: datetime.datetime # timestamp like 2020-08-21 07:05:11

    def __post_init__(self):
        if (type(self.log_id)!=str):
            raise TypeError

        if (type(self.noise_id)!=int):
            raise TypeError

        if (type(self.noise_perspective) != str):
            raise TypeError

        if (type(self.noise_type) != str):
            raise TypeError

        if (type(self.noise_proportion) != float):
            raise TypeError

        if (type(self.noise_start)!=datetime.datetime):
            raise TypeError

        if (type(self.noise_end) != datetime.datetime):
            raise TypeError

        self.noise_id=0 #Once we generate multiple drifts this should be changed
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
    drifts = list() #list[DriftInfo]
    noise = list()
    number_of_drifts: int = 0  # initially 0
    number_of_noises: int = 0  # initially 0

    def add_drift(self, dinf):
        self.drifts.append(dinf)

    def add_noise(self, ninf):
        self.noise.append(ninf)

    def increase_drift_count(self):
        self.number_of_drifts+=1

    def increase_noise_count(self):
        self.number_of_noises+=1

    def fill_drift_log(self): #This method is used to store the dictionary with log attribute levels in the log (xes file)
        param_drift = vars(DriftInfo)

    @staticmethod
    def extract_drift_xes_all(path):  # The path specified here must be a path to a folder without a slash at the end
        loaded_event_logs = {}
        for dir_path, dir_names, filenames in os.walk(path):
            for index, filename in enumerate(filenames):
                if filename.endswith('.xes'):
                    loaded_event_logs[filename] = os.sep.join([dir_path])

        read_class = list()

        for p in [v+"/"+k for k,v in loaded_event_logs.items()]:
            log = pm4py.read_xes(p)
            DI = DriftInfo(*list(DriftInfo.extract_info_xes(log).values()))
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
            NI = DriftInfo(*list(NoiseInfo.extract_info_xes(log).values()))
            read_class.append(NI)
        return read_class


















































