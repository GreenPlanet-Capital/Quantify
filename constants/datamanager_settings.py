import sys, os
def setup_datamgr_settings():
    sys.path.append('DataManager') # Insert DataManager to path

    # Set env variable to absolute path of datamanager folder
    os.environ['DATAMGR_ABS_PATH'] = os.path.join(os.getcwd(), 'DataManager')
    print(os.environ['DATAMGR_ABS_PATH'])