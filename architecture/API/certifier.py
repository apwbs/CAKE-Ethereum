from decouple import config
from Crypto.PublicKey import RSA
import ipfshttpclient
import sqlite3
import io
import block_int
import rsa
import random
from datetime import datetime
import json


class Certfier():
    def certify(actors):
        for actor in actors:
            Certfier.__read_public_key__(actor)
        Certfier.__skm_public_key__()
        Certfier.__attribute_certification__(actors)

    def __read_public_key__(actor_name):
        api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

        print("Reading keys of " + actor_name)
        reader_address = config('ADDRESS_' + actor_name)
        private_key = config('PRIVATEKEY_' + actor_name)

        # Connection to SQLite3 reader database
        conn = sqlite3.connect('..files/reader/reader.db')
        x = conn.cursor()

        # # Connection to SQLite3 data_owner database
        connection = sqlite3.connect('..files/data_owner/data_owner.db')
        y = connection.cursor()

        keyPair = RSA.generate(bits=1024)

        f = io.StringIO()
        f.write('reader_address: ' + reader_address + '###')
        f.write(str(keyPair.n) + '###' + str(keyPair.e))
        f.seek(0)

        hash_file = api.add_json(f.read())
        #print(f'ipfs hash: {hash_file}')
        print('ipfs hash: ' + str(hash_file))
        
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

    def __skm_public_key__():

        api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

        skm_address = config('SKM_ADDRESS')
        skm_private_key = config('SKM_PRIVATEKEY')

        # Connection to SQLite3 reader database
        conn = sqlite3.connect('..files/skm/skm.db')
        x = conn.cursor()

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


    def __attribute_certification__(actors):

        api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001') # Connect to local IPFS node (creo un nodo locale di ipfs)

        certifier_address = config('CERTIFIER_ADDRESS')
        certifier_private_key = config('CERTIFIER_PRIVATEKEY')

        # Connection to SQLite3 attribute_certifier database
        conn = sqlite3.connect('files/attribute_certifier/attribute_certifier.db') # Connect to the database
        x = conn.cursor()

        now = datetime.now()
        now = int(now.strftime("%Y%m%d%H%M%S%f"))
        random.seed(now)
        process_instance_id = random.randint(1, 2 ** 64)
        print(f'process instance id: {process_instance_id}')
        dict_users = {}
        for actor in actors:
            dict_users[config('ADDRESS_' + actor)] = [str(process_instance_id), actor]
        #dict_users = {for actor in actors: config('ADDRESS_' + actor): [str(process_instance_id), actor]}

        f = io.StringIO()
        dict_users_dumped = json.dumps(dict_users) # Metto su blockchain gli attributi degli utenti manufacter, supplier1 e supplier2
        f.write('"process_instance_id": ' + str(process_instance_id) + '####')
        f.write(dict_users_dumped)
        f.seek(0)

        file_to_str = f.read()

        hash_file = api.add_json(file_to_str)
        print(f'ipfs hash: {hash_file}')

        block_int.send_users_attributes(certifier_address, certifier_private_key, process_instance_id, hash_file)

        x.execute("INSERT OR IGNORE INTO user_attributes VALUES (?,?,?)",
                (str(process_instance_id), hash_file, file_to_str))
        conn.commit()