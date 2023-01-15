import sqlite3
import block_int
import ipfshttpclient
import rsa
import io

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')


def mk_encoder(mk, skm_address):
    skm_pk_link = block_int.retrieve_publicKey(skm_address)
    getfile = api.cat(skm_pk_link)
    getfile = getfile.split(b'###')
    if getfile[0].split(b': ')[1].decode('utf-8') == skm_address:
        publicKey_usable = rsa.PublicKey.load_pkcs1(getfile[1].rstrip(b'"').replace(b'\\n', b'\n'))

        info = [mk[i:i + 117] for i in range(0, len(mk), 117)]

        f = io.BytesIO()
        for part in info:
            crypto = rsa.encrypt(part, publicKey_usable)
            f.write(crypto)
        f.seek(0)

        file_to_str = f.read()
        return file_to_str


def mk_decoder(mk_encoded, skm_address):
    # Connection to SQLite3 reader database
    conn = sqlite3.connect('files/skm/skm.db')
    x = conn.cursor()

    x.execute("SELECT * FROM rsa_private_key WHERE reader_address = ?", (skm_address,))
    user_privateKey = x.fetchall()
    privateKey_usable = rsa.PrivateKey.load_pkcs1(user_privateKey[0][1])

    info2 = [mk_encoded[i:i + 128] for i in range(0, len(mk_encoded), 128)]
    final_bytes = b''

    for j in info2:
        message = rsa.decrypt(j, privateKey_usable)
        final_bytes = final_bytes + message

    return final_bytes
