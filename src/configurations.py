import os

# Default directories
DEFAULT_OUTPUT_DIR = os.path.join('output')
DEFAULT_PARAMETER_DIR = os.path.join('src/input_parameters/')
PARAMETER_NAME = 'supervised_cdd' ## 'default'
# First time stamp of each event log
FIRST_TIMESTAMP = '2023/01/01 08:00:00'
# Incremental evolution parameters for incremental drifts
INCREMENTAL_EVOLUTION_SCOPE = [0.05, 0.10]
