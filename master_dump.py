'''
    Useless now
'''
import os
import re
import shutil
import json
import unicodedata
import UnityPy

masterFilepath = 'assets/'
jsonPath = 'json/'
outputPath = 'wall/'
os.makedirs(masterFilepath, exist_ok=True)
os.makedirs(jsonPath, exist_ok=True)
os.makedirs(outputPath, exist_ok=True)

element = {
    '0':'无',
    '1':'火',
    '2':'水',
    '3':'风',
    '4':'光',
    '5':'暗'
}

abnormal = {
    '_RegistAbnormalRate01':'Poison',
    '_RegistAbnormalRate02':'Burn',
    '_RegistAbnormalRate03':'Freeze',
    '_RegistAbnormalRate04':'Paralysis',
    '_RegistAbnormalRate05':'Blind',
    '_RegistAbnormalRate06':'Stun',
    '_RegistAbnormalRate07':'Bog',
    '_RegistAbnormalRate08':'Sleep',
    '_RegistAbnormalRate09':'Curse',
    '_RegistAbnormalRate10':'Frostbite'
}

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

def dumpAllJson(filepath, type):
    env = UnityPy.load(filepath)
    for obj in env.objects:
        data = obj.read()
        if str(obj.type) == type:
            tree = data.type_tree
            with open(jsonPath + data.name + '.json', 'w', encoding='utf8') as f:
                json.dump(process_json(tree), f, indent=2, ensure_ascii=False)

def retrieveWallData():
    wallPrefix = '21601'
    wallHPData = {}
    enemyparamJson = json.load(open(jsonPath + 'EnemyParam.json', encoding='utf8'))
    #21601*0**  element(1-5) & level(01-99)
    for eid in enemyparamJson:
        if wallPrefix in eid:
            wallHPData[str(eid)] = enemyparamJson[eid]['_HP']
    with open(outputPath + 'wall.csv', 'w', encoding='utf-8-sig') as f:
        for w in wallHPData:
            f.write(element[w[5]] + w[-2:] + ',' + str(wallHPData[w]) + '\n')
    f.close()

def retrievePossible70mc():
    # sooooooooo UGLY!
    skilldataJson = json.load(open(jsonPath + 'SkillData.json', encoding='utf8'))
    textlabelJson = json.load(open(jsonPath + 'TextLabel.json', encoding='utf8'))
    textlabel = {}
    for tid in textlabelJson:
        textlabel[textlabelJson[tid]['_Id']] = textlabelJson[tid]['_Text']
    for sid in skilldataJson:
        if skilldataJson[sid]['_AdvancedSkillLv1'] != 0:
            try:
                i = textlabel['CHARA_NAME_COMMENT_' + sid[:8]]
                v = 'S' + sid[8]  + ': ' + textlabel['SKILL_NAME_' + sid]
                eawid = len(i) + sum(1 for v in i if unicodedata.east_asian_width(v) in 'FWA')
                pad = ' ' * (30 - eawid)
                print("%s%s%s" % (i, pad, v))
            except KeyError:
                try:
                    i = textlabel['CHARA_NAME_' + sid[:8]]
                    v = 'S' + sid[8]  + ': ' + textlabel['SKILL_NAME_' + sid]
                    eawid = len(i) + sum(1 for v in i if unicodedata.east_asian_width(v) in 'FWA')
                    pad = ' ' * (30 - eawid)
                    print("%s%s%s" % (i, pad, v))
                except KeyError:
                    print('CHARA_NAME_' + sid[:8])
            
def main():
    #dumpAllJson('assets/master', 'MonoBehaviour')
    retrieveWallData()
    retrievePossible70mc()

if __name__ == '__main__':
    main()