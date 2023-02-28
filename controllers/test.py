from dataclasses import dataclass
import datetime



@dataclass
class LogDriftInfo:
    """
    Object for keeping information about added drift and noise instances for a generated event log
    """
    drifts = list()  # list[DriftInfo]
    noise = list()
    number_of_drifts: int = 0  # initially 0
    number_of_noises: int = 0  # initially 0

    def add_drift(self, dinf):
        self.drifts.append(dinf)

    def store_noise_xes(self):
        special_line = '<log xes.version="1849-2016" xes.features="nested-attributes" xmlns="http://www.xes-standard.org/">'
        for i in self.noise:
            values = list()
            i_keys = list(vars(i).keys())
            i_val = list(vars(i).values())

            with open(str(i.folder_id) + "/log_" + str(i.log_id) + "_modified" + ".xes", "r") as f:
                contents = f.readlines()
            line_index = [x for x in range(len(contents)) if special_line in contents[x]][0]

            values.append("<int key="+str(i_keys[0])+"value=" + "'" + str(i_val[0]) + "'>")
            values = ["<int key="+str(i_keys[j]) + "value='" + str(i_val[j]) + "'/>"  for j in range(1,len(i_keys))]
            values.append("</int>")

            for j, v in enumerate(values):
                contents.insert(line_index + j + 2, v)
            contents.insert(line_index + j + 3, "\n")

            with open(str(i.folder_id) + "/log_" + str(i.log_id) + "_modified" + ".xes", "w") as f:
                contents = "".join(contents)
                f.write(contents)
