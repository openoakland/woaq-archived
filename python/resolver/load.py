from typing import Dict
from io import StringIO
import pandas as pd

def _get_ends_with(target_dir: str, ftype: str) -> str:
    # This method is premised on the assumption that each of these dailies
    # directories have 2 files in them: 
    # 1. .csv
    # 2. .log
    # And we just want the one that is specified by ftype
    select = None
    for file in os.listdir(target_dir):
        if file.endswith(ftype):
            select = file
    return select
    

def load(target_day_dir: str) -> Dict[str, pd.DataFrame]:
    # Initialize all target output values at the top
    sensor_data = None
    aq_data = None
    gps_data = None
    
    # Utilize helper method to generate the path to the log and csv files
    aq_filepath = os.path.join(target_day_dir,
                               _get_ends_with(target_day_dir, '.csv'))
    gps_filepath = os.path.join(target_day_dir,
                                _get_ends_with(target_day_dir, '.log'))

    # Two operations, both sort of hacks, that read in the relevant
    # file and process them to produce the desired output files
    with open(aq_filepath, 'r') as f:
        all_lines = [x for x in f]

        sio = StringIO('\n'.join(all_lines[:18]))
        # A series of contortions in pandas to convert the top
        # 19 rows to a more key-value like data store (in this case,
        # a pandas Series, which behaves a lot like a Python dict)
        sensor_data = pd.read_csv(sio, header=None)
        sensor_data = sensor_data.set_index(0)
        sensor_data = sensor_data.T.squeeze()

        sio = StringIO('\n'.join(all_lines[18:]))
        aq_data = pd.read_csv(sio)
        aq_data.columns = ['time_elapsed', 'mass', 'alarms', 'errors']

    with open(gps_filepath, 'r') as f:
        gps_data = pd.read_csv(f)
    
    # TODO: Validation of these desired datasets is critical
    #       in the future to avoid downstream issues
    return {
        'sensor': sensor_data,
        'air_quality': aq_data,
        'trace': gps_data}