from controllers.drift_info_collection import DriftInfo
import pm4py
import xlswriter

workbook = xlswriter.Workbook("write_data.xlsx")

row_0 = ["log_id"]

attr = ["log_id", "drift_id", "process_perspective", "drift_type", "drift_time", "activities_added", "activities_deleted","activities_moved"]

DI = DriftInfo(1,1,"control-flow","incremental", ["datetime.datetime(2022, 7, 8, 5, 49, 40, 47514)", "datetime.datetime(2022, 10, 7, 13, 50, 24, 919672)","datetime.datetime(2022, 12, 31, 23, 29, 31, 540381)", "datetime.datetime(2023, 4, 9, 11, 5, 58, 154204)", "datetime.datetime(2023, 7, 6, 9, 48, 36, 400846)"], ["Random activity 1", "Random activity 2", "Random activity 3"], ["Random activity 1", "h"], [])



print(list(vars(DI).values()))

