import aiohttp
import asyncio
from argparse import ArgumentParser
import errno
import os
import timeit
import tqdm

#PROXY CONFIG
http_proxy = 'http://127.0.0.1:10809'
pac_http_proxy = 'http://127.0.0.1:10810/pac/?t=115431'

lang_list = ['zh_cn', 'zh_tw', 'en_us', 'jp']
manifest_str = ['assetbundle', '.' , 'manifest']

def merge_path_dir(path):
    new_dir = os.path.dirname(path).replace('/', '.')
    return new_dir + '/' + os.path.basename(path)

def check_target_path(target):
    if not os.path.exists(os.path.dirname(target)):
        try:
            os.makedirs(os.path.dirname(target))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

async def download(session, source, target):
    if os.path.exists(target): # Empty file will not be redownload if timeout
        return
#    print('Download', source, target)
    async with session.get(source, proxy = http_proxy) as resp:
#        print(target, resp.status)
        if resp.status != 200:
            print(source)
        assert resp.status == 200
        check_target_path(target)
        with open(target, 'wb') as f:
            f.write(await resp.read())
#        print(target, ' download complete.')

def read_manifest(manifest, folder_name):
    manifest_dic = dict()
    try:
        with open(manifest, 'r') as m:
            for l in m:
                sp = l.split(',')
                if sp[1].strip() != '':
                    manifest_dic[folder_name + '/' + merge_path_dir(sp[0].strip())] = sp[1].strip()
    except FileNotFoundError:
        print(manifest + " not exists!")
        exit(-1)
    
    #print(manifest_dic)
    return manifest_dic

async def main(mdir, o_mdir, lang, folder_name):
    jp_manifest_dic = dict()
    other_manifest_dic = dict()
    manifest_dic = dict()
    old_jp_manifest_dic = dict()
    old_other_manifest_dic = dict()
    old_manifest_dic = dict()
    download_set = set()

    if lang not in lang_list:
        print("-l should be jp/en_us/zh_cn/zh_tw!") 
        exit(0) 

    jp_manifest_dic = read_manifest(mdir + manifest_str[0] + manifest_str[1] + manifest_str[2], folder_name)
    if lang != lang_list[3]:
        other_manifest_dic = read_manifest(mdir + manifest_str[0] + manifest_str[1] + lang + manifest_str[1] + manifest_str[2], folder_name)
    manifest_dic = {**jp_manifest_dic, **other_manifest_dic}
    #print("manifest_dic: " + str(manifest_dic) + "\n")

    if o_mdir is not None:
        old_jp_manifest_dic = read_manifest(o_mdir + manifest_str[0] + manifest_str[1] + manifest_str[2], folder_name)
        if lang != lang_list[3]:
            old_other_manifest_dic = read_manifest(o_mdir + manifest_str[0] + manifest_str[1] + lang + manifest_str[1] + manifest_str[2], folder_name)
        old_manifest_dic = {**old_jp_manifest_dic, **old_other_manifest_dic}
        #print("old_manifest_dic: " + str(manifest_dic) + "\n")
    
    download_set = manifest_dic.items() - old_manifest_dic.items()
    #print(download_set)

    async with aiohttp.ClientSession() as session:     
        tasks = [
            download(session, source, target)
            for target, source in download_set] 
        for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks), desc='download progress'):
            await f
            
if __name__ == '__main__':
    parser = ArgumentParser(description='Download assets from dl-cdn.')
    parser.add_argument('-f', type=str, help='specific filename-hash directory', default='prs_manifests/')
    parser.add_argument('-o', type=str, help='specific old filename-hash directory', default='prs_manifests/old/')
    parser.add_argument('-l', type=str, help='language(jp/zh_cn/zh_tw/en_us)', default='zh_cn')
    parser.add_argument('-d', type=str, help='download folder name', default='20200722')
    args = parser.parse_args()

    #start = timeit.default_timer()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.f, args.o, args.l, args.d))
    #end = timeit.default_timer()

    #print(end-start)
    
