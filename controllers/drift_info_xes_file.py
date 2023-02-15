import pm4py
import re


# Import the event log in xes-format
if __name__ == "__main__":
    log = pm4py.read_xes("C:/Users/ziedk/OneDrive/Bureau/New folder/cdlg_tool_dev/data/generated_collections/1676402108/log_0.xes")


print(log.attributes["drift:info"])

def extract(log_att,val): #serializer that takes the attribute drift:info or the attribute noise:info and extract the value val
    x = log_att
    x = log.attributes["drift:info"]
    s1 = re.findall("[a-z]+_[a-z]+", x)
    s2 = re.findall("\d+", x)[0:2]
    s3 = re.findall("=('[a-z ]+')", x)
    s4 = re.findall("(\[(.*?)\])", x)
    s4 = [i[0] for i in s4]
    s2.extend(s3)
    s2.extend(s4)
    if val not in s1:
        raise ValueError
    return(s2[s1.index(val)])
print(extract(log.attributes["drift:info"],"log_id"))
print(extract(log.attributes["drift:info"],"drift_id"))
print(extract(log.attributes["drift:info"],"process_perspective"))
print(extract(log.attributes["drift:info"],"drift_type"))
print(extract(log.attributes["drift:info"],"drift_time"))
print(extract(log.attributes["drift:info"],"activities_added"))
print(extract(log.attributes["drift:info"],"activities_deleted"))
print(extract(log.attributes["drift:info"],"activities_moved"))
