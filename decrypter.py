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
from argparse import ArgumentParser
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

def decrypt(method):
    print('decrypting...')
    if method == 'cs':
        manifest_decrypt.decrypt(manifest_decrypt.load_key(), manifest_decrypt.load_iv())
    elif method == 'py':
        manifest_decrypt.decryptPy(manifest_decrypt.load_key(), manifest_decrypt.load_iv(), MANIFESTS, DEC)
    else:
        print('method does not exist.')
        exit(-1)

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

def main(date, resVer, note, method):
    download(date, resVer)
    archiveManifests(date, resVer)
    decrypt(method)
    archiveDecManifests(date, resVer)
    parse()
    archivePrsManifests(date, resVer)
    appendRecord(date, resVer, note)

if __name__ == '__main__':
    #--Default--
    date = '20201223'
    resVer = 'UOWfZfLZ5nbBwIki'
    note = '14:00 time attack + anni-raid * 2'
    method = 'cs'
    #--Default--

    parser = ArgumentParser(description='Deal with manifests.')
    parser.add_argument('-d', type=str, help='Date when new data came out (For record use)', default=date)
    parser.add_argument('-r', type=str, help='Manifest resource version (just manifests folder name)', default=resVer)
    parser.add_argument('-n', type=str, help='Memo for this update (For record use)', default=note)
    parser.add_argument('-m', type=str, help='Method for decryption (py or cs)', default=method)
    args = parser.parse_args()

    main(args.d, args.r, args.n, args.m)