import re
def extract_list_from_string(string_of_list: str):
    return [int(int_val_str) for int_val_str in re.findall(r'\d+', string_of_list)]

