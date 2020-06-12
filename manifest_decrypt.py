import os
import time
import base64
import rijndael
from hashlib import sha256
from argparse import ArgumentParser

ROOT = os.path.dirname(os.path.realpath(__file__))
MANIFESTS = os.path.join(ROOT, 'manifests')
DEC = os.path.join(ROOT, 'dec_manifests')
os.makedirs(MANIFESTS, exist_ok=True)
os.makedirs(DEC, exist_ok=True)

def main():   
    for root, dirs, files in os.walk(MANIFESTS, topdown=False):
        for f in files:
            src = os.path.realpath(os.path.join(root, f))
            if ".manifest" in src:
                print("processing " + f + "...")
                rj256dec(src, f)
    print("finished.")


def rj256dec(enc, dec):
    with open(enc, "rb") as e:
        enc_bin = e.read()
        dec_bin = rijndael_cbc.decrypt(enc_bin)        
        with open(os.path.join(DEC, dec), "wb") as d:
            d.write(dec_bin)


if __name__ == '__main__':
    parser = ArgumentParser(description = 'Decrypt the raw manifests with provided key and id.')
    parser.add_argument('-m', '--method', default = 'cs', help = 'Using the compiled program(cs) or using the python version(py).')
    parser.add_argument('-k', '--key', help ='Set the key (instead of loading it from key.txt)')
    parser.add_argument('-i', '--iv', help = 'Set the iv (instead of loading it from iv.txt)')
    args = parser.parse_args()

    key = ''
    iv = ''

    if args.key:       
        key = args.key
    else:
        if not os.path.isfile("key.txt"):
            print("key.txt is needed")
            exit(1)
        with open("key.txt", "rb") as key_file:
            key = key_file.read()
    if args.iv:
        iv = args.iv
    else:
        if not os.path.isfile("iv.txt"):
            print("iv.txt is needed")
            exit(1)
        with open("iv.txt", "rb") as iv_file:
            iv = iv_file.read()
    
    if sha256(iv).hexdigest() != "4be4928a99aadafe05ed8a5fc16e1916917af64e344a366a33e2d29d5e2909ef":
        print("Invalid iv!")
        exit(1)
    if sha256(key).hexdigest() != "94799fb84532096a9bf33e5450b929a983efcf5a822e0637977f809406bb8688":
        print("Invalid key!")
        exit(1)

    if args.method == 'cs':
        os.system('dec.exe ' + bytes.decode(key) + ' ' + bytes.decode(iv))
    elif args.method == 'py':
        rijndael_cbc = rijndael.RijndaelCbc(
        key=base64.b64decode(key),
        iv=base64.b64decode(iv),
        block_size=32
        )
        main()
    else:
        print("Incorrect -m args! Enter \"py\" or \"cs\"!")
        exit(1)