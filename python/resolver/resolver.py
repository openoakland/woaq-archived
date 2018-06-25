import calendar
from datetime import timedelta

import pandas as pd
from .load import load
from .utils import (extract_optimum_trace,
                    generate_tracker_initial_datetime,
                    pair_aq_with_gps)

# Note: This will be converted/upgraded perhaps to a class with
#       state in the future, but a more functional approach is more
#       straightforward (IMO) for a first pass
def run(target_day_dir: str, i_limit=None):
    # Read in all related/required values for a single
    # day (given data format)
    components = load(target_day_dir)

    # Parse the start time/date (all row times will be
    # this time plus the assessed time delta)
    init_dt = generate_tracker_initial_datetime(components['sensor'])

    # Iterate through the rows from the air quality readings
    # and find the closest GPS trace for each value
    results_rows = []
    aqdf = components['air_quality'].reset_index(drop=True)
    for i, row in aqdf.iterrows():
        # Used for debugging purposes, to not have to
        # go through all rows (and just evaluate n supplied)
        if i_limit is not None and i > i_limit:
            break

        # First, calculate the time (utc value)
        seconds_add = int(row['time_elapsed'])
        new_time = init_dt + timedelta(seconds=seconds_add)
        utc_val = str(calendar.timegm(new_time.utctimetuple()))

        # I'm not yet clear on what hte filter value is, so
        # I do not see how we correctly calculate that value
        filter_val = None

        # Mass is a direct transfer from the data
        # and will be used for the "pm" value
        pm_val = float(row['mass'])

        # This operation returns two items, both the auto-selected
        # best GPS trace, and a bunch of other data that
        # we could save and use for improved analyses in the future
        rel_trace = extract_optimum_trace(trace=components['trace'],
                                          new_time=new_time,
                                          tolerance_seconds=10)

        lat_val = rel_trace['selected'].latitude
        lon_val = rel_trace['selected'].longitude

        # Goal: Desired column schema:
        # - utc
        # - filter
        # - pm
        # - lat
        # - lon
        # - device
        results_rows.append({
            'utc': utc_val,
            'filter': filter_val,
            'pm': pm_val,
            'lat': lat_val,
            'lon': lon_val,
            'device': components['sensor']['Instrument Name']})

    # From the resulting rows' schema, convert to a pandas DataFrame
    results_df = pd.DataFrame(results_rows)

    # TODO: Improve this step
    # Finally, save the outputs somewhere
    results_df.to_csv('{}/paired_results.csv'.format(target_day_dir))
    components = load(target_day_dir)