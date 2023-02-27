# Import the event log in xes-format
import pm4py

if __name__ == "__main__":
    log = pm4py.read_xes("C:/Users/ziedk/OneDrive/Bureau/New folder/cdlg_tool_dev/data/generated_collections/1677165193/log_0_modified.xes")

########### After loading the XES file the objecct is considered as a string ####

print(log.attributes["Drift:info"])
print(log.attributes["noise:info"])



