from random import random
from src.utilities import TraceAttributes, select_random
from src import configurations as config
from pm4py.objects.process_tree import semantics
import math
import numpy
import random
from pm4py.objects.log.obj import EventLog
from copy import deepcopy



def combine_two_logs_with_certain_change_type(log_1: EventLog, log_2: EventLog, paremeters):

    random_int = random()
    if random_int > config.CHANGE_TYPE_THRESHOLD:
        combined_log = combine_two_logs_sudden(log_1, log_2)
    else:
        gradual_type = select_random(paremeters.Gradual_drift_type, option='random')
        combined_log = combine_two_logs_gradual(log_1, log_2, gradual_type)

    return combined_log


def combine_two_logs_sudden(log_1: EventLog, log_2: EventLog):
    """ Merging of two event logs

    :param log_one: first event log
    :param log_two: second event log
    :return: combined event log
    """
    log_one = deepcopy(log_1)
    log_two = deepcopy(log_2)
    log_combined = EventLog()


    last_model_version = 0
    for trace in log_one:
        try:
            last_model_version = trace.attributes[TraceAttributes.model_version.value]
        except:
            trace.attributes[TraceAttributes.model_version.value] = last_model_version
        log_combined.append(trace)

    for trace in log_two:
        trace.attributes[TraceAttributes.model_version.value] = last_model_version + 1
        log_combined.append(trace)

    log_combined = update_trace_ids(log_combined)

    return log_combined

def combine_two_logs_gradual(log_1: EventLog, log_2: EventLog, option: str = 'linear'):
    pass

    # TODO: write a function that detects the latest id in the log
    # TODO: write a function that assigns an id to all traces in a given event log
    # TODO: use distribute_traces to create

    log_transition = distribute_traces(tree_previous, tree_new, gradual_type, num_traces_gradual_phase)


    log_1
    log_2
    return None


def update_trace_ids(log):
    trace_id = 0
    for trace in log:
        trace.attributes[TraceAttributes.concept_name.value] = str(trace_id)
        trace_id += 1
    return log



def distribute_traces(tree_one, tree_two, distribute_type, nu_traces):
    """Linear or exponential distribution of the traces during the gradual drift

    :param tree_one: initial model
    :param tree_two: evolved model
    :param distribute_type: distribution type (linear, exponential)
    :param nu_traces: number of occurring traces during drift
    :return: An log only including the gradual drift part
    """
    result = EventLog()
    count = 0
    if distribute_type.strip() == 'linear':
        rest_one, rest_two, rounds, b = get_rest_parameter(nu_traces, distribute_type)
        x = 1
        most_one = rest_one + b * rounds
        most_two = rest_two + b * rounds
        while x <= rounds:
            if x == rounds:
                count = count + most_two
                log_t = semantics.generate_log(tree_two, most_two)
            else:
                count = count + (x * b)
                log_t = semantics.generate_log(tree_two, x * b)
            for t in log_t:
                result.append(t)
            if x == 1:
                count = count + most_one
                log_a = semantics.generate_log(tree_one, most_one)
            else:
                count = count + ((rounds - (x - 1)) * b)
                log_a = semantics.generate_log(tree_one, (rounds - (x - 1)) * b)
            for a in log_a:
                result.append(a)
            x = x + 1
    else:
        rest_one, rest_two, rounds, b = get_rest_parameter(nu_traces, distribute_type)
        x = 1
        most_one = rest_one + int(round(math.exp(rounds * b) + 0.0001))
        most_two = rest_two + int(round(math.exp(rounds * b) + 0.0001))
        while x <= rounds:
            if x == rounds:
                log_t = semantics.generate_log(tree_two, most_two)
            else:
                log_t = semantics.generate_log(tree_two, int(round(math.exp(x * b) + 0.0001)))
            for t in log_t:
                result.append(t)
            if x == 1:
                log_a = semantics.generate_log(tree_one, most_one)
            else:
                log_a = semantics.generate_log(tree_one, int(round(math.exp((rounds - (x - 1)) * b))))
            for a in log_a:
                result.append(a)
            x = x + 1
    return result



def get_rest_parameter(nu_traces, distribute_type):
    """ Calculation of the best parameters for the gradual drift.

    :param nu_traces: number of traces to be distributed
    :param distribute_type: mathematical type of distribution
    :return:
    """
    rests_one = []
    rests_two = []
    rounds = []
    nu_drift_model_one = int(round((nu_traces / 2) + 0.0001))
    nu_drift_model_two = nu_traces - nu_drift_model_one

    if distribute_type.strip() == 'exponential':
        b = 0.5
        while b <= 0.8:
            hel = 0
            rest_one = 1
            rest_two = 1
            round_l = 0
            while hel + int(round(math.exp((round_l + 1) * b) + 0.0001)) <= nu_drift_model_one:
                round_l = round_l + 1
                hel = hel + int(round(math.exp(round_l * b) + 0.0001))
                rest_one = nu_drift_model_one - hel
                rest_two = nu_drift_model_two - hel
            b = b + 0.1
            rests_one.append(rest_one)
            rests_two.append(rest_two)
            rounds.append(round_l)
    else:
        # linear distribution type
        b = 2
        while b < 6:
            hel = 0
            rest_one = 1
            rest_two = 1
            round_l = 0
            while hel + (round_l + 1) * b <= nu_drift_model_one:
                round_l = round_l + 1
                hel = hel + round_l * b
                rest_one = nu_drift_model_one - hel
                rest_two = nu_drift_model_two - hel
            b = b + 1
            rests_one.append(rest_one)
            rests_two.append(rest_two)
            rounds.append(round_l)
        return int(round(rests_one[numpy.argmin(rests_one)] + 0.0001)), int(
            round(rests_two[numpy.argmin(rests_one)] + 0.0001)), rounds[numpy.argmin(rests_one)], numpy.argmin(
            rests_one) + 2


    return rests_one[numpy.argmin(rests_one)], rests_two[numpy.argmin(rests_one)], rounds[numpy.argmin(rests_one)], (
                numpy.argmin(rests_one) * 0.1) + 0.5
