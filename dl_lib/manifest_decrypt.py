# decrypt /manifests_archive/*/*.manifest to /dec_manifests/

# The python implementation is verrrrry slow, so I use a compiled C# program to complete the work.

import os
import base64
import py3rijndael
from hashlib import sha256
from argparse import ArgumentParser

def load_key():
    key = ''
    if not os.path.isfile("key.txt"):
        print("key.txt is needed")
        exit(-1)
    with open("key.txt", "rb") as key_file:
        key = key_file.read()
    return key

def load_iv():
    iv = ''
    if not os.path.isfile("iv.txt"):
        print("iv.txt is needed")
        exit(-1)
    with open("iv.txt", "rb") as iv_file:
        iv = iv_file.read()
    return iv

# Not really needed to check these things because C# program will do all the works.
def check_keyiv(key, iv):
    if sha256(iv).hexdigest() != "4be4928a99aadafe05ed8a5fc16e1916917af64e344a366a33e2d29d5e2909ef":
        print("Invalid iv!")
        exit(-1)
    if sha256(key).hexdigest() != "94799fb84532096a9bf33e5450b929a983efcf5a822e0637977f809406bb8688":
        print("Invalid key!")
        exit(-1)

# Input and output folders are hard coded in the C# code.
def decrypt(key, iv):
    os.system('dec.exe ' + bytes.decode(key) + ' ' + bytes.decode(iv))

# The pure-python decrypt method
# This is very slow (around 30 seconds) and buggy (see the comments below).
def decryptPy(key, iv, input_folder, output_folder):
    print('Warning: this procedure is very slow and buggy.')
    print('\tPlease read the comments in dl_lib/manifest_decrypt.py if error.')
    rijndael_cbc = py3rijndael.rijndael.RijndaelCbc(
        key=base64.b64decode(key),
        iv=base64.b64decode(iv),
        padding=py3rijndael.ZeroPadding(32),
        block_size=32
        )
    for root, dirs, files in os.walk(input_folder, topdown=False):
        for f in files:
            src = os.path.realpath(os.path.join(root, f))
            if ".manifest" in src:
                print("processing " + src + "...")
                try:
                    rj256dec(src, f, rijndael_cbc, output_folder)
                except AssertionError:
                    print('len(source) \% self.block_size != 0! File skipped.')
                    # Please note that py3rijndael does not offer the none-padding.
                    # So Zero-padding will raise an AssertionError if dec_bin % blocksize != 0.
                    # If that happened, you can either
                    # 1) use C# program
                    # 2) modify the source code, change class RijndaelCbc(Rijndael).decrypt(self, cipher),
                    #    and comment "pt = self.padding.decode(ppt)" then change the return statement "return ppt".
                    
    print("finished.")

def rj256dec(enc, dec, rijndael_cbc, output_folder):
    with open(enc, "rb") as e:
        enc_bin = e.read()
        dec_bin = rijndael_cbc.decrypt(enc_bin)      
        with open(os.path.join(output_folder, dec), "wb") as d:
            d.write(dec_bin)
    
# Trash code
def decAll(archive_folder, dec_archive_folder, key, iv):
    for f in os.listdir(archive_folder):
        if os.path.isdir(os.path.join(archive_folder, f)):
            os.system('dec_v2.exe %s %s %s %s' % (bytes.decode(key), bytes.decode(iv), os.path.join(archive_folder, f), dec_archive_folder))
            print(os.path.join(archive_folder, f))

if __name__ == '__main__':
    parser = ArgumentParser(description = 'Decrypt the raw manifests with provided key and id.')
    parser.add_argument('-k', '--key', help ='Set the key (instead of loading it from key.txt)')
    parser.add_argument('-i', '--iv', help = 'Set the iv (instead of loading it from iv.txt)')
    args = parser.parse_args()

    key = args.key if args.key else load_key()
    iv = args.iv if args.iv else load_iv()
     
    check_keyiv(key, iv)
    decrypt(key, iv)