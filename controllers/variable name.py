from dataclasses import dataclass

@dataclass
class DriftAttributeClass():
    att1 = "log_id"
    att2 = "drift_id"
    att3 = "process_perspective"
    att4 ="drift_type"
    att5 ="drift_time"
    att6 = "activities_added"
    att7 = "activities_deleted"
    att8="activities_moved"
    att9="folder_id"

    def extract_name_val(self):
        s =""
        att = list()
        for property, value in vars(DriftAttributeClass).items():
            s = s + str(property) + ":" + str(value) + "\n"

        for i in s.split("\n"):
            if i.split(":")[0] == "extract_name_val":
                break
            att.append(i)
        return att[1:]



@dataclass
class DriftInfo:
    for i in DriftAttributeClass().extract_name_val():
        exec("%s = %s" % (i.split(":")[1], None))

    ##### PROBLEM : WE CANNOT INFORCE THE VARIABLE TYPE ANYMORE

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


