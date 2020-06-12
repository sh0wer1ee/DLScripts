# DLScripts
Scripts for dl.
# Dependency
- [unitypy](https://github.com/K0lb3/UnityPy)
- [py3rijndael](https://github.com/meyt/py3rijndael) : Borrow the code and use none padding. 
# Usage
- ```manifest_grab.py```: Grab manifest files directly from dl-cdn, using version string.
   ```
   manifest_grab.py -v versionstr (-p Android)
   ```
- ```manifest_decrypt.py```: Decrypt the manifests using the given key and iv. 
   ```
   manifest_decrypt.py (-m py) (-k key_content) (-i iv_content)
   ```
   C# code is provided as ``` dec.cs ```.
   <br>**DO NOT** ask for the key and iv.</br>

   TODO: 
   - Python ver need multithread modification.
   - Using dll.
- ```manifest_dump.py```: Dump and parse the decrypted manifest monobehaviour into filename-url lists.
   ```
   manifest_dump.py (-i input_folder) (-o output_folder)
   ```
- ```asset_download.py```: Download assets from the filename-hash lists.
   ```
   asset_download.py (-f manifest_dir) (-o old_manifest_dir) (-l language) (-d folder_name)
   ```