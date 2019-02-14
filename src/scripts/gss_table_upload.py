import boto3
import simplejson
import pandas

GSS_CODE_FILES = {
                  'counties': 'counties.json', 'county_elctoral_divisions': 'ceds.json', 'districts': 'districts.json',
                  'wards': 'wards.json', 'countries': 'countries.json', 'regions': 'regions.json',
                  'parliamentary_constituencies': 'constituencies.json',
                  'eu_electoral_region': 'european_registers.json', 'nuts_and_lau_areas': 'nuts.json',
                  'parishes': 'parishes.json', 'primary_care_trusts': 'pcts.json',
                  'strategic_health_authorities': 'nhsHa.json', 'clinical_commissioning_groups': 'ccgs.json',
                  'lower_layer_super_output_areas': 'lsoa.json','middle_layer_super_output_areas': 'msoa.json',
                  'police_force': 'police_force.csv'
                }
AWS_REGION = 'eu-west-2'

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
for table_name in GSS_CODE_FILES.keys():
    print(f'Uploading to {table_name}')
    filename = 'Data/GSS_to_names/' + GSS_CODE_FILES[table_name]
    file = open(filename)
    if '.json' in filename:
        json = simplejson.load(file)
        gss_codes = list(json.keys())
        # Check if file has code and name dictionaries as values for each gss code
        if isinstance(json[list(json.keys())[0]], dict):
            names = []
            for code in gss_codes:
                names.append(json[code]['name'])
        else:
            names = list(json.values())
    elif '.csv' in filename:
        csv_data = pandas.read_csv(filename)
        gss_codes = list(csv_data.iloc[:, 0])
        names = list(csv_data.iloc[:, 1])
    else:
        raise Exception('unknown file type: ' + filename)
    file.close()
    table = dynamodb.Table(table_name)
    with table.batch_writer() as batch:
        for index in range(len(gss_codes)):
            batch.put_item(Item=
                {
                    'gss_code': str(gss_codes[index]),
                    'human_readable_name': str(names[index]),
                }
            )