# Module for entering nodes from the resource flowchart into taxonomy_shikhar.json
# Merges additions with existing taxonomies.json file
# includes function for sorting the json alphabetically and removing duplicates
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import json

txs = json.load(open('taxonomy.json', 'r')).get('taxonomies')
fname = "taxonomy.json"

# Converting json dict to list(key-value tuples),
# then sorting and converting back to json
def sort_json(fname):
    print('\nSorting jsons in taxonomy.json...')
    txs = json.load(open(fname))['taxonomies']
    k = list({(j.get('key'), j.get('value')) for j in txs})
    k.sort(key=lambda x: x[0])
    file = open(fname, 'w').close()
    file = open(fname, 'a')
    file.write('{\n  "taxonomies": [')
    for i in range(0,len(k)):
        j = {"key": k[i][0], "value": k[i][1]}
        json.dump(j, file, indent=8)
        if i != len(k)-1: file.write(',\n')
    file.write('\n  ]\n}')
    print('Done\n')

def sheets_api(rss_type):
    # Setup the Sheets API
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    store = file.Storage('jsons/credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('jsons/client_secret_tags.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    print('Fetching from Google Sheet...')

    # Call the Sheets API
    # SPREADSHEET_ID = '1K5OsO_yhttXHRtuWT83grwVZaC-6GOm6VzRNk3cegnA' # prod
    SPREADSHEET_ID = '1EsH5FPmODz2oYPQ4weI_Owfa8bDxdQYh3cKEQrNPPUw' # dev
    RANGE_NAME = rss_type[0:-1]+'-dev'+'!A:Z'
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=RANGE_NAME).execute()
    sheet_values = result.get('values', [])
    return sheet_values

def data_entry(fname):
    ins = []
    file = open(fname, 'a')
    while True:
        root = ''

        cat = input("\n\nEnter Category - Agent, Skill, Dataset:    ")
        if cat == 'a':
            root += 'agent'
        elif cat == 's':
            root += 'skill'
        elif cat == 'd':
            root += 'dataset'
        elif cat == 'q':
            break
        else:
            continue

        for i in range(1,50):
            t = input("Enter root "+ str(i)+":  ").replace(' ', '').lower()
            if t == '': break
            root += '.' + t

        print('root: ' + root)

        for i in range(1, 50):
            key = input("Enter key " + str(i) + ":  ").replace(' ', '').lower()
            if key == '': break
            val = input("\nEnter value for " + root + '.' + key +': ')
            if val == '':
                val = ' '.join([x.capitalize() for x in key.split('_')])
            j = {"key": root + '.' + key, "value": val}
            ins.append(j)
            json.dump(j, file, indent=4)
            file.write(',\n')
            print('\n', j)

    print(ins)

def main(entry=None):
    if entry: data_entry(fname)
    sort_json(fname)