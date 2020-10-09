'''
    This script will
        Download the manifests of given resourse version, then decrypt and parse.
        Archive the files (raw manifests, decrypted manifests, parsed manifests).
        Add record to newdata_timeline.csv.
'''
import aiohttp
import asyncio
import os
import shutil
import pandas as pd
import dl_lib.manifest_grab as manifest_grab
import dl_lib.manifest_decrypt as manifest_decrypt
import dl_lib.manifest_dump as manifest_dump

ROOT = os.path.dirname(os.path.realpath(__file__))
MANIFESTS = os.path.join(ROOT, 'manifests')
ARCHIVES = os.path.join(ROOT, 'manifests_archive')
DEC = os.path.join(ROOT, 'dec_manifests')
DEC_ARCHIVES = os.path.join(ROOT, 'dec_manifests_archive')
PRS = os.path.join(ROOT, 'prs_manifests')
PRS_ARCHIVES = os.path.join(ROOT, 'prs_manifests_archive')
os.makedirs(MANIFESTS, exist_ok=True)
os.makedirs(ARCHIVES, exist_ok=True)
os.makedirs(DEC, exist_ok=True)
os.makedirs(DEC_ARCHIVES, exist_ok=True)
os.makedirs(PRS, exist_ok=True)
os.makedirs(PRS_ARCHIVES, exist_ok=True)

def download(date, resVer):
    print('downloading manifests...')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(manifest_grab.main(resVer, 'Android', MANIFESTS))
    print('manifests download completed.')

def archiveManifests(date, resVer):
    archive_path = '%s/%s_%s' % (ARCHIVES, date, resVer)
    os.makedirs(archive_path, exist_ok=True)
    for f in os.listdir(MANIFESTS):
        if 'manifest' in f:
            shutil.copy(os.path.join(MANIFESTS, f), archive_path)
    print('manifests archived.')

def decrypt():
    print('decrypting...')
    manifest_decrypt.decrypt(manifest_decrypt.load_key(), manifest_decrypt.load_iv())


def archiveDecManifests(date, resVer):
    archive_path = os.path.join(DEC_ARCHIVES, '%s_%s' % (date, resVer))
    os.makedirs(archive_path, exist_ok=True)
    for f in os.listdir(DEC):
        if 'manifest' in f:
            shutil.copy(os.path.join(DEC, f), archive_path)
    print('decrypted manifests archived.')

def parse():
    print('dumping...')
    manifest_dump.main(DEC, PRS)
    print('finished.')

def archivePrsManifests(date, resVer):
    archive_path = os.path.join(PRS_ARCHIVES, '%s_%s' % (date, resVer))
    os.makedirs(archive_path, exist_ok=True)
    for f in os.listdir(PRS):
        if 'manifest' in f:
            shutil.copy(os.path.join(PRS, f), archive_path)
    print('parsed manifests archived.')

def appendRecord(date, resVer, note=None):
    df = pd.read_csv('newdata_timeline.csv')
    if resVer not in df['res_ver(android)'].values:
        newRow = pd.Series([date,resVer,note], index=df.columns)
        newDf = df.append(newRow, ignore_index=True)
        newDf.to_csv('newdata_timeline.csv', index=False)
        print('record is added to the newdata_timeline.csv.')

if __name__ == '__main__':
    #--Config--
    date = '20201009'
    resVer = 'rUAJ84rrQoQKbHPT'
    note = '14:00 master agito & wind platinum'
    #--Config--

    download(date, resVer)
    archiveManifests(date, resVer)
    decrypt()
    archiveDecManifests(date, resVer)
    parse()
    archivePrsManifests(date, resVer)
    appendRecord(date, resVer, note)

