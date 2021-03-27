import aiohttp
import asyncio
import os
import re
import shutil
from argparse import ArgumentParser

import sys

if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

dl_cdn_header = 'https://dragalialost.akamaized.net/dl/manifests/'
assetbundle = ['/assetbundle.manifest',
               '/assetbundle.zh_cn.manifest',
               '/assetbundle.zh_tw.manifest',
               '/assetbundle.en_us.manifest']

def build_fileset(ver_str, platform):
    file_set = set()
    url = ''
    for m in assetbundle:
        url = dl_cdn_header + platform + '/' + ver_str + m
        ftuple = url, m
        file_set.add(ftuple)
    return file_set

async def download(session, url, filename, path, http_proxy):
    async with session.get(url, proxy = http_proxy) as resp:
        if resp.status != 200:
            print(filename, ': download failed.')
        else:
            with open(path + filename, 'wb') as f:
                f.write(await resp.read())

async def main(ver_str, platform, path, http_proxy):
    file_set = build_fileset(ver_str, platform)   
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[
            download(session, url, filename, path, http_proxy)
            for url, filename in file_set               
        ])

# trash code
async def download_all_archive(platform, archive_path, manifest_path, http_proxy):
    archive_dic = dict()
    with open('newdata_timeline.csv', 'r') as f:
        for l in f:
            sp = l.split(',')
            if sp[0].strip() != 'date' and sp[1] != '':
                archive_dic[sp[1]] = sp[0]
    for key in archive_dic:
        print(key)
        file_set = build_fileset(key, platform)
        archive_path = archive_path + '/' + archive_dic[key] + '_' + key
        os.makedirs(archive_path, exist_ok=True)
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(*[
                download(session, url, filename, manifest_path, http_proxy)
                for url, filename in file_set               
            ])
        for f in os.listdir(manifest_path):
            if 'manifest' in f:
                shutil.copy(os.path.join(manifest_path, f), archive_path)

if __name__ == '__main__':
    parser = ArgumentParser(description='Download manifest files from dl-cdn.')
    parser.add_argument('-v', type=str, help='version string', default='ctA0ok1hpqbQLNpi')
    parser.add_argument('-p', type=str, help='platform(iOS or Android)', default='Android')
    parser.add_argument('-d', type=str, help='destination folder', default='manifests')
    parser.add_argument('-p', type=str, help='Http Proxy (proxy link/None)', default=None)
    args = parser.parse_args()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.v, args.p, args.d, args.p))
    #loop.run_until_complete(download_all_archive(args.p))
    print("download complete.")

    