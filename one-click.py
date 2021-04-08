import sys
import os

#--CONFIG--
proxy = 'http://127.0.0.1:10809'
date = '20210409'# <--
res_ver = ''# <--
memo = '13:40 dragon legend'# <--
new = f'prs_manifests_archive/{date}_{res_ver}'
old = 'prs_manifests_archive/20210407_vV26vt33rpPRoANd'# <--
#--CONFIG--

os.system(f'python decrypter.py -d "{date}" -r "{res_ver}" -p "{proxy}"')
os.system('pause')
os.system(f'python diff_downloader.py -n "{new}" -o "{old}" -p "{proxy}"')
os.system('pause')
os.system('python newdata_heatmap.py')