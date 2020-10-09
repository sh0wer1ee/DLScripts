import os
import re
from argparse import ArgumentParser
from UnityPy import AssetsManager

dl_cdn_header = 'http://dragalialost.akamaized.net/dl/assetbundles/'
pattern = r'string name = \"(.*)\"(?:\r)*(?:\n)*(?:\t)*string hash = \"(.*)\"'

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
    
def main(input_folder, output_folder):
    for root, dirs, files in os.walk(input_folder, topdown=False):
        for f in files:
            print('processing ' + f + '...')
            src = os.path.realpath(os.path.join(root, f))
            filepath = os.path.join(output_folder, f)
            if "manifest" in src:
                extract_assets(src, filepath)


def extract_assets(src, filepath):
    am = AssetsManager(src)
    for asset in am.assets.values():
        buildtarget = asset.target_platform
        for obj in asset.container.values():
            export_obj(obj, filepath, buildtarget)


def export_obj(obj, filepath, buildtarget):
    sp = str(buildtarget).split('.')
    data = obj.read()
    if data.name == 'manifest':
        if obj.type == "MonoBehaviour":
            parsed_list = parse(data.dump())
            with open(filepath, 'w') as f:
                for p in parsed_list:
                    path = p[0] if p[0] != 'shader' else '_shader' # deal with the name conflict
                    f.write('%s,%s%s/%s/%s\n' % (path , dl_cdn_header, sp[1], p[1][0:2], p[1]))

def parse(manifest):
    mlist = re.findall(pattern, manifest, re.MULTILINE)
    return mlist

def dump_all(dec_archive_folder, prs_archive_folder):
    os.makedirs(dec_archive_folder, exist_ok=True)
    os.makedirs(prs_archive_folder, exist_ok=True)
    for f in os.listdir(dec_archive_folder):
        if os.path.isdir(os.path.join(dec_archive_folder, f)):
            os.makedirs(prs_archive_folder +'/'+ f, exist_ok=True)
            main(os.path.join(dec_archive_folder, f), prs_archive_folder +'/'+ f)


if __name__ == '__main__':
    parser = ArgumentParser(description='Dump and parse the decrypted manifests.')
    parser.add_argument('-i', type=str, help='input folder', default='dec_manifests')
    parser.add_argument('-o', type=str, help='output folder', default='prs_manifests')
    args = parser.parse_args()

    #dump_all('dec_manifests_archive/manifests_archive', 'prs_manifests_archive')
    main(args.i, args.o)
