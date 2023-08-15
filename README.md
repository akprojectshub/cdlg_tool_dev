CDLG: Concept Drift Log Generator
====

About
---
This project is a second version 2.0 of the initial project CDLG tool that is described in the paper: _CDLG: A Tool for the Generation of Event Logs with Concept Drifts_ by Justus Grimm, Alexander Kraus, and Han van der Aa, submitted to the demo track of BPM 2022. The new version includes new features like multiple drift generation per log, as well as an automated evaluation approach that allows to compare a collection of logs to gold standards, as well as an overall more structured approach of the tool.
This submission comes with a corresponding [tutorial document](https://gitlab.uni-mannheim.de/processanalytics/cdlg_tool/-/blob/main/cdlg_tutorial.pdf) and [explanation video].
The primary contact for questions or comments regarding CDLG is Alexander Kraus: alexander[dot]kraus[at]uni-mannheim[dot]de 

**If you want to use parts of the approach in your project we refer to our [python package](https://gitlab.uni-mannheim.de/processanalytics/cdlg-package).**

Scope
---
This approach supports the generation of event logs with following features:
* Import of block-structured models (BPMN, Petri nets, Process trees)
* Concept drifts single or multiple (i.e. sudden-, gradual-, recurring-, incremental drift)
* Multiple drifts
* Noise introduction
* Random control-flow changes
* Controlled control-flow changes
Regarding the parameters of the logs generated, some files with predefined parameters have been pre-established. 
This approch also allows the automated evaluation of a collection of logs with actual drift by comparing it with the drifts in a tool simulated collection log. The comparison returns metrics such as:
* Precision = TP/(TP+FP)
* Recall = TP/(TP+FN)
* F1 Score = (2*precision*recall)/(precision+recall)
* Accuracy  = (TP+TN)/(TP+FN+TN+FP)
The collection of logs with actual drift should be provided by the user either in a CSV file, or via a collection class provided by the CDLG tool. Compared to the previous one the new version of the CDLG tool allows more features like generation of collection of logs with more than one drift, generation of collection of logs, and provide automated evalution that allow to compare two collection of logs with each other. 


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
The repository contains a tutorial document "cdlg_tutorial". This document explains the main use cases of the tool and provides a step-by-step guidance. In addition, the video document "cdlg_explanation_video.mp4" screencasts and demonstrates the tool.

### Execution Files ###

The following 5 Python files allow the generation of event logs with concept drifts and to evaluate the drifts of a collection of drifts provided by the user:
1. <code>configurations.py</code>Uncomment the file name from which the log generation parameters should be retrieved
2. <code>generate_collection_of_logs.py</code> A collection of logs will be generated with respect to the parameters specified previously
4. <code>automated_evaluation.py</code> 
5. <code>class_collection.py</code> 


### Run: Generation of logs ###
1. Specify the parameters parameter file to be used by uncommenting it in the file placed in /src/configurations.py. The files with the predefined settings could be found in src/input_parameters
2. Run the file generate_collection_of_logs.py which will generate a collection of logs that is conform to the parameters specified in step 1
3. The generated collection of logs can be accesses output/[collection_of_logs_id]


### Output ###
All generated event logs in XES format are saved with a corresponding sub-folder in _output.
Each collection of logs in addition to the XES files accompained by a CSV file that summarizes all the logs' data


### Run: Automated evaluation ###
1. Generate a collection of logs with detected drifts using the process described above
2. Provide actual log which can be provided either in a: 
    * CSV file. In this case the CSV file will be converted to a collection of logs class 
    * A collection of logs class object that is provided by the tool which can be directly used for the automated evaluation 
3. The output of the evaluation can be accessed in the folder output/Evaluation reports


**Note** once a new evaluation report is generated the previous one would be overwritten.




Reference
---
* [PM4Py](https://pm4py.fit.fraunhofer.de)


