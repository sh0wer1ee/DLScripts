'''
    Diff between two versions and download assets.
'''
import aiohttp
import asyncio
from argparse import ArgumentParser
import errno
import os
import timeit
import tqdm
import shutil

lang_list = ['zh_cn', 'zh_tw', 'en_us', 'jp']
manifest_str = ['assetbundle', 'manifest']

def merge_path_dir(path):
    new_dir = os.path.dirname(path).replace('/', '.')
    return os.path.join(new_dir, os.path.basename(path))

def check_target_path(target):
    if not os.path.exists(os.path.dirname(target)):
        try:
            os.makedirs(os.path.dirname(target))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

async def download(session, source, target, http_proxy):
    if os.path.exists(target): # Empty file will not be redownload if timeout
        return
    async with session.get(source, proxy = http_proxy) as resp:
        if resp.status != 200:
            print(source)
        assert resp.status == 200
        check_target_path(target)
        with open(target, 'wb') as f:
            f.write(await resp.read())
            f.close()

def read_manifest(manifest, folder_name, filter_str):
    manifest_dic = dict()
    try:
        with open(manifest, 'r') as m:
            for l in m:
                sp = l.split(',')
                if not filter_str or filter_str in sp[0]:
                    if sp[1].strip() != '':
                        manifest_dic[f'{folder_name}/{merge_path_dir(sp[0].strip())}'] = sp[1].strip()
            m.close()
    except FileNotFoundError:
        print(f'Cannot find {manifest}. Exiting...')
        exit(-1)
    return manifest_dic

async def main(mdir, o_mdir, lang, localized_only, folder_name, filter_str, http_proxy):
    jp_manifest_dic = dict()
    other_manifest_dic = dict()
    manifest_dic = dict()
    old_jp_manifest_dic = dict()
    old_other_manifest_dic = dict()
    old_manifest_dic = dict()
    download_set = set()
    temp_manifest_str = manifest_str.copy()

    if lang not in lang_list:
        print('-l should be jp/en_us/zh_cn/zh_tw!') 
        exit(0)
    if folder_name is None:
        if 'prs_manifests_archive/' in mdir:
            date = mdir.split('/')[1].split('_')[0]
            folder_name = f'../{date}'
        else:
            folder_name = 'newdata'

    jp_manifest_path = os.path.join(mdir, '.'.join(manifest_str))
    jp_manifest_dic = read_manifest(jp_manifest_path, folder_name, filter_str)
    if lang != lang_list[3]:
        temp_manifest_str.insert(1, lang)
        other_manifest_path = os.path.join(mdir, '.'.join(temp_manifest_str))
        other_manifest_dic = read_manifest(other_manifest_path, folder_name, filter_str)
        manifest_dic = {**jp_manifest_dic, **other_manifest_dic}
    else:
        manifest_dic = jp_manifest_dic

    if o_mdir is not None:
        old_jp_manifest_path = os.path.join(o_mdir, '.'.join(manifest_str))
        old_jp_manifest_dic = read_manifest(old_jp_manifest_path, folder_name, filter_str)
        if lang != lang_list[3]:
            old_other_manifest_path = os.path.join(o_mdir, '.'.join(temp_manifest_str))
            old_other_manifest_dic = read_manifest(old_other_manifest_path, folder_name, filter_str)
            old_manifest_dic = {**old_jp_manifest_dic, **old_other_manifest_dic}
        else:
            old_manifest_dic = old_jp_manifest_dic
    if localized_only:
        download_set = other_manifest_dic.items() - old_other_manifest_dic.items()
    else:
        download_set = manifest_dic.items() - old_manifest_dic.items()

    async with aiohttp.ClientSession() as session:     
        tasks = [
            download(session, source, target, http_proxy)
            for target, source in download_set] 
        for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks), desc='Download progress'):
            await f

if __name__ == '__main__':
    #--Default--
    new_manifest_folder = 'prs_manifests_archive/YYYYMMDD_****************' # example
    old_manifest_folder = None
    lang = 'zh_cn'
    localized_only = False
    folder_name = None
    filter_str = None
    http_proxy = None
    #--Default--
    
    parser = ArgumentParser(description='Diff between versions and download the assets.')
    parser.add_argument('-n', type=str, help='Manifest folder (Newer version)', default=new_manifest_folder)
    parser.add_argument('-o', type=str, help='Manifest folder (Older version)', default=old_manifest_folder)
    parser.add_argument('-l', type=str, help='Language version (jp/zh_cn/zh_tw/en_us)', default=lang)
    parser.add_argument('-c', type=str, help='Localized only? (True/False)', default=localized_only)
    parser.add_argument('-d', type=str, help='Download location', default=folder_name)
    parser.add_argument('-f', type=str, help='Filter string (Case sensitive)', default=filter_str)
    parser.add_argument('-p', type=str, help='Http Proxy (proxy link/None)', default=http_proxy)
    args = parser.parse_args()

    start = timeit.default_timer()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.n, args.o, args.l, args.c, args.d, args.f, args.p))
    end = timeit.default_timer()

    print('Time spent: ' + str(end-start) + ' second.')
    
