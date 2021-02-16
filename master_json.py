'''
    A trash code that generates the newest json files.
    (These files should be dumped at datamining period.)
'''
import UnityPy
import json
import requests
import os

#proxies = {'http': 'http://127.0.0.1:10809',
#           'https': 'http://127.0.0.1:10809'}

def process_json(tree):
    while isinstance(tree, dict):
        if 'dict' in tree:
            tree = tree['dict']
        elif 'list' in tree:
            tree = tree['list']
        elif 'entriesValue' in tree and 'entriesHashCode' in tree:
            return {k: process_json(v) for k, v in zip(tree['entriesHashCode'], tree['entriesValue'])}
        else:
            return tree
    return tree

def fetchNewestManifestUrl():
    print('fetching newset manifest url...')
    response = requests.get('https://raw.githubusercontent.com/sh0wer1ee/DLScripts/master/newdata_timeline.csv')#, proxies=proxies)
    if(response.status_code == 200):
        newest = response.content.split(b'\n')[-2].decode('utf8').split(',')
        return 'https://raw.githubusercontent.com/sh0wer1ee/DLScripts/master/prs_manifests_archive/%s_%s/assetbundle.zh_cn.manifest' % (newest[0], newest[1])

def fetchNewestMasterUrl():
    print('fetching newest master url...')
    response = requests.get(fetchNewestManifestUrl())#, proxies=proxies)
    if(response.status_code == 200):
        newest = response.content.split(b'\n')[0].decode('utf8').split(',')[1]
        return newest

def dumpJson(path):
    os.makedirs(path, exist_ok=True)
    response = requests.get(fetchNewestMasterUrl())#, proxies=proxies)
    if(response.status_code == 200):
        am = UnityPy.AssetsManager(response.content)
        for asset in am.assets.values():
            for o in asset.objects.values():
                data = o.read()
                if str(data.type) == 'MonoBehaviour':
                    print('dumping %s...' % data.name)
                    tree = data.type_tree
                    with open(f'{path}{data.name}.json', 'w', encoding='utf8') as f:
                        json.dump(process_json(tree), f, indent=2, ensure_ascii=False)
                        f.close()

if __name__ == '__main__':
    dumpJson('json/')