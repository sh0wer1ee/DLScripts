# decrypt /manifests_archive/*/*.manifest to /dec_manifests/

# The python implementation is verrrrry slow, so I use a compiled C# program to complete the work.

import os
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