from charm.toolbox.ABEnc import ABEnc
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.toolbox.pairinggroup import PairingGroup, GT
from charm.core.engine.util import objectToBytes, bytesToObject
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.core.math.pairing import hashPair as sha2, deserialize, serialize
import json
import random
import hashlib
import base64
import encoders_decoders
from datetime import datetime
import block_int
import ipfshttpclient
import ast
from decouple import config

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

skm_address = config('SKM_ADDRESS')
sdm_address = config('SDM_ADDRESS')
sdm_private_key = config('SDM_PRIVATEKEY')


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

    def encrypt(self, pk, M, object):
        key = self.group.random(GT)
        c1 = self.abenc.encrypt(pk, key, object)
        cipher = AuthenticatedCryptoAbstraction(sha2(key))
        c2 = cipher.encrypt(M)
        return {'c1': c1, 'c2': c2}


"""
- creation of the "shared secret" between SDM and SKM, namely (pk,mk) keys
- ciphering of the message with the policy
- call to the "write" module to write the IPFS file with all necessary data of the message
"""


def main(message, entries, access_policy, sender):
    groupObj = PairingGroup('SS512')
    cpabe = CPabe_BSW07(groupObj)
    hyb_abe = HybridABEnc(cpabe, groupObj)

    (pk, mk) = hyb_abe.setup()

    pk_bytes = objectToBytes(pk, groupObj)
    pk_bytes_64 = base64.b64encode(pk_bytes).decode('ascii')

    mk_bytes = objectToBytes(mk, groupObj)
    mk_bytes_encoded = encoders_decoders.mk_encoder(mk_bytes, skm_address)
    mk_bytes_encoded_64 = base64.b64encode(mk_bytes_encoded).decode('ascii')

    access_policy = access_policy.split('###')

    if len(access_policy) == 1:
        message = json.dumps(json.loads(message))
        message_ciphered = hyb_abe.encrypt(pk, message, access_policy[0])
        message_ciphered_bytes = objectToBytes(message_ciphered, groupObj)
        cipher_bytes_64 = base64.b64encode(message_ciphered_bytes).decode('ascii')

        now = datetime.now()
        now = int(now.strftime("%Y%m%d%H%M%S%f"))
        random.seed(now)
        message_id = random.randint(1, 2 ** 64)
        print(f'message id: {message_id}')

        salt = random.randint(1, 2 ** 64)
        salt_to_encrypt = str(salt).encode()
        salt_with_policy = hyb_abe.encrypt(pk, salt_to_encrypt, access_policy[0])
        salt_with_policy_bytes = objectToBytes(salt_with_policy, groupObj)
        salt_with_policy_bytes_64 = base64.b64encode(salt_with_policy_bytes).decode('ascii')

        s_1 = message + str(salt)
        s_1 = s_1.encode()
        s_1_hashed = hashlib.sha256(s_1)
        hex_dig = s_1_hashed.hexdigest()

        json_encoded_list = [hex_dig, salt_with_policy_bytes_64]
        final_messages_parts = [(json_encoded_list, cipher_bytes_64)]
        json_encoded_list = json.dumps(final_messages_parts)

        header = {'sender': sender, 'message_id': message_id, 'pk': pk_bytes_64, 'mk': mk_bytes_encoded_64}

        final_message = {'header': header, 'body': json_encoded_list}

        hash_file = api.add_json(final_message)
        print(f'ipfs hash: {hash_file}')

        block_int.send_MessageIPFSLink(sender, sdm_private_key, message_id, hash_file)

        return message_id

    else:
        now = datetime.now()
        now = int(now.strftime("%Y%m%d%H%M%S%f"))
        random.seed(now)
        message_dict = json.loads(message)
        entries = entries.split('###')
        decoded = [ast.literal_eval(y) for y in entries]

        final_messages_parts = []
        for i, entry in enumerate(decoded):
            json_file_ciphered = {}

            slices = []
            slice_id = random.randint(1, 2 ** 64)
            print(f'slice id: {slice_id}')
            slices.append(slice_id)

            salt_message = []

            message_with_salt_hash = []
            for field in entry:
                json_file_ciphered[field] = message_dict[field]
            json_file_ciphered_string = json.dumps(json_file_ciphered)
            message_salt = json_file_ciphered_string
            cipher = hyb_abe.encrypt(pk, json_file_ciphered_string, access_policy[i])
            cipher_bytes = objectToBytes(cipher, groupObj)
            cipher_bytes_64 = base64.b64encode(cipher_bytes).decode('ascii')

            salt = random.randint(1, 2 ** 64)
            salt_to_encrypt = str(salt).encode()
            salt_with_policy = hyb_abe.encrypt(pk, salt_to_encrypt, access_policy[i])
            salt_with_policy_bytes = objectToBytes(salt_with_policy, groupObj)
            salt_with_policy_bytes_64 = base64.b64encode(salt_with_policy_bytes).decode('ascii')
            salt_message.append(salt_with_policy_bytes_64)

            s_1 = message_salt + str(salt)
            s_1 = s_1.encode()
            s_1_hashed = hashlib.sha256(s_1)
            hex_dig = s_1_hashed.hexdigest()
            message_with_salt_hash.append(hex_dig)

            zipped = zip(slices, message_with_salt_hash, salt_message)
            zipped_list = list(zipped)
            final_messages_parts.append((zipped_list, cipher_bytes_64))

        message_id = random.randint(1, 2 ** 64)
        print(f'message id: {message_id}')

        json_encoded_list = json.dumps(final_messages_parts)

        header = {'sender': sender, 'message_id': message_id, 'pk': pk_bytes_64, 'mk': mk_bytes_encoded_64}

        final_message = {'header': header, 'body': json_encoded_list}

        hash_file = api.add_json(final_message)
        print(f'ipfs hash: {hash_file}')

        block_int.send_MessageIPFSLink(sdm_address, sdm_private_key, sender, message_id, hash_file)

        return message_id
