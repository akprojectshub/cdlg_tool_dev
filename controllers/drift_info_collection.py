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

        if self.drift_type == "sudden":
            self.drift_time.remove('N/A')

        if self.drift_type !="sudden":
            self.drift_time[1] = datetime.datetime.strptime(self.drift_time[1][0:len(self.drift_time[1])-6].strip(),"%Y-%m-%d %H:%M:%S.%f")

        self.drift_id=0 #Once we generate multiple drifts this should be changed

    def drift_info_to_dict(self):
        DI = vars(self)
        d = dict()
        d["value"] = True ## By default need to add this as a parameter
        d["children"] = dict({i[0]:i[1] for i in zip(list(DI.keys()), list(DI.values()))})
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
        d = dict()
        d["value"] = True
        d["children"] = dict({i[0]: i[1] for i in zip(list(NI.keys()), list(NI.values()))})
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



def DriftInfo_from_xes(path):
    #C: / Users / ziedk / OneDrive / Bureau / New
    #folder / cdlg_tool_dev / data / generated_collections / 1677683533
    drifts = list()
    os.chdir(path)
    for file in glob.glob("*.xes"):
        if __name__ == "__main__":
            log = pm4py.read_xes(path+"/"+str(file))
        DI = DriftInfo(*list(log[list(log.attributes.keys())[0]]["children"].values()))
        drifts.append(DI)

    return drifts



def extract_change_moments(created_log):
    change_moments = {}
    current_model_version = created_log[0].attributes['model:version']
    change_id = 0
    for trace in created_log:
        change_moment = trace[0]['time:timestamp']
        version = trace.attributes['model:version']
        if version != current_model_version:
            change_id += 1
            change_moments['change_' + str(change_id)] = change_moment #.strftime("%Y-%m-%d, %H:%M:%S")
            current_model_version = version


    return {"value": "timestamps", "children": change_moments}












































