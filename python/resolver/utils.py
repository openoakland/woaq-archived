from datetime import datetime

import pandas as pd
import pytz


class NoValidTimes(Exception):
    pass

class OptimumTracePairDetails(abc.ABC):
    def __init__(self,
                 prev_timestamp: Union[datetime.time, None],
                 next_timestamp: Union[datetime.time, None],
                 
                 # latitude, longitude
                 prev_location: Union[List[float], None],
                 next_location: Union[List[float], None],
                 
                 percent_between: Union[float, None]):
        
        self.prev_timestamp = prev_timestamp
        self.next_timestamp = next_timestamp
        
        self.prev_location = prev_location
        self.next_location = next_location
        
        self.percent_between = percent_between
        
    def as_dict(self):
        # Assemble a fresh dictionary contained
        # related variables
        rd = dict()
        rd['prev_timestamp'] = prev_timestamp
        rd['next_timestamp'] = next_timestamp
        rd['prev_location'] = prev_location
        rd['next_location'] = next_location
        rd['percent_between'] = percent_between
        return rd


def _produce_timestamps(r):
    # Take in a row and return a padnas Timestamp
    return pd.Timestamp(f'{str(r.datestamp)}  {str(r.timestamp)}')


def extract_optimum_trace(
        trace: pd.DataFrame,
        new_time: datetime.time,
        tolerance_seconds: int):
    # Initialize reference variables used in this step
    most_recent_in_past = None
    soonest_in_future = None

    # Next generate a mask based on the report time
    mask = trace['timestamp'] >= new_time.time()

    # Now, we want two subdataframes, a "before" and an "after"
    # based on the time series data
    sub_before = trace[~mask]
    # For both, we only care if there are any valid rows here
    if len(sub_before):
        ts_before = sub_before.apply(_produce_timestamps, axis=1)
        most_recent_in_past = sub_before.iloc[ts_before.idxmax()].squeeze()

    # And one more, for the after times
    sub_after = trace[mask]
    if len(sub_after):
        ts_after = sub_after.apply(_produce_timestamps, axis=1)
        soonest_in_future = sub_after.iloc[ts_after.idxmin()].squeeze()

    # Sanity check that we have something to work with
    if most_recent_in_past is None and soonest_in_future is None:
        raise NoValidTimes('Timeseries request generated no valid rows to evalaute')

    # At this point, we have a choice: return the before
    # or after if only one exists...
    if most_recent_in_past is None:
        return {
            'selected': soonest_in_future,
            'more_details': OptimumTracePairDetails(
                prev_timestamp=None,
                next_timestamp=soonest_in_future['timestamp'],
                prev_location=None,
                next_location=[soonest_in_future.latitude,
                               soonest_in_future.longitude],
                percent_between=None)}

    if soonest_in_future is None:
        return {
            'selected': most_recent_in_past,
            'more_details': OptimumTracePairDetails(
                prev_timestamp=most_recent_in_past['timestamp'],
                next_timestamp=None,
                prev_location=[most_recent_in_past.latitude,
                               most_recent_in_past.longitude],
                next_location=None,
                percent_between=None)}

    # Or, try and pick the time that is closest,
    # based on the threshold
    
    # First we want to check to see if there is a nearest in future tool
    nt = new_time.time()
    sf = soonest_in_future['timestamp']
    enter_timedelta = timedelta(hours=nt.hour, minutes=nt.minute, seconds=nt.second)
    exit_td_sf = timedelta(hours=sf.hour, minutes=sf.minute, seconds=sf.second)
    sf_diff = exit_td_sf - enter_timedelta
    
    # If the upcoming trace is within a margin of
    # tolerance, then we should pick that one
    if sf_diff.seconds <= tolerance_seconds:
        return soonest_in_future
    
    # At this point, we should not automatically choose to return the previous time
    # because, if it is egregiously behind, we might opt to choose the future time
    # Also check the nearest in the past, one, too
    rp = most_recent_in_past['timestamp']
    exit_td_rp = timedelta(hours=rp.hour, minutes=rp.minute, seconds=rp.second)
    rp_diff = enter_timedelta - exit_td_rp
    
    # At this point, we have two time differences:
    # 1. rp_diff: Time since the last recorded timestamp
    # 2. sf_diff: Time until the next recorded timestamp
    
    # We first want to compute what "percent" of the way between
    # the two time points we are at
    pct_from_rp_to_next_time = round(rp_diff / (rp_diff + sf_diff), 3)
    
    # Using pct_from_rp_to_next_time, we pick the time that is closest
    # and record the percentage offset, so that future postprocesses
    # can utilize this data to effectively create a linearly
    # referenced point values between connected timestamp edges
    otp = OptimumTracePairDetails(
        prev_timestamp=rp,
        next_timestamp=sf,
        prev_location=[most_recent_in_past.latitude,
                       most_recent_in_past.longitude],
        next_location=[soonest_in_future.latitude,
                       soonest_in_future.longitude],
        percent_between=pct_from_rp_to_next_time)
    
    # Select the one that the timestamp
    # falls closes to
    if pct_from_rp_to_next_time < 0.5:
        sel = most_recent_in_past
    else:
        sel = soonest_in_future

    # Finally, we can return the context via
    # the more details class
    return {'selected': sel, 'more_details': otp}


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
    

    # Adjust the timezone from LA to UTC
    og_timezone = pytz.timezone('America/Los_Angeles')
    adjusted_time = og_timezone.localize(aq_start_dt).astimezone(pytz.UTC) 
    
    # This should be a fully instantiated datetime object
    return adjusted_time
