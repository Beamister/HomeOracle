from functools import lru_cache
from constants import *
import boto3


class LocationEngine:

    def __init__(self, database_engine):
        self.cache = lru_cache(LOCATION_ENGINE_CACHE_SIZE)
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        self.tables = {}
        for table_name in GSS_CODE_TABLE_NAMES:
            self.tables[table_name] = dynamodb.Table(table_name)
        self.last_check_resolution = ''
        self.check_list = []

    # TODO - loads the list of locations at the given resolution
    def load_check_list(self, resolution):
        pass

    # TODO - converts a given postcode to the area it in is within at the given resolution
    def convert_postcode(self, postcode, resolution):
        return ''

    # TODO - checks if a given string is a GSS code, returns true if so, else false
    def is_gss_code(self, string):
        return True

    # TODO - converts a gss code to a human readable name, if resolution is given then only
    #  relevant conversion table needs to be checked, None if no match found
    def convert_gss_code(self, code, resolution=None):
        return None

    def check_location(self, location, resolution):
        if resolution != self.last_check_resolution:
            self.load_check_list(resolution)
        if location in self.check_list:
            return location
        else:
            #TODO - check if the given location is similar to a location in the check list,
            # if so return the corrected spelling, else return None
            pass
