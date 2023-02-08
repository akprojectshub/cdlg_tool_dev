import sys
import random
import wexpect


def initial_config(log_setting):
    # Start the program and provide initial log information
    cmd_path, command, log_config = log_setting

    child = wexpect.spawn(cmd_path, ['/c', command])
    for config in log_config:
        child.expect(" ")
        child.sendline(config)
    print("Log initialized")

    return child


def drift_settings_selection(settings):
    drift_setting = {}
    drift_number_max, drift_types, drift_starts, drift_gradual_durations, drift_gradual_after, drift_sudden_lengths, drift_severities = settings
    drift_setting['drift_type'] = random.choice(drift_types)
    drift_setting['drift_start'] = str(round(random.uniform(drift_starts[0], drift_starts[1]), 2))
    drift_setting['drift_gradual_duration'] = str(round(random.randint(drift_gradual_durations[0], drift_gradual_durations[-1]), -1))
    drift_setting['drift_gradual_after'] = str(round(random.randint(drift_gradual_after[0], drift_gradual_after[-1]), -1))
    drift_setting['drift_sudden_length'] = str(round(random.randint(drift_sudden_lengths[0], drift_sudden_lengths[-1]), -1))
    drift_setting['drift_severity'] = str(round(random.uniform(drift_severities[0], drift_severities[1]), 2))

    return drift_setting


def add_first_drift(child, drift_setting):
    if drift_setting['drift_type'] == 'sudden':
        child, configs = first_sudden_drift(child, drift_setting)
    elif drift_setting['drift_type'] == 'gradual':
        child, configs = first_gradual_drift(child, drift_setting)
    else:
        print(f"First drift type {drift_setting['drift_start']} is not allowed. Sudden type is used ")
        child, configs = first_sudden_drift(child, drift_setting)
    return child, configs


def first_sudden_drift(child, drift_setting):
    configs = [drift_setting['drift_type'],
               drift_setting['drift_sudden_length'],
               drift_setting['drift_start'],
               'random',
               drift_setting['drift_severity']]
    for config in configs:
        child.expect(" ")
        child.sendline(config)

    return child, configs


def first_gradual_drift(child, drift_setting):
    start = round(float(drift_setting['drift_start']), 2)
    gradual_drift_min_length = 0.1
    drift_end = round(start + random.uniform(gradual_drift_min_length, 1-start-gradual_drift_min_length), 2)
    configs = [drift_setting['drift_type'],
               drift_setting['drift_sudden_length'],
               drift_setting['drift_start'],
               str(drift_end),
               'linear',
               'random',
               drift_setting['drift_severity']]
    for config in configs:
        child.expect(" ")
        child.sendline(config)

    return child, configs


def add_gradual_drift(child, drift_setting):
    configs = [drift_setting['drift_type'],
               'evolved_version',
               'random',
               drift_setting['drift_severity'],
               'end',
               drift_setting['drift_gradual_duration'],
               drift_setting['drift_gradual_after'],
               'linear']
    for config in configs:
        child.expect(" ")
        child.sendline(config)

    return child, configs


def add_sudden_drift(child, drift_setting):
    configs = [drift_setting['drift_type'],
               'evolved_version',
               'random',
               drift_setting['drift_severity'],
               'end',
               drift_setting['drift_sudden_length']]
    for config in configs:
        child.expect(" ")
        child.sendline(config)

    return child, configs


def add_drift(child, drift_setting):
    drift_type = drift_setting['drift_type']

    if drift_type == 'sudden':
        child, configs = add_sudden_drift(child, drift_setting)
    elif drift_type == 'gradual':
        child, configs = add_gradual_drift(child, drift_setting)
    else:
        print(f"Drift type {drift_type} is not allowed. Sudden type is used ")
        child, configs = add_sudden_drift(child, drift_setting)

    return child, configs


def drift_closing_decision(child, drift_number, drift_number_max):
    if drift_number == drift_number_max:
        child.expect("[yes, no]?")
        child.sendline('no')
    else:
        child.expect("[yes, no]?")
        child.sendline('yes')

    return child


def noise_setting_selection(noise_settings):

    noise_setting = {}
    noise, noise_type, noise_starts, noise_ends, noise_proportions, noise_severities = noise_settings
    noise_setting['noise'] = noise
    noise_setting['noise_type'] = noise_type
    noise_start = round(random.uniform(noise_starts[0], noise_starts[1]), 2)
    noise_setting['noise_start'] =str(noise_start)
    noise_setting['noise_end'] =str( round(noise_start + random.uniform(0.1, 1-noise_start-0.1), 2))
    noise_setting['noise_proportion'] =str(round(random.uniform(noise_proportions[0],noise_proportions[-1]), 1))
    noise_setting['noise_severity'] = str(round(random.uniform(noise_severities[0],noise_severities[-1]), 1))

    return noise_setting


def add_noise(child, noise_setting):
    print(f"Noise: {noise_setting['noise']}")
    if noise_setting['noise'] == "yes":
        child.expect("[yes, no]?")
        child.sendline('yes')
        configs = [noise_setting['noise_type'],
                   noise_setting['noise_start'],
                   noise_setting['noise_end'],
                   noise_setting['noise_proportion'],
                   noise_setting['noise_severity']]
        for config in configs:
            child.expect(" ")
            child.sendline(config)
    else:
        child.expect("[yes, no]?")
        child.sendline('no')

    return child


def main():

    drift_setting_dict = {}
    child = initial_config(LOG_SETTING)


    drift_number_max = random.randint(drift_numbers[0], drift_numbers[-1])
    for drift_number in range(1, drift_number_max + 1):
        drift_setting = drift_settings_selection(SETTINGS)
        if drift_number == 1:
            child, configs = add_first_drift(child, drift_setting)
        else:
            child, configs = add_drift(child, drift_setting)
        drift_setting_dict[str(drift_number)] = configs
        print(f"Drift {drift_number} added: {drift_setting['drift_type']}")
        child = drift_closing_decision(child, drift_number, drift_number_max)

    noise_setting = noise_setting_selection(NOISE_SETTINGS)
    drift_setting_dict['noise_setting'] = noise_setting
    child = add_noise(child, noise_setting)

    child.expect(wexpect.EOF)
    console = child.before
    log_name = console[-31:]
    config_dict = {log_name[2:-2]: drift_setting_dict}
    return config_dict


if __name__ == "__main__":
    number_of_logs = 5

    cmd_path = 'C:\windows\system32\cmd.exe'
    command = 'python start_generator_terminal.py'
    log_config = ['random', 'one_model', 'no', 'complex']
    LOG_SETTING = [cmd_path, command, log_config]

    drift_numbers = [1, 3]
    drift_types = ['sudden', 'gradual']
    drift_starts = [0.2, 0.8]
    drift_gradual_durations = [500, 1000]
    drift_gradual_after = [1000, 2000]
    drift_sudden_lengths = [2000, 4000]
    drift_severities = [0.2, 0.8]
    SETTINGS = [drift_numbers,
                drift_types,
                drift_starts,
                drift_gradual_durations,
                drift_gradual_after,
                drift_sudden_lengths,
                drift_severities]

    noise = 'no'
    noise_type = 'changed_model'
    noise_starts = [0.1, 0.9]
    noise_ends = [0.1, 0.9]
    noise_proportions = [0.1, 0.5]
    noise_severities = [0.1, 0.5]
    NOISE_SETTINGS = [noise, noise_type, noise_starts, noise_ends, noise_proportions, noise_severities]

    USED_PARAMETERS = {}
    for i in range(1, number_of_logs+1):
        print(f"Start of log generation: {i} out of {number_of_logs}")
        USED_PARAMETERS |= main()
        print(f"End of log generation: {i}", "\n")


    sys.exit()