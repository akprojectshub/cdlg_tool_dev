import os

###################################################################
# DIRECTORIES
###################################################################
#DEFAULT_PARAMETER_DIR = os.path.join('data/parameters')
#DEFAULT_LOG_COLLECTION_OUTPUT_DIR = os.path.join('data/generated_collections')
DEFAULT_LOG_COLLECTION_OUTPUT_DIR = os.path.join('output')
DEFAULT_PARAMETER_DIR = os.path.join('src/input_parameters/')

###################################################################
# FILE NAMES
###################################################################
PAR_LOG_COLLECTION = 'default'

# First time stamp of each event log
FIRST_TIMESTAMP = '2020/01/01 08:00:00'

# Incremental evolution parameters
INCREMENTAL_EVOLUTION_SCOPE = [0.05, 0.15]

paths = dict(
    input_folder=os.path.join('data/parameters'),
    output_folder=os.path.join('data/parameters'),
    input_configurations=os.path.join('data/parameters')
)

drifts = dict(
    sudden='',
    gradual='',
    incremental='',
    recurring=''
)
