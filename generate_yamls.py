from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import csv, json, os, shutil, random, yaml, subprocess, glob, io


def init(rss_type, path):

    if rss_type == "dataset":
        rss_type, titl_col, desc_col, tag_col = "dataset",  0, 1, [4,6]
    elif rss_type == "skill":
        rss_type, titl_col, desc_col, tag_col = "skill",  0, 1, [2]
    elif rss_type == "agent":
        rss_type, titl_col, desc_col, tag_col = "agent",  0, 1, [2,3]
    else:
        rss_type, titl_col, desc_col, tag_col = None, 0, 1, 2

    # creating an empty resource folder if it doesn't exist
    if not os.path.exists(path + rss_type + '-camel/' + rss_type + 's/'):
        os.makedirs(path + rss_type + '-camel/' + rss_type + 's/')

    return (rss_type, titl_col, desc_col, tag_col), path


def set_em_up(taxonomyfile, resource, path, CHANGE_SKILL_YAML, CHANGE_RSS_YAML):

    rss_type, titl_col, desc_col, tag_col = resource

    # creating txs array from taxonomy.json
    txs = json.load(open(taxonomyfile))['taxonomies']
    for pair in range(0, len(txs)):
        txs[pair] = (txs[pair].get('value'), txs[pair].get('key'))

    # Sheet Structure
    # r[0] = name
    # r[1] = human title
    # r[2] = description
    # r[3] = tag label array

    # Creating data array from the google sheet
    sheet = []
    sheet_raw = sheets_api(rss_type)
    if sheet_raw == []: return set()
    for row in sheet_raw:
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
    many_found = set()

    # creating the resource.yaml file
    for rss in sheet:

        rss_name = rss[0]
        rss_title = rss[1]
        rss_desc = rss[2]
        rss_tags = rss[3]

        # creating a folder for each resource
        if not os.path.exists(path + rss_type+'-camel/' + rss_type+'s/' + rss_name+'/'):
            os.makedirs(path + rss_type+'-camel/' + rss_type+'s/' + rss_name+'/')

        # add tags from skill.yaml
        if os.path.exists(path + rss_type+'-camel/' + rss_type+'s/' + rss_name+'/' +  'skill.yaml'):
            yaml_json = yaml.load(open(path + rss_type+'-camel/' + rss_type+'s/' + rss_name+'/' +  'skill.yaml', 'r'))
            if yaml_json is not None:
                t = yaml_json.get('tags') or None
                if t is not None and not(t in rss_tags):
                    rss_tags += t

        # adding cognitivescale tag
        rss_tags.append(dict({"label" : "CognitiveScale", "value" : rss_type + ".service_providers.cognitive_scale"}))

        # get tag key-value from taxonomy.json
        tags = []
        for label in rss_tags:

            if isinstance(label, str):
                if label == '': continue
                og_label = label
                label = cleanup(label)
                query_results = list(filter(lambda x: x[1].split('.')[0] == rss_type and
                                            x[1].split('.')[-1] == label,
                                txs))
                if query_results == []:
                    not_found.add(rss_type + '.[PATH].' + label + ' - ' + og_label + ' in ' + rss_name)
                elif len(query_results) > 1:
                    many_found.add((rss_type + '.[PATH].' + label, tuple(query_results)))
                else:
                    tags.append(dict({"label" : query_results[0][0], "value" : query_results[0][1]}))
            if isinstance(label, dict):
                query_results = list(filter(lambda x: x[0] == label.get('label') and
                                                      cleanup(x[1]) == cleanup(label.get('value')),
                                            txs))
                if query_results == []:
                    not_found.add(label.get('value')+' - '+label.get('label') + ' in ' + rss_name)
                elif len(query_results) > 1:
                    many_found.add((label.get('value'), tuple(query_results)))
                tags.append(dict({"label": label.get('label'), 'value': label.get('value')}))

        # remove duplicates
        tags_set = []
        for t in tags:
            if t not in tags_set:
                tags_set.append(t)
        tags_set.sort(key=lambda x : x["value"])
        rss_tags = tags_set

        # adding the resource.yaml file
        resource_yaml = {
            "name": ('cortex/' + rss_name),
            "title": rss_title,
            "description": rss_desc,
            "type": {
                "name": rss_type
            }, "icon": "http://icon.png",
            "price": {
                "unit": "CCU",
                "value": random.randint(50,100)
            }, "tutorials": [
                {
                    "description": "Tutorial Description",
                    "videoLink": "http://video.avi"
                }
            ],
            "tags": rss_tags
        }

        # overwrite resource.yaml
        if CHANGE_RSS_YAML == "resource":
            file = open(path + rss_type+'-camel/' + rss_type+'s/' + rss_name+'/' + "resource.yaml", 'w')
            json.dump(resource_yaml, file, indent=4)

        # adding merged tags to skills.yaml
        if CHANGE_SKILL_YAML == 'skill':
            if os.path.exists(path + rss_type+'-camel/' + rss_type+'s/' + rss_name+'/' +  'skill.yaml'):
                skyaml = open(path + rss_type+'-camel/' + rss_type+'s/' + rss_name+'/' +  'skill.yaml', 'r').read()
                try:
                    tag_index = skyaml.index('tags:')
                except ValueError:
                    print('no tags ' + rss_name)
                    continue
                yaml_json = yaml.load(skyaml[tag_index-1:])
                yaml_json['tags'] = rss_tags
                yamldump = io.StringIO("")
                yaml.dump(yaml_json, yamldump, default_flow_style=False)
                skyaml = skyaml[:tag_index] + yamldump.getvalue()
                final_write = open(path + rss_type+'-camel/' + rss_type+'s/' + rss_name+'/' +  'skill.yaml', 'w')
                final_write.write(skyaml)
                yamldump.close()
            else:
                # print('not found ' + rss_name)
                pass

    return not_found, many_found

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
    s = s.replace("*","")
    s = s.replace(" ", "_")
    s = s.replace("__", "_")
    s = s.replace("__", "_")
    s = s.replace("/", "_")
    s = s.replace(chr(8217) + 's', "")
    s = s.replace(chr(8217), "")
    if s[-1] == '_':
        s = s[0:-1]
    s = s.lower()

    return s

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
        j = {"key": k[i][0].lower(), "value": k[i][1]}
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
    RANGE_NAME = rss_type +'s-dev' + '!A:Z'
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=RANGE_NAME).execute()
    sheet_values = result.get('values', [])
    return sheet_values



def knock_em_down():
    path = '/Users/sbakhda/dev/c12e-agents-skills/'



    taxonomyfile = path + 'taxonomy.json'

    CHANGE_RSS_YAML = input("Do you want to modify RESOURCE.yamls? Confirm with resource:\t")

    # sorting taxonomy.json
    sort_json(taxonomyfile)

    if CHANGE_RSS_YAML == 'resource':
        try:
            subprocess.Popen("find "+path+" -name 'resource*.yaml' -delete")
        except: pass

    rss_type = 'skill'

    if rss_type == 'skill':
        CHANGE_SKILL_YAML = input("Do you want to modify SKILL.yamls? Confirm with skill:\t")
    else:
        CHANGE_SKILL_YAML = None


    print('Generating ' + rss_type + ' resource.yamls...')
    resource, path = init(rss_type, path)
    not_found, many_found = set_em_up(taxonomyfile, resource, path, CHANGE_SKILL_YAML, CHANGE_RSS_YAML)
    print('Done\n')


    print('\n'+str(len(not_found))+' '+rss_type+' resource tags were not found in taxonomies:\n')
    for k in sorted(list(not_found)):
        print(k)

    print('\n'+str(len(many_found))+' '+rss_type+'  resource tags had multiple tags in taxonomies:\n')
    for k in sorted(list(many_found)):
        print(k[0])
        for q in k[1]:
            print('\t'+str(q))

knock_em_down()