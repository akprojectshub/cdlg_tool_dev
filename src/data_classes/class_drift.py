from dataclasses import dataclass, field
import numpy as np
from collections import defaultdict
from copy import deepcopy
import re



@dataclass
class DriftInfo:
    log_id: str = None
    drift_id: int = np.NAN
    process_perspective: str = None
    drift_type: str = None
    process_trees: dict = field(default_factory=lambda: defaultdict(dict))
    change_info: dict = field(default_factory=lambda: defaultdict(dict))

    def set_log_id(self, log_name):
        self.log_id = log_name
        return None

    def set_drift_id(self, drift_id):
        self.drift_id = drift_id
        return None


    def set_process_perspective(self, process_perspective):
        self.process_perspective = process_perspective
        return None

    def set_drift_type(self, drift_type):
        self.drift_type = drift_type
        return None

    def add_process_tree(self, process_tree):
        process_tree_id = str(len(self.process_trees))
        self.process_trees[process_tree_id] = deepcopy(process_tree)
        return None



    def add_change_info(self, change_trace_index, change_type, tree_previous, tree_new, deleted_acs, added_acs, moved_acs,change_start,change_end): #Question: Shouldn't we also store the start and end time if a drift ?

        self.add_process_tree(tree_new)
        change_id = str(len(self.change_info)+1)
        self.change_info[change_id] = {'change_type': change_type,
                                       'change_trace_index': change_trace_index,
                                       'process_tree_before': tree_previous,
                                       'process_tree_after': tree_new,
                                       'activities_deleted': deleted_acs,
                                       'activities_added': added_acs,
                                       'activities_moved': moved_acs,
                                       'change_start': change_start,
                                       'change_end':change_end}
        return None

    def convert_change_trace_index_into_timestamp(self, event_log):

        change_info_new = deepcopy(self.change_info)
        for change_id, change_data in self.change_info.items():
            for change_attr, attr_value in change_data.items():
                if change_attr == 'change_trace_index':
                    change_info_new[change_id]['change_start'] = event_log[attr_value[0]][0]['time:timestamp']
                    if isinstance(attr_value, list) and len(attr_value) == 2:
                        change_info_new[change_id]['change_end'] = event_log[attr_value[-1]][0]['time:timestamp']
                    elif isinstance(attr_value, list) and len(attr_value) == 1:
                        change_info_new[change_id]['change_end'] = change_info_new[change_id]['change_start']
                    else:
                        ValueError("Something is wrong!")
        self.change_info = change_info_new
        return None

    def get_previous_process_tree(self):
        max_process_tree_id = str(max([int(key) for key in self.process_trees.keys()]))
        previous_process_tree = deepcopy(self.process_trees[max_process_tree_id])
        return previous_process_tree


    def extract_info_xes(self,log, log_name):
        l = []
        for k in list(log.attributes["drift:info"]["children"].keys()): #parses through the drifts: k takes k, drift_2 ...
            log_ID = re.findall("(\d+)", log_name)[1]
            self.set_log_id(log_ID)
            self.set_drift_id(k)
            self.set_process_perspective(log.attributes["drift:info"]["children"][k]["children"]["process_perspective"])
            self.set_drift_type(log.attributes["drift:info"]["children"][k]["children"]["drift_type"])
            for c in list(log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"].keys()):
                self.add_change_info(log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c]["children"]["change_trace_index"],
                                     log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c]["children"]["change_type"],
                                     log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c]["children"]["process_tree_before"],
                                     log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c]["children"]["process_tree_after"],
                                     log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c]["children"]["activities_deleted"],
                                     log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c]["children"]["activities_added"],
                                     log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c]["children"]["activities_moved"],
                                     log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c]["children"]["change_start"],
                                     log.attributes["drift:info"]["children"][k]["children"]["change_info"]["children"][c]["children"]["change_end"])
            x = deepcopy(self)
            l.append(x)
        return l #should be an isntance of the class itself
        #extract info xes should return an istance of the class drift_info
        #the variable drifts later on should return contain list of drifts class instances







def initialize_drift_instance_from_list(input: list):
    log_id, drift_id, perspective, drift_type, drift_time, added, deleted, moved, trees = input

    drift_instance = DriftInfo()
    if drift_type:
        drift_instance.log_id = log_id
        drift_instance.drift_id = drift_id
        drift_instance.process_perspective = perspective
        drift_instance.drift_type = drift_type
        drift_instance.drift_time = drift_time
        drift_instance.activities_added = added
        drift_instance.activities_deleted = deleted
        drift_instance.activities_moved = moved
        drift_instance.process_trees = trees

    return drift_instance
