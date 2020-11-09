# DLScripts
Scripts for dl. Mainly for assets downloading.
# Requirements
`python -m pip install -r requirements.txt`
# Usage
## Assets download
- ```decrypter.py```: Download the manifests of given resourse version, then decrypt and parse. Archive the files (raw manifests, decrypted manifests, parsed manifests). Add record to newdata_timeline.csv. (Need key and iv to work, **DO NOT** ask for that.)
- ```diff_downloader.py```: Diff between two versions and download assets.
## Other tools
- ```master_dump.py```: Dump mono jsons from ```master.asset```.
- ```story_parser.py```: Dump and parse story assets into readable content, and rename them according to textlabel.(zh_cn only)
## Trash code
- ```master_json.py```: A tool that automatically generates master json files. (meaningless...)