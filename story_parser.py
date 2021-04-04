'''
    Parse the story assets directly which are downloaded by manifest_diff_download.py.
    Run master_dump.py before using this script to build necessary json files.
    Not compatible with JP version.
'''

import os
import re
import shutil
import json
import tqdm
import errno
import UnityPy

# story.awakeningstory/rarity*_1*****_**
# story.castlestory/100****
# story.ingame000* 
# story.queststory.event/2******
# story.queststory.main/100****
# story.tutorial/t******
# story.unitstory.chara/1********
# story.unitstory.dragon/2********

ROOT = os.path.dirname(os.path.realpath(__file__))
#--CONFIG--#
playerName = '尤蒂尔'
masterJSONPath = 'json/'
INPUT = os.path.join(ROOT, 'story_asset')
OUTPUT = os.path.join(ROOT, 'prs_story')
#--CONFIG--#
os.makedirs(INPUT, exist_ok=True)
os.makedirs(OUTPUT, exist_ok=True)

textlabel = {}
textlabelJson = json.load(open(masterJSONPath + 'TextLabel.json', encoding='utf8'))
charadataJson = json.load(open(masterJSONPath + 'CharaData.json', encoding='utf8'))
dragondataJson = json.load(open(masterJSONPath + 'DragonData.json', encoding='utf8'))      



def parseStory(filePath):
    env = UnityPy.load(filePath)
    for obj in env.objects:
        if obj.type in ['MonoBehaviour']:
            data = obj.read()
            tree = data.type_tree
            outPath = OUTPUT +  generateName(filePath)
            os.makedirs(os.path.dirname(outPath), exist_ok=True)
            with open(outPath, 'w', encoding='utf-8-sig') as o:
                o.write(parseMono(tree))
                o.close()
                

def parseMono(tree):
    res = ''
    olTitle = ''
    
    for func in tree['functions']:
        for command in func['commandList']:
            commandType = command['command']
            commandData = command['args']
            if commandType == 'OL_TITLE':
                olTitle = commandData[0]
                res = res + olTitle + ':\n'
            elif commandType == 'outline':
                if olTitle != '':
                    res = res + '\t' + commandData[0].replace('\\n', '\n\t').replace('{player_name}', playerName) + '\n'
            elif commandType == 'telop':
                res = res + '\n'
                for arg in commandData:
                    if arg.strip() != '':
                        res = res + '\t' + arg + '\n'
                res = res + '\n'
            elif commandType == 'add_book_text':
                res = res + '\t' + commandData[0].replace('\\n', '\n\t').replace('{player_name}', playerName) + '\n\n'
            elif commandType == 'print':
                res = res + commandData[0].replace('{player_name}', playerName) + ':\n'
                res = res + '\t' + commandData[1].replace('\\n', '\n\t').replace('{player_name}', playerName) + '\n'
            # else:
            #     continue

    return res

def generateName(filepath):
    res = ''
    fileName = os.path.basename(filepath)

    if 'story.awakeningstory' in filepath:
        charaName = ''
        sp = fileName.split('_')
        rarity = sp[0][-1]
        for cd in charadataJson:
            if charadataJson[cd]['_BaseId'] == int(sp[1]) and charadataJson[cd]['_VariationId'] == int(sp[2]):
                charaName = textlabel[charadataJson[cd]['_Name']] if charadataJson[cd]['_VariationId'] == 1 else textlabel[charadataJson[cd]['_SecondName']]
        res = ('\\人物觉醒\\%s %s 觉醒至%s星.txt') % (fileName, charaName, rarity)
    elif 'story.castlestory' in filepath:
        try:
            castleStoryName = textlabel[('STORY_CASTLE_NAME_%s') % fileName]
        except KeyError:
            castleStoryName = fileName
        res = ('\\城堡故事\\%s %s.txt') % (fileName, castleStoryName)
    elif 'story.queststory.event' in filepath:
        eventID = fileName[:5]
        eventName = ''
        storyName = ''
        episode = ''
        try:
            eventName = textlabel[('EVENT_NAME_%s') % eventID]
        except KeyError:
            eventName = eventID
        try:
            storyName = textlabel[('STORY_QUEST_NAME_%s') % fileName]
        except KeyError:
            storyName = fileName
        try:
            episode = textlabel[('STORY_QUEST_TITLE_%s') % fileName]
        except KeyError:
            episode = fileName[5:]
        res = ('\\活动剧情\\%s %s %s %s.txt') % (fileName, eventName, episode, storyName)
    elif 'story.queststory.main' in filepath:
        title = ''
        storyName = ''
        try:
            title = textlabel[('STORY_QUEST_TITLE_%s') % fileName]
        except KeyError:
            title = fileName
        try:
            storyName = textlabel[('STORY_QUEST_NAME_%s') % fileName]
        except KeyError:
            storyName = fileName 
        res = ('\\主线剧情\\%s %s %s.txt') % (fileName, title, storyName)
    elif 'story.tutorial' in filepath:
        res = ('\\教程\\%s.txt') % fileName
    elif 'story.unitstory.chara' in filepath:
        charaName = ''
        storyName = ''
        charaBaseID = fileName[:6]
        charaVariationId = fileName[6:8]
        episode = fileName[-1]
        for cd in charadataJson:
            if charadataJson[cd]['_BaseId'] == int(charaBaseID) and charadataJson[cd]['_VariationId'] == int(charaVariationId) and str(charadataJson[cd]['_Id'])[0] != '9':
                # some id begin with 9 match the condition but is not correct.
                try:
                    if charadataJson[cd]['_VariationId'] == 1:
                        charaName = textlabel[charadataJson[cd]['_Name']]
                    else: # Zena(Another Zethia) is special here, she uses Zethia's baseID but VariationId is not 1
                          # And she is technically an alter of Zethia but not with second name.
                        charaName = textlabel[charadataJson[cd]['_SecondName']]     
                except KeyError:
                    charaName = textlabel[charadataJson[cd]['_Name']]       
        try:
            storyName = textlabel[('STORY_UNIT_NAME_%s') % fileName]
        except KeyError:
            storyName = fileName
        res = ('\\角色剧情\\%s %s 第%s话 %s.txt') % (fileName, charaName, episode, storyName)
    elif 'story.unitstory.dragon' in filepath:
        dragonName = ''
        storyName = ''
        dragonBaseID = fileName[:6] # the unique one
        # dragonVariationId = fileName[6:8] # sadly the dragon alt wont get a different VariationId
        for dd in dragondataJson:
            if dragondataJson[dd]['_BaseId'] == int(dragonBaseID):
                try:
                    dragonName = textlabel[dragondataJson[dd]['_SecondName']]
                except KeyError:
                    dragonName = textlabel[dragondataJson[dd]['_Name']]
        try:
            storyName = textlabel[('STORY_UNIT_NAME_%s') % fileName]
        except KeyError:
            storyName = fileName  
        res = ('\\龙之剧情\\%s %s %s.txt') % (fileName, dragonName, storyName)
    elif 'ingame' in filepath:
        res = ('\\游戏内\\%s.txt') % fileName
    return res

def main():
    for tid in textlabelJson:
        textlabel[textlabelJson[tid]['_Id']] = textlabelJson[tid]['_Text']
    for root, dirs, files in os.walk(INPUT, topdown=False):
        if files:
            pbar = tqdm.tqdm(files)
            for f in pbar:
                pbar.set_description('processing %s...' % f)
                src = os.path.realpath(os.path.join(root, f))
                parseStory(src)

if __name__ == '__main__':
    main()