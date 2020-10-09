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

import manifest_grab
import manifest_decrypt
import manifest_dump

def download(date, resVer):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(manifest_grab.main(resVer, 'Android'))
    print("manifests download completed.")

def archiveManifests(date, resVer):
    archive_path = '%s/%s_%s' % (manifest_grab.ARCHIVES, date, resVer)
    os.makedirs(archive_path, exist_ok=True)
    for f in os.listdir(manifest_grab.MANIFESTS):
        if 'manifest' in f:
            shutil.copy(os.path.join(manifest_grab.MANIFESTS, f), archive_path)

def decrypt():
    manifest_decrypt.select_method('cs', manifest_decrypt.load_key(), manifest_decrypt.load_iv())

def archiveDecManifests(date, resVer):
    archive_path = '%s/%s_%s' % ('dec_manifests_archive/manifests_archive', date, resVer)
    os.makedirs(archive_path, exist_ok=True)
    for f in os.listdir(manifest_decrypt.DEC):
        if 'manifest' in f:
            shutil.copy(os.path.join(manifest_decrypt.DEC, f), archive_path)

def parse():
    manifest_dump.main(manifest_dump.DEC, manifest_dump.PRS)

def archivePrsManifests(date, resVer):
    archive_path = '%s/%s_%s' % ('prs_manifests_archive', date, resVer)
    os.makedirs(archive_path, exist_ok=True)
    for f in os.listdir(manifest_dump.PRS):
        if 'manifest' in f:
            shutil.copy(os.path.join(manifest_dump.PRS, f), archive_path)

def appendRecord(date, resVer, note=None):
    df = pd.read_csv('newdata_timeline.csv')
    newRow = pd.Series([date,resVer,note], index=df.columns)
    newDf = df.append(newRow, ignore_index=True)
    newDf.to_csv('newdata_timeline.csv', index=False)


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
    #appendRecord(date, resVer, note=None)

