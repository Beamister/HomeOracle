import os.path

DATA_DIRECTORY = 'Data'
DEFAULT_DATA_FILE = 'housing.csv'
DATA_DIRECTORY_PATH = os.path.join(os.path.split(__file__)[0], DATA_DIRECTORY)
DEFAULT_DATA_PATH = os.path.join(DATA_DIRECTORY_PATH, DEFAULT_DATA_FILE)
DEFAULT_DATA_HEADERS = ['Crime', 'Residential', 'Industrial', 'River Boundary', 'Nitric Oxide',
                        'Rooms', 'Pre 1940', 'Employment distance', 'Accessibility', 'Tax',
                        'Education', 'Black Population', 'Lower Status', 'Median Value']
DEFAULT_TARGET_HEADER = 'Median Value'

SUMMARY_ATTRIBUTES = ['Count', 'Mean', 'STD', 'Min', '25%', '50%', '75%', 'Max']


DEFAULT_3D_CAMERA = {'up': {'x': 0, 'y': 0, 'z': 1},
                     'center': {'x': 0, 'y': 0, 'z': 0},
                     'eye': {'x': 1, 'y': -2, 'z': 0.25}}


LAND_REGISTRY_URL = 'http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/' \
                    'pp-monthly-update-new-version.csv'
LAND_REGISTRY_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M'
LAND_REGISTRY_DATA_HEADERS = ['sale_id', 'price', 'date', 'postcode', 'property_type', 'new_property_flag', 'duration',
                              'PAON', 'SAON', 'street', 'locality', 'town/city', 'district', 'county', 'PDD_type',
                              'record_status']

STAGED_ENTRY_HEADERS = ['sale_id', 'date', 'value', 'PDD_type', 'postcode', 'new_property_flag', 'property_type',
                        'record_status']

CORE_METADATA_HEADERS = ['entry_id', 'sale_id', 'date', 'value', 'PDD_type', 'postcode', 'new_property_flag',
                         'property_type', 'tenure_type']
CORE_TARGET_HEADER = 'value'

AWS_REGION = 'eu-west-2'

# Dictionary of gss code table names to files
GSS_CODE_FILES = {
    'counties': 'counties.json',
    'county_electoral_divisions': 'ceds.json',
    'districts': 'districts.json',
    'wards': 'wards.json',
    'countries': 'countries.json',
    'regions': 'regions.json',
    'parliamentary_constituencies': 'constituencies.json',
    'eu_electoral_region': 'european_registers.json',
    'nuts_and_lau_areas': 'nuts.json',
    'parishes': 'parishes.json',
    'primary_care_trusts': 'pcts.json',
    'strategic_health_authorities': 'nhsHa.json',
    'clinical_commissioning_groups': 'ccgs.json',
    'lower_layer_super_output_areas': 'lsoa.json',
    'middle_layer_super_output_areas': 'msoa.json',
    'police_force': 'police_force.csv'
}

# Number of days to delay staging after sources should be ready, accounts for edge case issues to varying month lengths
# and delay in pulling sources
COMMIT_DELAY = 6

# Keep in length descending length order
FREQUENCY_DAY_COUNTS = {'yearly': 365, 'monthly': 30, 'weekly': 7, 'daily': 1}
# Dictionaries of names to view labels
FREQUENCIES = {'yearly': 'Yearly', 'monthly': 'Monthly', 'weekly': 'Weekly', 'daily': 'Daily'}

AREA_RESOLUTIONS = {'ward': 'Ward',
                    'cty': 'County',
                    'pcon': 'Constituency',
                    'ctry': 'Country',
                    'pfa': 'Police Force',
                    'european_electoral_register': 'European Electoral Area',
                    'rgn': 'Region',
                    'nuts': 'European Statistical Region',
                    'pct': 'Primary Care Trust',
                    'hlthau': 'Health Authority',
                    'ccg': 'Clinical Commissioning Group',
                    'lsoa11': 'Lower Layer Super Output Area',
                    'msoa11': 'Middle Layer Super Output Area',
                    'ced': 'District'}

SERVER_STATE_FILE = 'state.json'

MAX_TRAINING_ENTRIES = 100000
DEFAULT_SVM_DEGREE = 3

# Number of seconds for managers to wait before polling again after empty result
JOB_MANAGER_POLL_DELAY = 600
COMMIT_MANAGER_POLL_DELAY = 3600

BLUE = '#0074D9'
ORANGE = '#FF851B'
TIMESTAMP_FORMAT = '%Y-%m-%d-%H-%M-%S'
TIMESTAMP_FORMATTER = '{}-{:02}-{:02}-{:02}-{:02}-{:02}'
MAX_SOURCE_COLUMN_COUNT = 10
SECONDS_PER_HOUR = 3600

PULL_SOURCE_JOB = 'pull_source'
PULL_LAND_REGISTRY_JOB = 'pull_land_registry'
COMMIT_JOB = 'commit_entries'

LOCATION_ENGINE_CACHE_SIZE = 1024
GSS_CODE_TABLE_NAMES = []

PROPERTY_VIEW_MIN_INPUTS = 5
RDS_VIEW_ROW_COUNT = 100

MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiYmVhbW8iLCJhIjoiY2pzYnF2anVzMDdvcDQ0dGIwMDgxOXJmdSJ9.nchvAXMIixTwZWLcKxic6w'
DEFAULT_MAP_LATITUDE = 53.467
DEFAULT_MAP_LONGITUDE = -2.234

MODEL_TABLE_UPDATE_PERIOD = 10 * 1000