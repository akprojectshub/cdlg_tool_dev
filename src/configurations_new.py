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

# Incremental evolution parameters
INCREMENTAL_EVOLUTION_SCOPE = [0.05, 0.15]

folders = dict(
    input=os.path.join('data/parameters'),
    output=os.path.join('data/parameters'),
    input_parameters=os.path.join('data/parameters')
)

drifts = dict(
    sudden='',
    gradual='',
    incremental='',
    recurring=''
)

other = dict(
    first_timestamp = '2020/01/01 08:00:00',
)

file_name = dict(
    drift_info_csv = 'drift_info_summary'
)