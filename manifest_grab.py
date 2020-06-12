import aiohttp
import asyncio
import os
import re
import requests
from argparse import ArgumentParser

http_proxy = 'http://127.0.0.1:10809'
dl_cdn_header = 'https://dragalialost.akamaized.net/dl/manifests/'
assetbundle = ['/assetbundle.manifest',
               '/assetbundle.zh_cn.manifest',
               '/assetbundle.zh_tw.manifest',
               '/assetbundle.en_us.manifest']
ROOT = os.path.dirname(os.path.realpath(__file__))
MANIFESTS = os.path.join(ROOT, 'manifests')
os.makedirs(MANIFESTS, exist_ok=True)

def build_fileset(ver_str, platform):
    file_set = set()
    url = ''
    for m in assetbundle:
        url = dl_cdn_header + platform + '/' + ver_str + m
        ftuple = url, m
        file_set.add(ftuple)
    return file_set

@asyncio.coroutine
async def download(session, url, filename):
    async with session.get(url) as resp:
        if resp.status != 200:
            print(filename, ': download failed.')
        else:
            with open(MANIFESTS + filename, 'wb') as f:
                f.write(await resp.read())

async def main(ver_str, platform):
    file_set = build_fileset(ver_str, platform)
    open(MANIFESTS + '/' + ver_str, 'a').close()
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[
            download(session, url, filename)
            for url, filename in file_set               
        ])

if __name__ == '__main__':
    parser = ArgumentParser(description='Download manifest files from dl-cdn.')
    parser.add_argument('-v', type=str, help='version string', default='nslrMaf2yLYRW3vV')
    parser.add_argument('-p', type=str, help='platform(iOS or Android)', default='Android')
    args = parser.parse_args()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.v, args.p))
    print("download complete.")

    