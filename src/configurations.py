import os

###################################################################
# DIRECTORIES
###################################################################
DEFAULT_OUTPUT_DIR = os.path.join('output')
DEFAULT_PARAMETER_DIR = os.path.join('src/input_parameters/')
#PARAMETER_NAME = 'default'
#PARAMETER_NAME = 'experiments_simple'
PARAMETER_NAME = 'experiments_all_types'

###################################################################
# FILE NAMES
###################################################################
# First time stamp of each event log
FIRST_TIMESTAMP = '2020/01/01 08:00:00'
# Incremental evolution parameters
INCREMENTAL_EVOLUTION_SCOPE = [0.05, 0.15]
