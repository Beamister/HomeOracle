import os.path

DATA_DIRECTORY = "Data"
DEFAULT_DATA_FILE = "housing.csv"
DATA_DIRECTORY_PATH = os.path.join(os.path.split(__file__)[0], DATA_DIRECTORY)
DEFAULT_DATA_PATH = os.path.join(DATA_DIRECTORY_PATH, DEFAULT_DATA_FILE)
DEFAULT_DATA_HEADERS = ["Crime", "Residential", "Industrial", "River Boundary", "Nitric Oxide",
                        "Rooms", "Pre 1940", "Employment distance", "Accessibility", "Tax",
                        "Education", "Black Population", "Lower Status", "Median Value"]

SUMMARY_ATTRIBUTES = ['Count', 'Mean', 'STD', 'Min', '25%', '50%', '75%', 'Max']


default_3d_camera =  {'up': {'x': 0, 'y': 0, 'z': 1},
                      'center': {'x': 0, 'y': 0, 'z': 0},
                      'eye': {'x': 1, 'y': -2, 'z': 0.25}}


BLUE = '#0074D9'
ORANGE = '#FF851B'
TIMESTAMP_FORMAT = '%Y-%m-%d-%H-%M-%S'
TIMESTAMP_FORMATTER = '{}-{:02}-{:02}-{:02}-{:02}-{:02}'
MAX_SOURCE_COLUMN_COUNT = 10
SECONDS_PER_HOUR = 3600

PULL_INDICATOR_JOB = 'pull_indicator'
PULL_LAND_REGISTRY_JOB = 'pull_land_registry'
UPDATE_DATA_SET_JOB = 'update_data_set'
