from charm.toolbox.ABEnc import ABEnc
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.core.math.pairing import hashPair as sha2
from charm.core.engine.util import objectToBytes, bytesToObject
import json
import sqlite3
import ipfshttpclient
from decouple import config
import base64
import block_int

process_instance_id = config('PROCESS_INSTANCE_ID')

"""
Necessary ABE connections
"""


class HybridABEnc(ABEnc):
    def __init__(self, scheme, groupObj):
        ABEnc.__init__(self)
        # check properties (TODO)
        self.abenc = scheme
        self.group = groupObj

    def setup(self):
        return self.abenc.setup()

    def decrypt(self, pk, sk, ct):
        c1, c2 = ct['c1'], ct['c2']
        key = self.abenc.decrypt(pk, sk, c1)
        if key is False:
            return b' '
            # raise Exception("failed to decrypt!")
        cipher = AuthenticatedCryptoAbstraction(sha2(key))
        return cipher.decrypt(c2)


"""
"""


def main(message_id, slice_id, reader_address):
    # Connection to SQLite3 skm database
    conn = sqlite3.connect('files/skm/skm.db')
    x = conn.cursor()

    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    global groupObj
    groupObj = PairingGroup('SS512')
    cpabe = CPabe_BSW07(groupObj)
    hyb_abe = HybridABEnc(cpabe, groupObj)

    msg_ipfs_link = block_int.retrieve_MessageIPFSLink(int(message_id))
    ciphertext_link = msg_ipfs_link[0]
    getfile1 = api.cat(ciphertext_link)
    j2 = json.loads(getfile1)

    pk = j2['header']['pk'].encode()
    pk = base64.b64decode(pk)
    pk = bytesToObject(pk, groupObj)

    if int(slice_id) != 0:
        body = json.loads(j2['body'])
        for i, elem in enumerate(body):
            slice_number = body[i][0][0][0]
            if slice_number == int(slice_id):
                message = body[i][1]
                message = base64.b64decode(message)
                message = bytesToObject(message, groupObj)

                salt = body[i][0][0][2]
                salt = base64.b64decode(salt)
                salt = bytesToObject(salt, groupObj)

                x.execute(
                    "SELECT * FROM generated_key_reader WHERE process_instance_id=? AND message_id=? AND reader_address=?",
                    (process_instance_id, message_id, reader_address))
                result = x.fetchall()
                sk = result[0][4]
                sk = bytesToObject(sk, groupObj)

                mdec = hyb_abe.decrypt(pk, sk, message)
                saltdec = hyb_abe.decrypt(pk, sk, salt)

                return mdec, saltdec
    else:
        body = json.loads(j2['body'])

        message = body[0][1]
        message = base64.b64decode(message)
        message = bytesToObject(message, groupObj)

        salt = body[0][0][1]
        salt = base64.b64decode(salt)
        salt = bytesToObject(salt, groupObj)

        x.execute(
            "SELECT * FROM generated_key_reader WHERE process_instance_id=? AND message_id=? AND reader_address=?",
            (process_instance_id, message_id, reader_address))
        result = x.fetchall()
        sk = result[0][4]
        sk = bytesToObject(sk, groupObj)

        mdec = hyb_abe.decrypt(pk, sk, message)
        saltdec = hyb_abe.decrypt(pk, sk, salt)

        return mdec, saltdec
