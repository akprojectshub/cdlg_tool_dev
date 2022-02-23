CDLG: Concept Drift Log Generator
====
___

Generation of event logs with concept drifts
---

This approach supports the generation of event logs with following features:
* Import of block-structured models (BPMN, Petri nets, Process trees)
* Concept drifts (i.e. sudden-, gradual-, recurring-, incremental drift)
* Multiple drifts
* Noise introduction
* Random control-flow changes
* Controlled control-flow changes

 
Installation
---
**The project requires python >= 3.9 and graphviz**

Install python [here](https://www.python.org/downloads/) and graphviz [here](https://graphviz.org/download/).

0. Optional: create a virtual environment 
1. Install the packages in requirements.txt: <code>pip install -r requirements.txt</code>

**Note:** the exact versions of the packages must be installed, as the versions of the dependencies have changed.
Otherwise, errors may occur.


Usage
---

### Execution Files ###

The following six Python files allow the generation of event logs with concept drifts:
1. <code>start_generator_terminal.py</code> starts the guided event log generation via the terminal 
2. <code>generate_log_sudden_drift_from_doc.py</code> generates an event log with a sudden drift (Parameters in _parameters_sudden_drift_)
3. <code>generate_log_gradual_drift_from_doc.py</code> generates an event log with a gradual drift (Parameters in _parameters_gradual_drift_)
4. <code>generate_log_recurring_drift_from_doc.py</code> generates an event log with a recurring drift (Parameters in _parameters_recurring_drift_)
5. <code>generate_log_incremental_drift_from_doc.py</code> generates an event log with an incremental drift (Parameters in _parameters_incremental_drift_)
6. <code>generate_collection_of_logs.py</code> generates a set of event logs with all drift types (Parameters in _parameters_logs_)

### Run ###
1. Specify the parameters in the corresponding text files placed in _Data/parameters_ for the execution files 2 - 6, if needed.
2. Run one project using <code>python _filename_ _[path_to_own_model_1]_ _[path_to_own_model_2]_</code>

**Note:** for the execution files 2 - 6 own models can be imported by specifying their file path after the execution file.
For 2 - 5 a maximum of two models are allowed and for 6 only one model is possible. 

### Input ###
It is optional to use your own models (BPMN model, Petri net, Process tree) in BPMN, PNML, or PTML format, which have to be block-structured.

**Note:** all models will be converted to process trees during execution.

### Output ###
All generated event logs in XES format and all process trees in PTML format are saved with a corresponding sub-folder in _Data/result_data_.
With the execution of 6 a CSV file so-called _gold_standard.csv_ is saved as well as a text file for each event log containing the drift configurations.

**Note:** after executing a particular project file, you should save the generated data in a different location, otherwise it will be overwritten when you execute it again.

Reference
---
* [PM4Py](https://pm4py.fit.fraunhofer.de)

Evaluation
---
Comprehensive Process Drift Detection with Visual Analytics (VDD technique) was used for the evaluation of CDLG.
The link to the GitHub repository can be found [here](https://github.com/yesanton/Process-Drift-Visualization-With-Declare).
The generated event logs by CDLG, which were used for the evaluation, are stored in the folder _'Data/evaluation'_.

 
