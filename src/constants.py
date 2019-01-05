import os.path

DATA_DIRECTORY = 'Data'
DEFAULT_DATA_FILE = 'housing.csv'
DATA_DIRECTORY_PATH = os.path.join(os.path.split(__file__)[0], DATA_DIRECTORY)
DEFAULT_DATA_PATH = os.path.join(DATA_DIRECTORY_PATH, DEFAULT_DATA_FILE)
DEFAULT_DATA_HEADERS = ['Crime', 'Residential', 'Industrial', 'River Boundary', 'Nitric Oxide',
                        'Rooms', 'Pre 1940', 'Employment distance', 'Accessibility', 'Tax',
                        'Education', 'Black Population', 'Lower Status', 'Median Value']

SUMMARY_ATTRIBUTES = ['Count', 'Mean', 'STD', 'Min', '25%', '50%', '75%', 'Max']


DEFAULT_3D_CAMERA =  {'up': {'x': 0, 'y': 0, 'z': 1},
                      'center': {'x': 0, 'y': 0, 'z': 0},
                      'eye': {'x': 1, 'y': -2, 'z': 0.25}}

LAND_REGISTRY_URL = 'http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-monthly-update-new-version.csv'
LAND_REGISTRY_DATA_HEADERS = ['sale_id', 'price', 'date', 'postcode', 'property_type', 'new_property_flag', 'duration', 'PAON',
                              'SAON', 'street', 'locality', 'town/city', 'district', 'county', 'PDD_type', 'record_status']
STAGED_ENTRY_HEADERS = ['sale_id', 'date', 'price', 'PDD_type', 'postcode', 'town/city', 'district', 'county', 'new_property_flag',
                        'property_type', 'tenure_type', 'record_status']

# Number of days to delay staging after sources should be ready, accounts for edge case issues to varying month lengths
# and delay in pulling sources
COMMIT_DELAY = 5

# Keep in length descending length order
FREQUENCY_DAY_COUNTS = {'yearly': 365, 'monthly': 30, 'weekly': 7, 'daily': 1}
# Dictionaries of names to view labels
FREQUENCIES = {'yearly': 'Yearly', 'monthly': 'Monthly', 'weekly': 'Weekly', 'daily': 'Daily'}
AREA_RESOLUTIONS = {'ward' : 'Ward', 'county' : 'County', 'parish' : 'Parish', 'constituency' : 'Constituency',
                    'police' : 'Police Force', 'individual' : 'Individual'}



BLUE = '#0074D9'
ORANGE = '#FF851B'
TIMESTAMP_FORMAT = '%Y-%m-%d-%H-%M-%S'
TIMESTAMP_FORMATTER = '{}-{:02}-{:02}-{:02}-{:02}-{:02}'
MAX_SOURCE_COLUMN_COUNT = 10
SECONDS_PER_HOUR = 3600

PULL_SOURCE_JOB = 'pull_source'
PULL_LAND_REGISTRY_JOB = 'pull_land_registry'
COMMIT_JOB = 'commit_entries'
