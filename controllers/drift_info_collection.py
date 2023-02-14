from dataclasses import dataclass
import datetime
@dataclass
class DriftInfo:

        log_id:str
        drift_id = 1  # One drift per log so drift_id is always 1

        process_perspective:str
        if process_perspective not in ["control-flow"]:
            raise ValueError("wrong value inserted for process_perspective")

        drift_type:str
        if drift_type not in ["sudden", "gradual", "incremental","recurring"]:
            raise ValueError ("wrong drift type")

        drift_time:list
        activities_added:list
        activities_deleted:list
        activities_moved:list


@dataclass
class NoiseInfo:
    """
        Object for keeping information about added noise to a generated event log
    """
    log_id: str  # unique name of the log to which the drift belongs
    noise_id: int  # unique per log
    noise_perspective: str  # control-flow
    noise_type: str  # like random_model
    noise_proportion: float  # 0.05
    noise_start: datetime.datetime  # timestamp like 2020-03-27 05:32:12
    noise_end: datetime.datetime # timestamp like 2020-08-21 07:05:11



@dataclass
class LogDriftInfo:
    """
        Object for keeping information about added drift and noise instances for a generated event log
    """
    number_of_drifts = 0
    number_of_noises = 0
    drifts = list()
    noise = list()
    log_id = str

    @dataclass
    class LogDriftInfo:
        """
            Object for keeping information about added drift and noise instances for a generated event log
        """

        drifts: list[DriftInfo]
        noise: list[NoiseInfo]
        number_of_drifts: int = 0  # initially 0
        number_of_noises: int = 0  # initially 0

        def add_drift(self,DriftInfo):
            self.drifts.append(DriftInfo)

        def add_noise(self,NoiseInfo):
            self.noise.append(NoiseInfo)

        def increase_drift_count(self):
            self.number_of_drifts+=1

        def increase_noise_count(self):
            self.number_of_noises+=1

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
