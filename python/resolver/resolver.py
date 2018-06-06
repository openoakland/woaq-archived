from .load import load
from .utils import generate_tracker_initial_datetime

# Note: This will be converted/upgraded perhaps to a class with
#       state in the future, but a more functional approach is more
#       straightforward (IMO) for a first pass
def run(target_day_dir: str):
    components = load(target_day_dir)
    generate_tracker_initial_datetime(components['sensor'])