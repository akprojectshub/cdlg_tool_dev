import os

from ConceptDrifts.without_drift import generate_log_without_drift
from Generators.event_logs_one_model import generate_logs_with_model
from Generators.event_logs_two_models import generate_logs_with_models
from Source.input_controller import input_yes_no, input_start, input_parameters, generate_tree_out_of_file, input_comp, \
    input_start_second, input_int, input_no_yes
from Source.process_tree_controller import generate_tree, visualise_tree, generate_specific_trees
from pm4py.objects.process_tree.exporter import exporter as ptml_exporter


def main():
    if not os.path.exists('Data/result_data'):
        os.makedirs('Data/result_data')
        os.makedirs('Data/result_data/terminal')
        os.makedirs('Data/result_data/terminal/event_logs')
        os.makedirs('Data/result_data/terminal/generated_models')
    elif not os.path.exists('Data/result_data/terminal'):
        os.makedirs('Data/result_data/terminal')
        os.makedirs('Data/result_data/terminal/event_logs')
        os.makedirs('Data/result_data/terminal/generated_models')
    elif not os.path.exists('Data/result_data/terminal'):
        os.makedirs('Data/result_data/terminal')
        os.makedirs('Data/result_data/terminal/event_logs')
        os.makedirs('Data/result_data/terminal/generated_models')
    print("--- GENERAL INPUT ---")
    print('The tool offers different paths to generate event logs with drifts.\n'
          '\t - import models: one or two own models can be imported,\n '
          '\t   whereby the BPMN models and Petri nets need to be block-structured.\n'
          '\t - random generated models: one or two process trees can be generated randomly.\n'
          'When using one model, it can evolve randomly or in a controlled manner.\n'
          'When using two models, the second model is/should be the already evolved version of the first model.\n'
          'Several event logs can be generated with one run of the application, and the parameters can be changed for each event log.\n')

    ev_log_drift = input_yes_no("Is an event log with a concept drift scenario required? [yes, no]: ")
    if ev_log_drift == 'yes':
        two_one_rand = input_start(
            'Import models or use randomly generated models [import, random]: ')
        if two_one_rand == 'import':
            imp = input_start_second(
                "Evolution of one imported model or use of two imported models [one_model, two_models]: ")
            if imp == 'one_model':
                tree_one = generate_tree_out_of_file(
                    "File path of the model, which has to be 'pnml', 'bpmn' or 'ptml' (e.g. 'Data/test_data/bpmn/model_00.bpmn'): ")
                nu_logs = input_int("Number of event logs to be generated (int): ")
                print(
                    "\nImported model made visible as a process tree. Please do not close it, as it is needed for further actions.")
                visualise_tree(tree_one)
                generate_logs_with_model(tree_one, nu_logs)
            elif imp == 'two_models':
                tree_one = generate_tree_out_of_file(
                    "File path of the first model, which has to be 'pnml', 'bpmn' or 'ptml' (e.g. 'Data/test_data/bpmn/model_00.bpmn'): ")
                tree_two = generate_tree_out_of_file(
                    "File path of the second model, which has to be 'pnml', 'bpmn' or 'ptml' (e.g. 'Data/test_data/bpmn/model_01.bpmn'): ")
                nu_logs = input_int("Number of event logs to be generated (int): ")
                generate_logs_with_models(tree_one, tree_two, nu_logs, False)
        elif two_one_rand == 'random':
            imp = input_start_second(
                "Evolution of one randomly generated model or use of two randomly generated models [one_model, two_models]: ")
            if imp == 'one_model':
                default = input_no_yes(
                    "Do you want to adjust the various settings/parameters for the process tree, which will be used to generate the model randomly [yes, no]? ")
                if default == 'yes':
                    parameters = input_parameters()
                    tree_ran = generate_tree(parameters)
                else:
                    str_clp = input_comp("Complexity of the process tree to be generated [simple, middle, complex]: ")
                    tree_ran = generate_specific_trees(str_clp)
                nu_logs = input_int("Number of event logs to be generated (int): ")
                ptml_exporter.apply(tree_ran, "Data/result_data/terminal/generated_models/random_initial_model.ptml")
                print(
                    "\nRandom generated model is made visible as a process tree. Please do not close it, as it is needed for further actions.")
                print(
                    "Random generated model 'random_initial_model' is saved in the folder 'Data/result_data/generated_tress'.")
                visualise_tree(tree_ran)
                generate_logs_with_model(tree_ran, nu_logs)
            elif imp == 'two_models':
                default = input_no_yes(
                    "Do you want to adjust the various settings/parameters for the process tree, which will be used to generate the model randomly [yes, no]? ")
                parameters = {}
                if default == 'yes':
                    parameters = input_parameters()
                    tree_ran_one = generate_tree(parameters)
                    tree_ran_two = generate_tree(parameters)
                else:
                    str_clp = input_comp("Complexity of the process trees to be generated [simple, middle, complex]: ")
                    tree_ran_one = generate_specific_trees(str_clp)
                    tree_ran_two = generate_specific_trees(str_clp)
                ptml_exporter.apply(tree_ran_one,
                                    "Data/result_data/terminal/generated_models/random_initial_model.ptml")
                ptml_exporter.apply(tree_ran_two,
                                    "Data/result_data/terminal/generated_models/random_evolved_model.ptml")
                nu_logs = input_int("Number of event logs to be generated (int): ")
                print("\nRandom generated models are made visible as process trees.")
                print(
                    "Random generated models 'random_initial_model' and 'random_evolved_model' are saved in the folder 'Data/result_data/generated_tress'.")
                visualise_tree(tree_ran_one)
                visualise_tree(tree_ran_two)
                generate_logs_with_models(tree_ran_one, tree_ran_two, True, nu_logs, parameters)
    else:
        imp_ran = input_start(
            'Import of one model or use of one randomly generated model for the generation of the event log [import, random]: ')
        if imp_ran == 'import':
            tree_one = generate_tree_out_of_file(
                "File path of the model, which has to be 'pnml', 'bpmn' or 'ptml' (e.g. 'Data/test_data/bpmn/model_00.bpmn'): ")
            nu_logs = input_int("Number of event logs to be generated (int): ")
            print("\nImported model is made visible as a process tree.")
            visualise_tree(tree_one)
            generate_log_without_drift(tree_one, nu_logs)
        else:
            default = input_no_yes(
                "Do you want to adjust the various settings/parameters for the process tree, which will be used to generate the model randomly [yes, no]? ")
            if default == 'yes':
                parameters = input_parameters()
                tree_ran = generate_tree(parameters)
            else:
                str_clp = input_comp("Complexity of the process tree to be generated [simple, middle, complex]: ")
                tree_ran = generate_specific_trees(str_clp)
            nu_logs = input_int("Number of event logs to be generated (int): ")
            ptml_exporter.apply(tree_ran,
                                "Data/result_data/terminal/generated_models/random_model_for_log_without_drift.ptml")
            print("\nRandom generated model is made visible as a process tree.")
            print(
                "Random generated model 'random_model_for_log_without_drift' is saved in the folder 'Data/result_data/generated_tress'.")
            visualise_tree(tree_ran)
            generate_log_without_drift(tree_ran, nu_logs)


if __name__ == '__main__':
    main()
