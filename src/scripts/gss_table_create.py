import boto3

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

AWS_REGION = 'eu-west-2'

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
for table_name in GSS_CODE_FILES.keys():
    table = dynamodb.create_table(TableName=table_name,
                                  KeySchema=[
                                      {
                                          'AttributeName': 'gss_code',
                                          'KeyType': 'HASH'  # Partition key
                                      }
                                  ],
                                  AttributeDefinitions=[
                                      {
                                          'AttributeName': 'gss_code',
                                          'AttributeType': 'S'
                                      }
                                  ],
                                  ProvisionedThroughput=
                                  {
                                      'ReadCapacityUnits': 5,
                                      'WriteCapacityUnits': 5
                                  }
                                  )
