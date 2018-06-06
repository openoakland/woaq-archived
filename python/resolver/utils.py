from datetime import datetime, timedelta
import pandas as pd

def generate_tracker_initial_datetime(sensor_meta: pd.Series):
    sd_key = 'Test Start Date'
    tst = 'Test Start Time'
    
    # Example from data source '07/17/2014'
    raw_start_date = sensor_meta[sd_key]
    # Example from data source 12:40:35 PM
    raw_start_time = sensor_meta[tst]

    # Conjoin the date and the time data
    raw_full_dt = ' '.join([raw_start_date,
                            raw_start_time])

    # Now parse both, together to instantiate a
    # full date/time class object
    pattern = '%m/%d/%Y %I:%M:%S %p'
    aq_start_dt = datetime.strptime(raw_full_dt, pattern)
    
    # TODO: Determine the role that timezone plays in the
    #       log and trace data - does it need to be
    #       initialized or considered at any point?
    
    # This should be a fully instantiated datetime object
    return aq_start_dt