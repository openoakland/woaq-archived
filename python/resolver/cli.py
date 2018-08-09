import os

from .resolver import run

if __name__ == '__main__':
    # TODO: The cli.py will include arg parsing and related
    #       script components to instantiate the Resolver class with
    #       relation initialization components. It will, once initialized
    #       also call the transform and load processes, enabling
    #       command-line scripted ETL process abstraction.

    # Some presets just for dev purposes
    parent_dir = os.path.join('woaq', 'to_join')
    target_day = '07232014'
    target_day_dir = os.path.join(parent_dir, target_day)

    # Placeholder run method
    run(target_day_dir, 50)