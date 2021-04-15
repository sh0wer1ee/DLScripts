import sys
import os

#--CONFIG--
proxy = 'http://127.0.0.1:10809'
date = '20210415'# <--
res_ver = 'tKNhlutrX4LPXPUk'# <--
memo = '14:00 fesex(??????)'# <--
new = f'prs_manifests_archive/{date}_{res_ver}'
old = 'prs_manifests_archive/20210412_725KSe0jjK7dUQZq'# <--
DIFF_ONLY = False # <---- important
#--CONFIG--

def decrypter():
    os.system(f'python decrypter.py -d "{date}" -r "{res_ver}" -n "{memo}" -p "{proxy}"')
    os.system('pause')
def diff_downloader():
    os.system(f'python diff_downloader.py -n "{new}" -o "{old}" -p "{proxy}"')
    os.system('pause')
def newdata_heatmap():
    os.system('python newdata_heatmap.py')
    os.system('pause')

if __name__ == '__main__':
    if DIFF_ONLY:
        diff_downloader()
    else:
        decrypter()
        diff_downloader()
        newdata_heatmap()