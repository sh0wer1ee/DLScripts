import aiohttp
import asyncio
import os
import requests
import UnityPy
import json
import timeit

http_proxy = 'http://127.0.0.1:10809'

ROOT = os.path.dirname(os.path.realpath(__file__))
MASTER = os.path.join(ROOT, 'master')
os.makedirs(MASTER, exist_ok=True)

tlJson = {'ENUS': {},
          'JP': {}, 'ZHCN': {}, 'ZHTW': {}}
outputJson = {}


def loadMastersUrl(resVer):
    assetbundle = {
        'jp': f'https://raw.githubusercontent.com/sh0wer1ee/DLScripts/master/prs_manifests_archive/{resVer}/assetbundle.manifest',
        'zh_cn': f'https://raw.githubusercontent.com/sh0wer1ee/DLScripts/master/prs_manifests_archive/{resVer}/assetbundle.zh_cn.manifest',
        'zh_tw': f'https://raw.githubusercontent.com/sh0wer1ee/DLScripts/master/prs_manifests_archive/{resVer}/assetbundle.zh_tw.manifest',
        'en_us': f'https://raw.githubusercontent.com/sh0wer1ee/DLScripts/master/prs_manifests_archive/{resVer}/assetbundle.en_us.manifest'}
    master = {}
    for lang in assetbundle:
        response = requests.get(assetbundle[lang])
        if(response.status_code == 200):
            master['%s-master' % lang] = response.content.split(b'\n')[0].decode('utf8').split(',')[1].strip()
        else:
            print('error: download failed.')
            exit()
    print('fetch master URLs success.')
    print(master)
    return master


async def download(session, url, filename):
    #async with session.get(url, proxy=http_proxy) as resp:
    async with session.get(url) as resp:
        if resp.status != 200:
            print(filename, ': download failed.')
        else:
            with open(os.path.join(MASTER, filename), 'wb') as f:
                f.write(await resp.read())


async def downloadMasters(master):
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[
            download(session, master[region], region)
            for region in master
        ])


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


def dumpTextlabel(filepath):
    env = UnityPy.load(filepath)
    for obj in env.objects:
        data = obj.read()
        if str(data.type) == 'MonoBehaviour' and str(data.name) == 'TextLabel':
            tree = data.type_tree
            return process_json(tree)
            # with open('%s/%sTextLabel.json' % (output, region), 'w', encoding='utf8') as f:
            #    json.dump(process_json(tree), f, indent=2, ensure_ascii=False)


def parseMasters(date):
    for f in os.listdir(MASTER):
        region = f.split('-')[0].replace('_', '').upper()
        print(f'dumping {region}.json...')
        tlJson[region] = dumpTextlabel(os.path.join(MASTER, f))
    combineJsons()
    with open(f'TextLabel{date}.json', 'w', encoding='utf8') as f:
        json.dump(outputJson, f, indent=2, ensure_ascii=False)
    print('dump complete.')


def combineJsons():
    for key in tlJson:
        for hash in tlJson[key]:
            text = tlJson[key][hash]['_Text']
            # if key == 'ENUS':
            #    text.replace('\\n', ' ')
            # else:
            #    text.replace('\\n', '')
            if (index := tlJson[key][hash]['_Id']) in outputJson:
                outputJson[index][key] = text
            else:
                outputJson[index] = {'ENUS': 'Null',
                                     'JP': 'Null', 'ZHCN': 'Null', 'ZHTW': 'Null'}
                outputJson[index][key] = text


def main(resVer):
    start = timeit.default_timer()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(downloadMasters(loadMastersUrl(resVer)))
    print("master download complete.")

    parseMasters(f'{resVer.split("_")[0]}')

    end = timeit.default_timer()
    print('time spent: ' + str(end-start))

def fetchNewestResourceVersion():
    print('fetching newset manifest url...')
    response = requests.get(
        'https://raw.githubusercontent.com/sh0wer1ee/DLScripts/master/newdata_timeline.csv')
    # , proxies=proxies)
    if(response.status_code == 200):
        newest = response.content.split(b'\n')[-2].decode('utf8').split(',')
        return f'{newest[0]}_{newest[1]}'

if __name__ == '__main__':
    main(fetchNewestResourceVersion())
