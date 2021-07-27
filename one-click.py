import sys
import os

# --CONFIG--
proxy = 'http://127.0.0.1:10809'
date = '20210727'  # <--
res_ver = 'ehkOH12Z6adBvlhd'  # <--
memo = '14:00 new pack'  # <--
new = f'prs_manifests_archive/{date}_{res_ver}'
old = 'prs_manifests_archive/20210725_67oUWzJD2q6UwKL0'  # <--
DIFF_ONLY = False  # <---- important
# --CONFIG--


def decrypter():
    os.system(
        f'python decrypter.py -d "{date}" -r "{res_ver}" -n "{memo}" -p "{proxy}"')
    os.system('pause')


def diff_downloader():
    os.system(f'python diff_downloader.py -n "{new}" -o "{old}" -p "{proxy}"')
    os.system('pause')


def newdata_heatmap():
    os.system('python newdata_heatmap.py')
    os.system('pause')


def auto_deploy():
    os.system('git add -A')
    os.system(f'git commit -m "{date}-{res_ver}"')
    os.system('git push --force')


if __name__ == '__main__':
    #os.system(f'python diff_downloader.py -n "{old}" -f "emotion/story/" -d "asset" -p "{proxy}"')
    # exit()
    if DIFF_ONLY:
        diff_downloader()
    else:
        decrypter()
        diff_downloader()
        newdata_heatmap()
        auto_deploy()
