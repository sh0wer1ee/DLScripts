using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Security.Cryptography;

namespace csharpstuff
{
    class MainClass
    {
        const string sha256_key = "94799fb84532096a9bf33e5450b929a983efcf5a822e0637977f809406bb8688";
        const string sha256_iv = "4be4928a99aadafe05ed8a5fc16e1916917af64e344a366a33e2d29d5e2909ef";

        public static int Main(string[] args)
        {
            var AssetBundleCryptKey = args[0];
            var AssetBundleCryptIV = args[1];
            Directory.CreateDirectory(@".\dec_manifests");
            string[] fileEntries = Directory.GetFiles(@".\manifests");
            foreach (string fileName in fileEntries)
            {
                if (fileName.Contains(".manifest"))
                {
                    Console.WriteLine("processing " + fileName + "...");
                    var raw_manifest = System.IO.File.ReadAllBytes(fileName);
                    var dec_manifest = Encryption.Decrypt(raw_manifest, AssetBundleCryptKey, AssetBundleCryptIV);
                    System.IO.File.WriteAllBytes(@".\dec_manifests\" + Path.GetFileName(fileName), dec_manifest);
                }
            }
            Console.WriteLine("finished.");
            return 0;
        }

        static string Sha256(string randomString)
        {
            var crypt = new System.Security.Cryptography.SHA256Managed();
            var hash = new System.Text.StringBuilder();
            byte[] crypto = crypt.ComputeHash(Encoding.UTF8.GetBytes(randomString));
            foreach (byte theByte in crypto)
            {
                hash.Append(theByte.ToString("x2"));
            }
            return hash.ToString();
        }

    }

    public static class Encryption
    {
        public static string Encrypt(string prm_text_to_encrypt, string prm_key, string prm_iv)
        {
            var sToEncrypt = prm_text_to_encrypt;

            var rj = new RijndaelManaged()
            {
                Padding = PaddingMode.PKCS7,
                Mode = CipherMode.CBC,
                KeySize = 256,
                BlockSize = 256,
            };

            var key = Convert.FromBase64String(prm_key);
            var IV = Convert.FromBase64String(prm_iv);

            var encryptor = rj.CreateEncryptor(key, IV);

            var msEncrypt = new MemoryStream();
            var csEncrypt = new CryptoStream(msEncrypt, encryptor, CryptoStreamMode.Write);

            var toEncrypt = Encoding.ASCII.GetBytes(sToEncrypt);

            csEncrypt.Write(toEncrypt, 0, toEncrypt.Length);
            csEncrypt.FlushFinalBlock();

            var encrypted = msEncrypt.ToArray();
            
            return (Convert.ToBase64String(encrypted).Replace("+", "-").Replace("/", "_").Replace("=", ","));
        }

        public static byte[] Decrypt(byte[] prm_text_to_decrypt, string prm_key, string prm_iv)
        {
            var sEncrypted = prm_text_to_decrypt;

            var rj = new RijndaelManaged()
            {
                Padding = PaddingMode.None,
                Mode = CipherMode.CBC,                             
                KeySize = 256,
                BlockSize = 256,
            };

            var key = Convert.FromBase64String(prm_key);           
            var IV = Convert.FromBase64String(prm_iv);

            var decryptor = rj.CreateDecryptor(key, IV);

            var fromEncrypt = new byte[sEncrypted.Length];

            var msDecrypt = new MemoryStream(sEncrypted);
            var csDecrypt = new CryptoStream(msDecrypt, decryptor, CryptoStreamMode.Read);

            csDecrypt.Read(fromEncrypt, 0, fromEncrypt.Length);
            return fromEncrypt;
        }

        public static void GenerateKeyIV(out string key, out string IV)
        {
            var rj = new RijndaelManaged()
            {
                Padding = PaddingMode.Zeros,
                Mode = CipherMode.CBC,
                KeySize = 256,
                BlockSize = 256,
            };
            rj.GenerateKey();
            rj.GenerateIV();

            key = Convert.ToBase64String(rj.Key);
            IV = Convert.ToBase64String(rj.IV);
        }
    }
}