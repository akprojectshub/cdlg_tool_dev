from dataclasses import dataclass

import numpy as np


@dataclass
class NoiseInfo:
    """
        Object for keeping information about added noise to a generated event log
    """
    log_id: str = str
    noisy_trace_prob: float = np.NAN
    noisy_event_prob: float = np.NAN

    def noise_info_to_dict(self):
        NI = vars(self)
        keys_list = list(NI.keys())
        values_list = list(NI.values())
        # TODO@Zied: please do not use methods starting with _ or __
        type_list = [type(i).__name__ for i in NI.values()]
        d = dict()
        d["value"] = True  ## By default need to add this as a parameter

        d_final = {"value": True, "children": {}}

        for i in range(0, len(type_list)):
            if type_list[i] == 'list':
                d[keys_list[i]] = {keys_list[i] + "_" + str(j): values_list[i][j] for j in
                                   range(0, len(values_list[i]))}
                d_final["children"][keys_list[i]] = {"value": len(values_list[i]), "children": d[keys_list[i]]}

            elif type_list[i] != 'list':
                d[keys_list[i]] = values_list[i]
                d_final["children"][keys_list[i]] = values_list[i]
        return d_final

    def set_log_id(self, log_name):
        self.log_id = log_name
        return None

    def set_noisy_trace_prob(self,noise_trace_prob):
        self.noisy_trace_prob = noise_trace_prob
        return None

    def set_noisy_event_prob(self,noise_event_prob):
        self.noisy_event_prob = noise_event_prob
        return None

    @staticmethod
    def extract_info_xes(log):
        d = dict()
        xes = log.attributes["noise:info"]["children"]

        for key, value in xes.items():
            if value == 0 and key != "drift_id":
                d[key] = []
            # TODO@Zied: please do not use methods starting with _ or __
            elif (type(value).__name__ != 'dict'):
                d[key] = value
            else:
                d[key] = list(value["children"].values())
        return d

