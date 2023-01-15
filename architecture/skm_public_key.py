import rsa
from decouple import config
import ipfshttpclient
import sqlite3
import io
import block_int

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

skm_address = config('SKM_ADDRESS')
skm_private_key = config('SKM_PRIVATEKEY')

# Connection to SQLite3 reader database
conn = sqlite3.connect('files/skm/skm.db')
x = conn.cursor()


def generate_keys():
    (publicKey, privateKey) = rsa.newkeys(1024)
    publicKey_store = publicKey.save_pkcs1().decode('utf-8')
    privateKey_store = privateKey.save_pkcs1().decode('utf-8')

    f = io.StringIO()
    f.write('skm_address: ' + skm_address + '###')
    f.write(publicKey_store)
    f.seek(0)

    hash_file = api.add_json(f.read())
    print(f'ipfs hash: {hash_file}')

    block_int.send_publicKey(skm_address, skm_private_key, hash_file)

    x.execute("INSERT OR IGNORE INTO rsa_private_key VALUES (?,?)", (skm_address, privateKey_store))
    conn.commit()

    x.execute("INSERT OR IGNORE INTO rsa_public_key VALUES (?,?,?)", (skm_address, hash_file, publicKey_store))
    conn.commit()


if __name__ == "__main__":
    generate_keys()
