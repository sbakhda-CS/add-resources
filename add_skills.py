from glob import glob
import json, yaml

path = '/Users/sbakhda/dev/c12e-agents-skills/skill-camel/skills/*'

for g in glob(path):
    yaml_json = yaml.load(open(g+'/skill.yaml', 'r'))
    if yaml_json is not None:
        # print(yaml_json.get('tags'))

        name = yaml_json.get('name').replace('cortex/','') or ''
        title = yaml_json.get('title') or ''
        desc = yaml_json.get('description') or ''
        tags = yaml_json.get('tags') or []


        # print('name', name)
        # print('title', title)
        # print('desc', desc)
        # print('tags', tags)
        s = []
        for t in tags:
            s.append(t.get("label"))

        # print(title+'\t'+desc+'\t'+('\t'*9)+str(tags))
        print(title+'\t'+desc+'\t'+('\t'*9)+', '.join(s))

