from charm.toolbox.ABEnc import ABEnc
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.core.engine.util import objectToBytes, bytesToObject
import json
from decouple import config
import ipfshttpclient
import encoders_decoders
import base64
import sqlite3
import block_int

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

process_instance_id = config('PROCESS_INSTANCE_ID')

skm_address = config('SKM_ADDRESS')


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

    def keygen(self, pk, mk, object):
        return self.abenc.keygen(pk, mk, object)


"""
function that creates a key for the demanding client. The key is generated using the 
"shared secret" between the SDM and SKM, and the attributes of that particular client 
"""


def main(message_id, reader_address):
    # Connection to SQLite3 skm database
    conn = sqlite3.connect('files/skm/skm.db')
    x = conn.cursor()

    global groupObj
    groupObj = PairingGroup('SS512')
    cpabe = CPabe_BSW07(groupObj)
    hyb_abe = HybridABEnc(cpabe, groupObj)

    attr_ipfs_link = block_int.retrieve_users_attributes(process_instance_id)
    getfile = api.cat(attr_ipfs_link)
    getfile = getfile.replace(b'\\', b'')
    getfile = getfile.decode('utf-8').rstrip('"').lstrip('"')
    getfile = getfile.encode('utf-8')
    getfile = getfile.split(b'####')
    attributes_dict = json.loads(getfile[1].decode('utf-8'))
    user_attr = attributes_dict[reader_address]

    msg_ipfs_link = block_int.retrieve_MessageIPFSLink(int(message_id))
    ciphertext_link = msg_ipfs_link[0]
    getfile1 = api.cat(ciphertext_link)
    j2 = json.loads(getfile1)
    pk = j2['header']['pk'].encode()
    pk = base64.b64decode(pk)
    pk = bytesToObject(pk, groupObj)

    mk_encoded = j2['header']['mk'].encode()
    mk_encoded = base64.b64decode(mk_encoded)
    mk = encoders_decoders.mk_decoder(mk_encoded, skm_address)
    mk = bytesToObject(mk, groupObj)

    sk = hyb_abe.keygen(pk, mk, user_attr)
    user_sk_bytes = objectToBytes(sk, groupObj)

    x.execute("INSERT OR IGNORE INTO generated_key_reader VALUES (?,?,?,?,?)",
              (str(process_instance_id), message_id, msg_ipfs_link[0], reader_address, user_sk_bytes))
    conn.commit()

    return user_sk_bytes, msg_ipfs_link[0]
