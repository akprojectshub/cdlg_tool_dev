import os

###################################################################
# DIRECTORIES
###################################################################
DEFAULT_PARAMETER_DIR = os.path.join('data/parameters')
DEFAULT_LOG_COLLECTION_OUTPUT_DIR = os.path.join('data/generated_collections')



###################################################################
# FILE NAMES
###################################################################
PAR_LOG_COLLECTION = 'parameters_log_collection'


# First time stamp of each event log
FIRST_TIMESTAMP = '2020/01/01 08:00:00'

# Incremental evolution parameters
INCREMENTAL_EVOLUTION_SCOPE = [0.05, 0.15]