from controllers.event_log_controller import *
from pm4py.objects.process_tree import semantics
from controllers.input_controller import input_percentage, input_int, input_end
import math
from controllers.utilities import select_random, ChangeTypes
from controllers.control_flow_controller import evolve_tree_randomly
from pm4py import play_out
from pm4py.algo.simulation.playout.process_tree.variants.topbottom import Parameters


def add_sudden_change(log, drift_instance, paremeters):
    """ Include an additional sudden drift to an event log
    :param log: initial event log
    :param process_tree: evolved tree version used to generate the next process model version
    :param num_traces: number of traces to added to the intial event log from the new process tree
    :return: event log with added additional sudden drift
    """
    tree_previous = drift_instance.get_previous_process_tree()
    ran_evolve = select_random(paremeters.Process_tree_evolution_proportion, option='uniform')
    tree_new, deleted_acs, added_acs, moved_acs = evolve_tree_randomly(tree_previous, ran_evolve)
    num_traces = select_random(paremeters.Number_traces_per_process_model_version, option='uniform_int')
    #log_two = play_out(tree_new, parameters={Parameters.NO_TRACES: num_traces})
    log_two = semantics.generate_log(tree_new, num_traces)
    log_extended = combine_two_logs(log, log_two)

    # Update drift infos
    drift_instance.add_process_tree(tree_new)
    change_trace_index = len(log) + 1
    drift_instance.add_change_info(change_trace_index,
                                   ChangeTypes.sudden.value,
                                   tree_previous, tree_new,
                                   deleted_acs, added_acs, moved_acs)

    return log_extended, drift_instance


def add_gradual_change(event_log, drift_instance, paremeters):
    """ Generation of an event log with a gradual drift

    :param tree_one: initial version of the process tree
    :param tree_two: evolved version of the process tree
    :param nu_traces: number of traces in the log
    :param start_point: start change point of the drift in percentage
    :param end_point: end change point of the drift in percentage
    :param distribution_type: type of distribution of the traces during the drift (linear, exponential)
    :return: event log with gradual drift
    """


    gradual_type = select_random(paremeters.Gradual_drift_type, option='random')
    ran_evolve = select_random(paremeters.Process_tree_evolution_proportion, option='uniform')
    # TODO: each trace should be associated with a process tree id. Then, previous tree is based on the last trace
    tree_previous = drift_instance.get_previous_process_tree()
    tree_new, deleted_acs, added_acs, moved_acs = evolve_tree_randomly(tree_previous, ran_evolve)
    num_traces = select_random(paremeters.Number_traces_per_process_model_version, option='uniform_int')
    #log_two = play_out(tree_new, parameters={Parameters.NO_TRACES: num_traces})
    log_two = semantics.generate_log(tree_new, num_traces)
    num_traces_gradual_phase = select_random(paremeters.Number_traces_for_gradual_change, option='uniform_int')
    # TODO: keep track of all trace ids
    log_transition = distribute_traces(tree_previous, tree_new, gradual_type, num_traces_gradual_phase)
    log_with_transition = combine_two_logs(event_log, log_transition)
    log_extended = combine_two_logs(log_with_transition, log_two)

    # Update drift infos
    drift_instance.add_process_tree(tree_new)
    change_trace_index = [len(event_log) + 1, len(log_with_transition) +1]
    drift_instance.add_change_info(change_trace_index,
                                   ChangeTypes.gradual.value,
                                   tree_previous, tree_new,
                                   deleted_acs, added_acs, moved_acs)

    return log_extended, drift_instance


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


def additional_gradual_drift_in_log(log, tree_one, tree_two):
    """ Including an additional gradual drift into an event log

    :param log: event log including a drift
    :param tree_one: predecessor version of the process tree version tree_two
    :param tree_two: evolved tree version
    :return: event log with an additional gradual drift
    """
    add_end = input_end("Adding the additional gradual drift at the end of the log or into the log [end, into]? ")
    dr_s = "drift perspective: control-flow; drift type: gradual; drift specific information: "
    if add_end == 'into':
        start_point = input_percentage("Starting point of the drift (0 < x < 1): ")
        end_point = input_percentage("Ending point of the drift (0 < x < 1): ")
        num_traces = length_of_log(log)
        distribution_type = input_typ_gradual(
            "Method for distributing the traces during the gradual drift [linear, exponential]: ")
        dr_s += distribution_type + " distribution; "
        result = EventLog()
        start = int(round((num_traces * start_point + 0.0001)))
        end = int(round((num_traces * end_point + 0.0001)))
        nu_traces_for_drift = int(round(num_traces * (end_point - start_point) + 0.0001))
        proportion = (end_point - start_point) / 2
        log_two_traces = num_traces - int(round((start_point + proportion) * num_traces + 0.0001))
        log_two = semantics.generate_log(tree_two, log_two_traces)
        p = 0
        z = 0
        for trace in log:
            if p < start:
                result.append(trace)
                p = p + 1
                z = z + 1
            else:
                break
        i = 0
        if distribution_type == 'linear':
            rest, rest_un, rounds, b = get_rest_parameter(nu_traces_for_drift, 'linear')
            most_one = rest + b * rounds
            most_two = rest_un + b * rounds
            x = 1
            l = most_one
            while z < end and x <= rounds:
                k = 0
                m = 0
                j = b * x
                for trace in log_two:
                    if (k == i and m < j and x != rounds) or (x == rounds and m < most_two and k == i):
                        result.append(trace)
                        k = k + 1
                        i = i + 1
                        m = m + 1
                        z = z + 1
                    else:
                        k = k + 1
                n = 0
                h = 0
                if x != 1:
                    l = (b * (rounds - (x - 1)))
                for trace in log:
                    if (n == z and h < l and x != 1) or (x == 1 and h < most_one and n == z):
                        result.append(trace)
                        n = n + 1
                        h = h + 1
                        z = z + 1
                    else:
                        n = n + 1
                x = x + 1
        else:
            rest, rest_un, rounds, b = get_rest_parameter(nu_traces_for_drift, 'exponential')
            most_one = int(round(rest + math.exp(rounds * b) + 0.0001))
            most_two = int(round(rest_un + math.exp(rounds * b) + 0.0001))
            x = 1
            l = most_one
            while z < end and x <= rounds:
                k = 0
                m = 0
                j = int(round(math.exp(x * b) + 0.0001))
                for trace in log_two:
                    if (k == i and m < j and x != rounds) or (x == rounds and m < most_two and k == i):
                        result.append(trace)
                        k = k + 1
                        i = i + 1
                        m = m + 1
                        z = z + 1
                    else:
                        k = k + 1
                n = 0
                h = 0
                if x != 1:
                    l = int(round(math.exp((rounds - (x - 1)) * b) + 0.0001))
                for trace in log:
                    if (n == z and h < l and x != 1) or (x == 1 and h < most_one and n == z):
                        result.append(trace)
                        n = n + 1
                        h = h + 1
                        z = z + 1
                    else:
                        n = n + 1
                x = x + 1
        o = 0
        for trace in log_two:
            if o == i and z < num_traces:
                result.append(trace)
                z = z + 1
                o = o + 1
                i = i + 1
            else:
                o = o + 1
    else:
        nu_add_traces = input_int(
            "Number of additional traces of the gradual drift to be added at the end of the event log (int): ")
        nu_new_model_traces = input_int(
            "Number of additional traces of the new model to be added after the drift occurred (int): ")
        distribution_type = input_typ_gradual(
            "Method for distributing the traces during the gradual drift [linear, exponential]: ")
        dr_s = "drift perspective: control-flow; drift type: gradual; drift specific information: " + distribution_type + " distribution; "
        start = length_of_log(log)
        end = start + nu_add_traces
        log_drift = distribute_traces(tree_one, tree_two, distribution_type, nu_add_traces)
        log_with_drift = combine_two_logs(log, log_drift)
        log_new = semantics.generate_log(tree_two, nu_new_model_traces)
        result = combine_two_logs(log_with_drift, log_new)
    drift_data = {'d': dr_s, 't': [start, end]}
    return result, drift_data


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
    if distribute_type.strip() == 'linear':
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
    else:
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
    return rests_one[numpy.argmin(rests_one)], rests_two[numpy.argmin(rests_one)], rounds[numpy.argmin(rests_one)], (
                numpy.argmin(rests_one) * 0.1) + 0.5
