# DLScripts
Scripts for dl. Mainly for assets downloading.
# Requirements
`python -m pip install -r requirements.txt`
# Usage
## Assets download
- ```one-click.py```: For personal use, it saves a lot of time.
- ```decrypter.py```: Download the manifests of given resource version, then decrypt and parse. Archive the files (raw manifests, decrypted manifests, parsed manifests). Add record to newdata_timeline.csv. (Need key and iv to work, **DO NOT** ask for that.)  
> - As for the resource version (aka manifest version), you can obtain it from a rooted phone (or an emulator that can toggle root status), go to ```/data/data/com.nintendo.zaga/files/manifests/{THIS RANDOM STRING}```, the folder name is exactly the version. Or use some ways to capture the traffic while downloading the manifests, the url contains the version string.
> - Key and iv can be found via reverse-engineering (and datamining).
> - The py3rijndael is a bit slow while processing the manifests, and it didn't offer none-padding mode, so I used a compiled C# program to handle the work. Source code is provided as ```dec.cs```. You can use python one though, please read the comment in ```dl_lib/manifest_decrypt.py```.
- ```diff_downloader.py```: Diff between two versions and download assets.
> - Note: This script can be run without key/iv or the version string.
## Other tools
- ```master_dump.py```: Dump mono jsons from ```master.a```.
- ```story_parser.py```: Dump and parse story assets into readable content, and rename them according to textlabel.(zh_cn only)
## Trash code
- ```master_json.py```: A tool that automatically generates master json files. (meaningless...)
## Others
- ```newdata_timeline.csv```: A simple csv database records the history resource version and note for each update.
- ```newdata_heatmap.pdf```: A heatmap of date when new data came. It begins with the day when I started archiving the data and I think there are no omissions. (zh_cn only! Because manifests can be update partially, happened once though and only updated the en_us manifest.)