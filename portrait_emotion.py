'''
    Dump the portrait base and parts from portrait assets.
    You need to download them with manifest_diff_download.py.

    TODO:
        Use pil to merge the parts to base.
'''

import os
import tqdm
import json
import UnityPy
from PIL import Image

ROOT = os.path.dirname(os.path.realpath(__file__))
#--CONFIG--#
INPUT = os.path.join(ROOT, 'portrait_asset')
OUTPUT = os.path.join(ROOT, 'portrait_output')
#--CONFIG--#
os.makedirs(INPUT, exist_ok=True)
os.makedirs(OUTPUT, exist_ok=True)

def processAsset(filePath):
    indexTable = {}
    imageData = {}

    baseName = os.path.basename(filePath)
    am = UnityPy.AssetsManager(filePath)
    for asset in am.assets.values():
        for o in asset.objects.values():
            data = o.read()
            if str(data.type) == 'MonoBehaviour':
                tree = data.read_type_tree()
                indexTable = parseMono(tree)
            if str(data.type) == 'Texture2D':
                imageData[data.name] = data.image
    imageData = loadNhaam(imageData)
    os.makedirs(os.path.join(OUTPUT, baseName), exist_ok=True)
    
    combineYCbCrA(imageData, baseName)
    for index in indexTable:
        combineYCbCrA(imageData, baseName, index, indexTable[index]) 
    
def parseMono(mono):
    partsTextureIndexTable = {}
    for index in mono['partsTextureIndexTable']:
        partsTextureIndexTable[index['colorIndex']] = index['alphaIndex']
    return partsTextureIndexTable

def combineYCbCrA(imageData, baseName, cidx = -1, aidx = -1):
    imageBase = ''
    if cidx == -1:
        imageBase = ('%s_base') % baseName
    else:
        imageBase = ('%s_parts_c%s') % (baseName, str(cidx).zfill(3))
    
    try:
        alpha = imageData['%s_alpha' % imageBase].convert('L') if aidx == -1 else imageData[('%s_parts_a%s_alpha') % (baseName, str(aidx).zfill(3))].convert('L')
    except KeyError:
        pass # ¯\_(ツ)_/¯

    Y = imageData['%s_Y' % imageBase].convert('RGBA').split()[-1]
    mergedImg = Image.merge('YCbCr',
    (
        Y,
        imageData['%s_Cb' % imageBase].convert('L').resize(Y.size, Image.ANTIALIAS),
        imageData['%s_Cr' % imageBase].convert('L').resize(Y.size, Image.ANTIALIAS)
    )).convert('RGBA')
    if aidx >= -1:
        mergedImg.putalpha(alpha) 
    mergedImg.save(('%s\\%s\\%s.png') % (OUTPUT, baseName, imageBase))

def loadNhaam(imageData):
    # missing Nhaam's base Y file
    am = UnityPy.AssetsManager(INPUT + '\\assets._gluonresources.images.emotion.story.chara.100007_01.parts\\100007_01_base_y')
    for asset in am.assets.values():
        for o in asset.objects.values():
            data = o.read()
            if str(data.type) == 'Texture2D':
                imageData[data.name] = data.image
    return imageData
            
def main():
    for root, dirs, files in os.walk(INPUT, topdown=False):
        if files:
            if files == ['100007_01_base_y']:
                continue
            pbar = tqdm.tqdm(files)
            for f in pbar:
                pbar.set_description('processing %s...' % f)
                src = os.path.realpath(os.path.join(root, f))
                processAsset(src)

if __name__ == '__main__':
    main()



