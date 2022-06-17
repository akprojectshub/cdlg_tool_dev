CDLG: Concept Drift Log Generator
====

About
---
This repository contains the prototype of the CDLG tool described in the paper: _CDLG: A Tool for the Generation of Event Logs with Concept Drifts_ by Justus Grimm, Alexander Kraus, and Han van der Aa, submitted to the demo track of BPM 2022.
This submission comes with a corresponding [tutorial document](https://gitlab.uni-mannheim.de/processanalytics/cdlg_tool/-/blob/main/cdlg_tutorial.pdf) and [explanation video](https://gitlab.uni-mannheim.de/processanalytics/cdlg_tool/-/blob/main/cdlg_explanation_video.mp4).

The primary contact for questions or comments regarding CDLG is Alexander Kraus: alexander[dot]kraus[at]uni-mannheim[dot]de 

**If you want to use parts of the approach in your project we refer to our [python package](https://gitlab.uni-mannheim.de/processanalytics/cdlg-package).**

Scope
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
The repository contains a tutorial document "cdlg_tutorial". This document explains the main use cases of the tool and provided a step-by-step guidance. In addition, the video document "cdlg_explanation_video.mp4" screencasts and demonstrates the tool.

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
For 2 - 4 a maximum of two models are allowed and for 5 & 6 only one model is possible. 

### Input ###
It is optional to use your own models (BPMN model, Petri net, Process tree) in BPMN, PNML, or PTML format, which have to be block-structured.

**Note:** all models will be converted to process trees during execution.

### Output ###
All generated event logs in XES format are saved with a corresponding sub-folder in _Data/result_data_.
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

 
