import pm4py
from pm4py.objects.log.obj import Trace
from pm4py.objects.log.obj import Event
import datetime
import os
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
import time



# Import the event log in xes-format
if __name__ == "__main__":
    log = pm4py.read_xes("C:/Users/ziedk/OneDrive/Bureau/New folder/cdlg_tool_dev/log_test.xes")

def store_drift(log,drift_class):
    drift_info = Trace()
    drift_instance = Event()
    drift_instance['drift:id'] = drift_class.drift_id
    drift_instance['drift:process_perspective'] = drift_class.process_perspective
    drift_instance['drift:type'] = drift_class.drift_type
    drift_instance['drift:moment'] = drift_class.drift_time
    drift_instance['drift:added'] = drift_class.activities_added
    drift_instance['drift:removed'] = drift_class.activities_deleted
    drift_instance['drift:changed'] = drift_class.activities_moved
    drift_info.append(drift_instance)
    log.attributes['drift:info'] = drift_info
    return log

def store_noise(log,noise_class):
    noise_info = Trace()
    noise_instance = Event()
    noise_instance['noise:id'] = noise_class.noise_id
    noise_instance['noise:perspective'] = noise_class.noise_perspective
    noise_instance['noise:type'] = noise_class.noise_type
    noise_instance['noise:proportion'] = noise_class.noise_proportion
    noise_instance['noise:start'] = noise_class.noise_start
    noise_instance['noise:end'] = noise_class.noise_end
    noise_info.append(noise_instance)
    log.attributes['noise:info'] = noise_info
    return log




    log_id: str  # unique name of the log to which the drift belongs
    noise_id: int  # unique per log
    noise_perspective: str  # control-flow
    noise_type: str  # like random_model
    noise_proportion: float  # 0.05
    noise_start: datetime.datetime  # timestamp like 2020-03-27 05:32:12
    noise_end: datetime.datetime # timestamp like 2020-08-21 07:05:11





#xes_exporter.apply(store_drift(log,drift_class):, os.path.join(out_folder, "log_"+str(i)+".xes"))



# Import the event log in xes-format
#if __name__ == "__main__":
#    log2 = pm4py.read_xes("C:/Users/ziedk/OneDrive/Bureau/New folder/cdlg_tool_dev/log_test.xes")



#print(log2.attributes['drift:info'][0]['drift:id'])
#print(log2.attributes)
