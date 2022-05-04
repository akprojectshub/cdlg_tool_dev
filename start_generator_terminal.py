import os

from Generators.event_logs_one_model import generate_logs_with_model
from Generators.event_logs_two_models import generate_logs_with_models
from Source.input_controller import input_start, input_parameters, generate_tree_out_of_file, input_comp, \
    input_start_second, input_no_yes
from Source.process_tree_controller import generate_tree, generate_specific_trees


def main():
    if not os.path.exists('Data/result_data'):
        os.makedirs('Data/result_data')
        os.makedirs('Data/result_data/terminal')
    elif not os.path.exists('Data/result_data/terminal'):
        os.makedirs('Data/result_data/terminal')
    print("--- GENERAL INPUT ---")
    print('The tool offers different paths to generate event logs with drifts.\n'
          '\t - import models: one or two own models can be imported,\n '
          '\t   whereby the BPMN models and Petri nets need to be block-structured.\n'
          '\t - random generated models: one or two process trees can be generated randomly.\n'
          'When using one model, it can evolve randomly or in a controlled manner.\n'
          'When using two models, the second model is/should be the already evolved version of the first model.\n'
          'Several event logs can be generated with one run of the application, and the parameters can be changed for each event log.\n\n'
          'Press ENTER for an interaction to set a default value.\n'
          'Press CTRL+C to interrupt the tool\'s execution.\n'
          )

    two_one_rand = input_start(
        'Import models or use randomly generated models [import, random]: ')
    if two_one_rand == 'import':
        imp = input_start_second(
            "Evolution of one imported model or use of two imported models [one_model, two_models]: ")
        if imp == 'one_model':
            tree_one = generate_tree_out_of_file(
                "File path of the model, which has to be 'pnml', 'bpmn' or 'ptml' (e.g. 'Data/test_data/bpmn/model_00.bpmn'): ")
            generate_logs_with_model(tree_one)
        elif imp == 'two_models':
            tree_one = generate_tree_out_of_file(
                "File path of the first model, which has to be 'pnml', 'bpmn' or 'ptml' (e.g. 'Data/test_data/bpmn/model_00.bpmn'): ")
            tree_two = generate_tree_out_of_file(
                "File path of the second model, which has to be 'pnml', 'bpmn' or 'ptml' (e.g. 'Data/test_data/bpmn/model_01.bpmn'): ")
            generate_logs_with_models(tree_one, tree_two, False)
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
            generate_logs_with_model(tree_ran)
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
            generate_logs_with_models(tree_ran_one, tree_ran_two, True, parameters)


if __name__ == '__main__':
    main()

