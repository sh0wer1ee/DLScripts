# DLScripts
Scripts for dl.
# Dependency
- [unitypy](https://github.com/K0lb3/UnityPy)
- [py3rijndael](https://github.com/meyt/py3rijndael) : Borrow the code and use none padding. 
# Usage
## Assets download
- ```decrypter.py```: Download the manifests of given resourse version, then decrypt and parse. Archive the files (raw manifests, decrypted manifests, parsed manifests). Add record to newdata_timeline.csv. (Need key and iv to work, **DO NOT** ask for that.)
- ```diff_downloader.py```: Diff between two versions and download assets.
## Other tools
- ```master_dump.py```: Dump mono jsons from ```master.asset```.
- ```story_parser.py```: Dump and parse story assets into readable content, and rename them according to textlabel.