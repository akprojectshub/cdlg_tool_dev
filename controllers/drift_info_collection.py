from dataclasses import dataclass

@dataclass
class DriftInfo:
    __init__(self, log_id, drift_id=1, process_perspective, drift_type, drift_time, activities_added, activities_deleted,
             actrivites_moved):
    self.log_id = log_id
    self.drift_id = drift_id  # isn't there only one drift per log generated in log generation via a file ? In this case isn't the drift_id always 1 ?
    self.process_perspective = process_perspective
    self.drift_type = drift_type
    self.drift_time = drift_time
    self.activities_added = activities_added
    self.activities_deleted = activities_deleted
    self.activities_moved = activities_moved

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
    noise_start: str  # timestamp like 2020-03-27 05:32:12
    noise_end: str  # timestamp like 2020-08-21 07:05:11

@dataclass
class LogDriftInfo:
    """
        Object for keeping information about added drift and noise instances for a generated event log
    """
    log_id: str  # unique name of the log to which the drift belongs
    number_of_drifts: int # initially 0
    number_of_noises: int # initially 0

    drifts: list[DriftInfo]
    noise: list[NoiseInfo]

    def add_drift(self):
        # TODO
        pass

    def add_noise(self):
        # TODO
        pass

    def increase_drift_count(self):
        # TODO
        pass

    def increase_noise_count(self):
        # TODO
        pass


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
