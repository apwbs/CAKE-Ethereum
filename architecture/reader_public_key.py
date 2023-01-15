from decouple import config
from Crypto.PublicKey import RSA
import ipfshttpclient
import sqlite3
import io
import block_int

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

manufacturer_address = config('ADDRESS_MANUFACTURER')
manufacturer_private_key = config('PRIVATEKEY_MANUFACTURER')
electronics_address = config('ADDRESS_SUPPLIER1')
electronics_private_key = config('PRIVATEKEY_SUPPLIER1')
mechanics_address = config('ADDRESS_SUPPLIER2')
mechanics_private_key = config('PRIVATEKEY_SUPPLIER2')

reader_address = mechanics_address
private_key = mechanics_private_key

# Connection to SQLite3 reader database
conn = sqlite3.connect('files/reader/reader.db')
x = conn.cursor()

# # Connection to SQLite3 data_owner database
connection = sqlite3.connect('files/data_owner/data_owner.db')
y = connection.cursor()


def generate_keys():
    keyPair = RSA.generate(bits=1024)
    # print(f"Public key:  (n={hex(keyPair.n)}, e={hex(keyPair.e)})")
    # print(f"Private key: (n={hex(keyPair.n)}, d={hex(keyPair.d)})")

    f = io.StringIO()
    f.write('reader_address: ' + reader_address + '###')
    f.write(str(keyPair.n) + '###' + str(keyPair.e))
    f.seek(0)

    hash_file = api.add_json(f.read())
    print(f'ipfs hash: {hash_file}')

    block_int.send_publicKey(reader_address, private_key, hash_file)

    x.execute("INSERT OR IGNORE INTO rsa_private_key VALUES (?,?,?)", (reader_address, str(keyPair.n), str(keyPair.d)))
    conn.commit()

    x.execute("INSERT OR IGNORE INTO rsa_public_key VALUES (?,?,?,?)",
              (reader_address, hash_file, str(keyPair.n), str(keyPair.e)))
    conn.commit()

    y.execute("INSERT OR IGNORE INTO rsa_private_key VALUES (?,?,?)", (reader_address, str(keyPair.n), str(keyPair.d)))
    connection.commit()

    y.execute("INSERT OR IGNORE INTO rsa_public_key VALUES (?,?,?,?)",
              (reader_address, hash_file, str(keyPair.n), str(keyPair.e)))
    connection.commit()


if __name__ == "__main__":
    generate_keys()
