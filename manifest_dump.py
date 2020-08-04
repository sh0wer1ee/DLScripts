import os
import re
from argparse import ArgumentParser
from UnityPy import AssetsManager

dl_cdn_header = 'http://dragalialost.akamaized.net/dl/assetbundles/'
ROOT = os.path.dirname(os.path.realpath(__file__))
DEC = os.path.join(ROOT, 'dec_manifests')
PRS = os.path.join(ROOT, 'prs_manifests')
os.makedirs(DEC, exist_ok=True)
os.makedirs(PRS, exist_ok=True)

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
                    f.write(p[0] + ',' + dl_cdn_header + sp[1] + '/' +p[1][0:2] + '/' +  p[1] + '\n')

def parse(manifest):
    mlist = re.findall(pattern, manifest, re.MULTILINE)
    return mlist

if __name__ == '__main__':
    parser = ArgumentParser(description='Dump and parse the decrypted manifests.')
    parser.add_argument('-i', type=str, help='input folder', default=DEC)
    parser.add_argument('-o', type=str, help='output folder', default=PRS)
    args = parser.parse_args()

    main(args.i, args.o)
