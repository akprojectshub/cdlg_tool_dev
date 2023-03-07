import pm4py
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
import os
import datetime

out_folder = "C:/Users/ziedk/OneDrive/Bureau/New folder (2)/cdlg_tool_dev/data/generated_collections/1677861719/"

d = {'value': True,'children': {'s1':123}}

x = {"value":True,"children":{'s1':'a', 's2':'b'}}

if __name__ == "__main__":
    log = pm4py.read_xes("C:/Users/ziedk/OneDrive/Bureau/New folder (2)/cdlg_tool_dev/data/generated_collections/1677861719/log_0.xes")


log.attributes["drift:info"] = d
log.attributes["drift:info"]["drift:time"] = x

xes_exporter.apply(log, os.path.join(out_folder, "log_" + str(0) + "_new" + ".xes"))
