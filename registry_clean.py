import requests
import json
import re
import datetime


def get_image_date(repo, tag, registry):
    info = requests.get(registry + 'v2/'+repo+'/manifests/'+tag)
    created_date = []
    try:
        for i in info.json()['history']:
            created =  json.loads(i['v1Compatibility'])['created']
            created_date.append(created)
    except KeyError:
        print("error repo = " +  repo + " tag = " + tag )
        print(info.json());
    created_date.sort()
    dt = re.search('\d\d\d\d-\d\d-\d\d', created_date[-1])
    date = datetime.datetime.strptime(dt.group(0), "%Y-%m-%d")
    return(date)

def mark_as_delete(repo, tag, registry):
    headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
    info = requests.get(registry + 'v2/'+repo+'/manifests/'+tag, headers=headers)
    res = requests.delete(registry + "v2/" + repo + "/manifests/" + info.headers['Docker-Content-Digest'])
    print(registry + "v2/" + repo + "/manifests/" + info.headers['Docker-Content-Digest'])
    print(res)
    print("done")

registry = "https://localhost:5000"
current_date = datetime.datetime.now()
delta = datetime.timedelta(days=21)
threshold_date = current_date - delta;
r = requests.get(registry + 'v2/_catalog')
for repo in r.json()['repositories']:
    tags = requests.get(registry + 'v2/'+repo+'/tags/list')
    try:
        for tag in (tags.json()["tags"]):
                img_date = get_image_date(repo, tag)
                if  (img_date < threshold_date) and (not  re.match(r".*latest", tag)):
                    print(repo+": "+tag)
                    print img_date
                    print threshold_date
                    print("--------------------------------------")
                    mark_as_delete(repo, tag)

    except TypeError:
        print('No tags')
