from dataclasses import dataclass, field
import numpy as np
from collections import defaultdict
from copy import deepcopy


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



    def add_change_info(self, change_trace_index, change_type, tree_previous, tree_new, deleted_acs, added_acs, moved_acs):

        self.add_process_tree(tree_new)
        change_id = str(len(self.change_info)+1)
        self.change_info[change_id] = {'change_type': change_type,
                                       'change_trace_index': change_trace_index,
                                       'process_tree_before': tree_previous,
                                       'process_tree_after': tree_new,
                                       'activities_deleted': deleted_acs,
                                       'activities_added': added_acs,
                                       'activities_moved': moved_acs}
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


