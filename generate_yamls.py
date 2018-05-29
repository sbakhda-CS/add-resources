from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import csv, json, os, shutil

def init(rss_type, path):

    if rss_type == "datasets":
        rss_type, titl_col, desc_col, tag_col = "datasets/",  0, 1, [4,6]
        csvfile = 'Master- Marketplace Accelerators - Datasets.csv'
    elif rss_type == "skills":
        rss_type, titl_col, desc_col, tag_col = "skills/",  0, 1, [11]
        csvfile = 'Master- Marketplace Accelerators - Skills.csv'
    elif rss_type == "agents":
        rss_type, titl_col, desc_col, tag_col = "agents/",  0, 1, [2,3]
        csvfile = 'Master- Marketplace Accelerators - Agents.csv'

    taxonomyfile = 'taxonomy.json'

    # creating an empty resource folder
    if os.path.exists(path + rss_type): shutil.rmtree(path + rss_type)
    else: os.makedirs(path + rss_type)

    return csvfile, taxonomyfile, (rss_type, titl_col, desc_col, tag_col), path

def main(csvfile, taxonomyfile, resource, path):

    rss_type, titl_col, desc_col, tag_col = resource

    # creating txs array from taxonomy.json
    txs = json.load(open(taxonomyfile))['taxonomies']
    for pair in range(0, len(txs)):
        txs[pair] = (txs[pair].get('value'), txs[pair].get('key'))


    # Creating data array from the csv sheet
    sheet = []
    # sheet_reader = csv.reader(open(csvfile, 'r'), delimiter=',', quotechar='"')
    sheet_values = sheets_api(rss_type)
    for row in sheet_values:
        sheet_row = ['','','', []]
        for col in range(0, len(row)):
            if col == titl_col:
                sheet_row[0] = cleanup(row[col])
                sheet_row[1] = row[col]
            elif col == desc_col:
                sheet_row[2] = row[col]
            elif col in tag_col:
                sheet_row[3] = list(set(sheet_row[3]+row[col].replace(', ', ',').split(',')))

        if sheet_row != ['','','',[]] and sheet_row != ['','','',['']]:
            sheet.append(sheet_row)
    sheet.pop(0) # removing column headers

    not_found = set()

    # creating the resource.yaml file
    for r in sheet:

        rss_name = r[0] + '/'

        # Adding tags using the taxonomy list
        tags = []
        for l in r[3]:
            if l == '': continue
            l = cleanup(l)
            tag = list(filter(lambda x: x[1].split('.')[0] == rss_type[0:-2] and
                                        x[1].split('.')[-1] == l,
                            txs))

            if tag == []: not_found.add(rss_type[:-1] + '.[PATH].' + l)
            for val in tag:
                tags.append(dict({"label" : val[0], "value" : val[1]}))
        # print(tags)
        # creating a folder for each resource
        if not os.path.exists(path + rss_type + rss_name): os.makedirs(path + rss_type + rss_name)

        # adding the resource.yaml file
        resource_yaml = {
            "name": r[0],
            "title": r[1],
            "description": r[2],
            "type": {
                "name": rss_type[0:-2]
            }, "icon": "http://icon.png",
            "price": {
                "unit": "CCU",
                "value": 45
            }, "tutorials": [
                {
                    "description": "Tutorial Description",
                    "videoLink": "http://video.avi"
                }
            ],
            "tags": tags
        }

        yaml_name = "resource.yaml"
        n = 0
        while True:
            n += 1
            if not os.path.isfile(path + rss_type  + rss_name + yaml_name):
                file = open(path + rss_type + rss_name + yaml_name, 'w')
                json.dump(resource_yaml, file, indent=4)
                break
            else:
                yaml_name = "resource"+str(n)+".yaml"

    return not_found

def cleanup(s):
    if s == '': return s
    s = s.replace("U.S.", "US")
    s = s.replace("U.S", "US")
    s = s.replace("-", " ")
    s = s.replace(".", " ")
    s = s.replace("\n", "")
    s = s.replace("(", " ")
    s = s.replace(")", " ")
    s = s.replace(":", "")
    s = s.replace(" ", "_")
    s = s.replace("__", "_")
    s = s.replace("__", "_")
    s = s.replace(chr(8217) + 's', "")
    s = s.replace(chr(8217), "")
    if s[-1] == '_':
        s = s[0:-1]
    s = s.lower()

    return s


def sheets_api(rss_type):
    # Setup the Sheets API
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    SPREADSHEET_ID = '1K5OsO_yhttXHRtuWT83grwVZaC-6GOm6VzRNk3cegnA'
    RANGE_NAME = rss_type[0:-1] + '!A:Z'
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=RANGE_NAME).execute()
    sheet_values = result.get('values', [])
    return sheet_values

path = '/'.join(os.path.realpath(__file__).split('/')[0:-1]) + '/'
# path = '/Users/sbakhda/dev/c12e-agents-skills/agent-camel/'


not_found = set()

print('Generating agent yamls...')
csvfile, taxonomyfile, resource, path = init("agents", path)
not_found |= main(csvfile, taxonomyfile, resource, path)
print('Done\n')


print('Generating dataset yamls...')
csvfile, taxonomyfile, resource, path = init("datasets", path)
not_found |= main(csvfile, taxonomyfile, resource, path)
print('Done\n')

print('Generating skill yamls...')
csvfile, taxonomyfile, resource, path = init("skills", path)
not_found |= main(csvfile, taxonomyfile, resource, path)
print('Done')

print('\n'+str(len(not_found))+' resource tags were not found in taxonomies:')
for k in not_found:
    print(k)

