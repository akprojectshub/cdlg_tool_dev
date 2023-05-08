import os

###################################################################
# DIRECTORIES
###################################################################
DEFAULT_OUTPUT_DIR = os.path.join('output')
DEFAULT_PARAMETER_DIR = os.path.join('src/input_parameters/')
#PARAMETER_NAME = 'default'
#PARAMETER_NAME = 'eval_00_simple_1_wo_noise'
#PARAMETER_NAME = 'eval_01_simple_2_wo_noise'
#PARAMETER_NAME = 'eval_01_simple_2_w_noise_0.1'
#PARAMETER_NAME = 'eval_01_simple_2_wo_noise_simple_complexity'
#PARAMETER_NAME = 'eval_02_simple_3_wo_noise'
#PARAMETER_NAME = 'eval_03_simple_4_wo_noise'
#PARAMETER_NAME = 'eval_04_simple_1_w_noise_0.1'
#PARAMETER_NAME = 'eval_04_simple_4_w_noise_0.1'
#PARAMETER_NAME = 'eval_04_simple_4_w_noise_0.2'
#PARAMETER_NAME = 'eval_04_simple_4_w_noise_0.3'
#PARAMETER_NAME = 'eval_04_simple_4_w_noise_0.4'
#PARAMETER_NAME = 'eval_04_simple_4_w_noise_0.5'

PARAMETER_NAME = 'experiments_simple'

###################################################################
# FILE NAMES
###################################################################
# First time stamp of each event log
FIRST_TIMESTAMP = '2020/01/01 08:00:00'
# Incremental evolution parameters
INCREMENTAL_EVOLUTION_SCOPE = [0.05, 0.15]
