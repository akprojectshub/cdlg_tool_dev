from dataclasses import dataclass
import datetime
@dataclass
class DriftInfo:
    log_id: int
    drift_id: int # One drift per log so drift_id is always 1
    process_perspective:str
    drift_type: str
    drift_time:list # With one timestamp or two timestamps according to the drift type so that the drift instantiation class is done in a single line
    activities_added:list
    activities_deleted:list
    activities_moved:list
    folder_id:int ## useful for accessing the folder and add the drift information in the logs generated in the collection of logs folder

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

        if (type(self.drift_time) != list):
            raise TypeError

        if (type(self.activities_added) != list):
            raise TypeError

        if (type(self.activities_deleted) != list):
            raise TypeError

        if (type(self.activities_moved) != list):
            raise TypeError

        if "N/A" in self.drift_time: # Removes "N/A" in case the drift if sudden and there is no end_drift_time
            self.drift_time.remove("N/A")
        else:
            self.drift_time[1] = datetime.datetime.strptime(self.drift_time[1][0:len(self.drift_time[1])-6].strip(),"%Y-%d-%m %H:%M:%S")


        self.drift_id=0 #Once we generate multiple drifts this should be changed

    def drift_info_to_dict(self, DI):
        d = dict()
        d["value"] = True
        d["children"] = dict({i[0]:i[1] for i in zip(vars(DI).keys(), list(vars(DI).values()))})
        del d["children"]["folder_id"]
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
    folder_id:int ## useful for accessing the folder and add the drift information in the logs generated in the collection of logs folder

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
    def noise_info_to_dict(self, NI):
        d = dict()
        d["value"] = True
        d["children"] = dict({i[0]: i[1] for i in zip(vars(NI).keys(), list(vars(NI).values()))})
        del d["children"]["folder_id"]
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















































