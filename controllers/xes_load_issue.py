# Import the event log in xes-format
import pm4py

if __name__ == "__main__":
    log = pm4py.read_xes("C:/Users/ziedk/OneDrive/Bureau/New folder/cdlg_tool_dev/data/generated_collections/1677637107/log_0_modified.xes")

########### After loading the XES file the objecct is considered as a string ####

print(log.attributes)
print("####")
print(log.attributes["drift:info"])
print("####")
print(log.attributes["noise:info"]["value"])



