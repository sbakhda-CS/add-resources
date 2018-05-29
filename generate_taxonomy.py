# Module for entering nodes from the resource flowchart into taxonomy_shikhar.json
# Merges additions with existing taxonomies.json file
# includes function for sorting the json alphabetically

import json

txs = json.load(open('taxonomy.json', 'r')).get('taxonomies')
fname = "taxonomy.json"

# Converting json dict to list(key-value tuples),
# then sorting and converting back to json
def sort_json(txs, fname):
    k = [(j.get('key'), j.get('value')) for j in txs]
    k.sort(key=lambda x: x[0])
    file = open(fname, 'w')
    file.close()
    file = open(fname, 'a')
    file.write('{\n  "taxonomies": [')
    for i in range(0,len(k)):
        j = {"key": k[i][0], "value": k[i][1]}
        json.dump(j, file, indent=8)
        if i != len(k)-1: file.write(',\n')
    file.write('\n  ]\n}')


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


data_entry(fname)
sort_json(txs, fname)