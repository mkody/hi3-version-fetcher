import re
import time
import json
import pytz
import semver
import requests
import collections

from datetime import datetime

print(str(datetime.now()) + '\n')

md = ''
with open('/var/www/n.kdy.ch/data/hi3.md', 'r') as content_file:
    md = content_file.read()

with open('hi3s.json') as json_file:
    servs = json.load(json_file)

table = '<!-- VER -->\n\n'
table += '| Serveur           | Version    | Date       |\n'
table += '|------------------:|:----------:|------------|\n'

od = collections.OrderedDict(sorted(servs.items(), key=lambda t: t[1]['order']))

for key, value in od.items():
    s = 0
    cont = True
    stay = False
    ts = int(time.time())

    print('Checking ' + key)

    # Get dispatch URL
    params = '?version={}_{}_android&t={}'.format(value['version'], key, ts)
    r = requests.get('http://{}/query_dispatch{}'.format(value['host'], params))
    j = r.json()
    dispatch = j['region_list'][0]['dispatch_url']

    # Save our current version
    v = value['version']

    # Test for multiple options
    while cont:
        # upgrade version
        if s == 0:
            value['version'] = semver.bump_patch(v)
            # print('Testing ' + key + ' on ' + value['version'])
            s = 1
        elif s == 1:
            value['version'] = semver.bump_minor(v)
            # print('Testing ' + key + ' on ' + value['version'])
            s = 2
        elif s == 2:
            value['version'] = semver.bump_major(v)
            # print('Testing ' + key + ' on ' + value['version'])
            s = 3
        else:
            value['version'] = v
            # print(key + ' still on ' + value['version'])
            cont = False
            stay = True

        params = '?version={}_{}_android&t={}'.format(value['version'], key, ts)

        r = requests.get(dispatch + params)
        js = r.json()

        if 'retcode' not in js or not (js['retcode'] == 4 or js['retcode'] == 1):
            if key != 'gf':  # We can't check CN yet
                value['build'] = js['ext']['ex_res_filename'][5:8]
            elif not stay:  # So if CN changes, put ???
                value['build'] = '???'

            if not stay:  # In case of an update, change to the current date
                value['date'] = datetime.now().strftime('%Y-%m-%d')

            print('{} - {}({})\n'.format(key, value['version'], value['build']))

    # Make our table row
    table += '| [{}][{}] | {}({}) | {} |\n'.format(
                    value['name'], key,
                    value['version'], value['build'],
                    value['date']
                )

    # Save our values back to the list
    servs[key] = value

print('Fetch done')

tz = pytz.timezone('Europe/Paris')
dt = datetime.now(tz)
table += '\n\n<small><i>Dernière vérification automatique ' + dt.strftime('le %d/%m/%Y à %H:%M %Z') + '.</i></small>'
table += '\n<!-- /VER -->'

# Replace in the doc
regex = r"<!-- VER -->[\s\S]+<!-- /VER -->"
result = re.sub(regex, table, md, 1, re.MULTILINE)

# print('\n' + table)

# Save to our doc
with open('/var/www/n.kdy.ch/data/hi3.md', "w") as f:
    f.write(result)

# Save our status for future run
with open('hi3s.json', 'w') as f:
    json.dump(servs, f)

print('Saved')
