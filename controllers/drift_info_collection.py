from dataclasses import dataclass
import datetime
@dataclass
class DriftInfo:
    log_id: int
    drift_id: int # One drift per log so drift_id is always 1
    process_perspective:str
    drift_type: str
    drift_time:list[datetime.datetime] # With one timestamp or two timestamps according to the drift type so that the drift instantiation class is done in a single line
    activities_added:list
    activities_deleted:list
    activities_moved:list
    folder_id:int ## useful for accessing the folder and add the drift information in the logs generated in the collection of logs folder

    def __post_init__(self):
        if self.process_perspective not in ["control-flow"]:
            raise ValueError("wrong value inserted for process_perspective")
        else:
            print("True")

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

        self.drift_id=0 #Once we generate multiple drifts this should be changed


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

    def log_drift(self, log): #add drift information  to the log in the attribute level
        log.attributes["drift:info"] = self.drifts[self.log_id]

    def log_noise(self, log): #add noise information to the log in the attribute level
        log.attributes["noise:info"] = self.noise[self.log_id]

    def store_drift_xes(self):
        special_line = '<log xes.version="1849-2016" xes.features="nested-attributes" xmlns="http://www.xes-standard.org/">'
        for i in self.drifts:
            with open(str(i.folder_id) +"/log_" + str(i.log_id) +".xes", "r") as f:
                contents = f.readlines()
            line_index = [x for x in range(len(contents)) if special_line in contents[x]][0]

            values = ["<int key= 'Drift:info' value=" + "'" + str(i.log_id) + "'" +  ">",  ## What value should I put here
                      "<int key='Drift:id' value=" + "'" +str(i.drift_id) + "'" + "/>",
                      "<int key='Drift:process_perspective' value=" + "'"+ str(i.process_perspective) + "'" +"/>",
                      "<int key='Drift:type' value=" + "'" + str(i.drift_type) + "'" + "/>",
                      "<list key='Drift:drift_time' value=" + "'" + str(i.drift_time).strip() + "'" + "/>",
                      "<list key='Drift:activities_added' value=" + "'" + str(i.activities_added).strip() + "'" + "/>",
                      "<list key='Drift:activities_deleted' value=" + "'" + str(i.activities_deleted).strip() + "'" + "/>",
                      "<list key='Drift:activities_moved' value=" + "'" + str(i.activities_moved).strip() + "'" + "/>",
                      "</int>"]


            for j, v in enumerate(values):
                contents.insert(line_index + j + 1 , v)
            contents.insert(line_index + j + 2, "\n")
            with open(str(i.folder_id) + "/log_" + str(i.log_id) + "_modified" +".xes", "w") as f:
                contents = "".join(contents)
                f.write(contents)

    def store_noise_xes(self):
        special_line = '<log xes.version="1849-2016" xes.features="nested-attributes" xmlns="http://www.xes-standard.org/">'
        for i in self.noise:
            with open(str(i.folder_id) + "/log_" + str(i.log_id) + "_modified" +".xes", "r") as f:
                contents = f.readlines()
            line_index = [x for x in range(len(contents)) if special_line in contents[x]][0]

            values = ["<int key= 'noise:info' value=" + "'" + str(i.log_id) + "'" + ">",
                      ## What value should I put here
                      "<int key='noise:id' value=" + "'" + str(i.noise_id) + "'" + "/>",
                      "<string key='noise:perspective' value=" + "'" + str(i.noise_perspective) + "'" + "/>",
                      "<string key='noise:type' value=" + "'" + str(i.noise_type) + "'" + "/>",
                      "<float key='noise:proportion' value=" + "'" + str(i.noise_proportion) + "'" + "/>",
                      "<string key='noise:start_time' value=" + "'" + str(i.noise_start) + "'" + "/>",
                      "<string key='noise:end_time' value=" + "'" + str(i.noise_end) + "'" + "/>",
                      "</int>"]

            for j, v in enumerate(values):
                contents.insert(line_index + j + 2, v)
            contents.insert(line_index + j + 3, "\n")

            with open(str(i.folder_id) + "/log_" + str(i.log_id) + "_modified" + ".xes", "w") as f:
                contents = "".join(contents)
                f.write(contents)

    #def table(self,log): #this method will be used to fill the table



# IGNORE THINGS BELOW
# @dataclass
# class CollectionLogDriftInfo:
#     """
#         Object for keeping information about drift information accros all generated event logs
#     """
#
#     def export_to_json(self):
#         pass

# "perspective: control-flow; " \
# "type: sudden; " \
# "drift_moment: 2020-04-01 10:01:57 (0.4); " \
# "activities_added: [Random activity 1, Random activity 2, Random activity 3]; " \
# "activities_deleted: []; " \
# "activities_moved: []"
#
# "perspective: control-flow;"
# " type: gradual;"
# " specific_information: linear distribution;"
# " drift_start: 2020-10-08 21:11:36 (0.4);"
# " drift_end: 2021-01-25 08:13:53 (0.6); "
# "activities_added: [Random activity 1]; "
# "activities_deleted: [a]; "
# "activities_moved: []"
#
# "perspective: control-flow; "
# "type: incremental; "
# "specific_information: 5 versions of the process model;"
# " drift_start: 2020-03-23 18:40:23 (0.33);"
# "drift_end: 2020-04-04 21:57:37 (0.67);"
# "activities_added: [Random activity 1, Random activity 2];"
# "activities_deleted: [h, k, e, b];"
# "activities_moved: [c, f]"
#
# "perspective: control-flow; "
# "type: recurring; "
# "specific_information: 3 seasonal_changes;"
# "drift_start: 2020-04-13 09:42:30 (0.2);"
# "drift_end: 2020-08-03 13:43:19 (0.8);"
# " activities_added: [Random activity 1];"
# "activities_deleted: [g];
# "activities_moved: []"
#
# "noise_info:"
# "noise_proportion: 0.05;"
# "start_point: 2020-03-27 05:32:12 (0.1);"
# "end_point: 2020-08-21 07:05:11 (0.9);"
# "noise_type: random_model"