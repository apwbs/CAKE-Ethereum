import sqlite3
from decouple import config
import ssl
import socket 
from hashlib import sha512

class CAKEBridge:
    def __init__(self, path_to_db, port, process_instance_id = config('PROCESS_INSTANCE_ID')):
        self.connection = sqlite3.connect(path_to_db)

        self.x = self.connection.cursor()

        # Read process instance id from .env file
        #self.process_instance_id = config('PROCESS_INSTANCE_ID')
        self.process_instance_id = process_instance_id
        print("Process instance id:", self.process_instance_id)
        # Set up connection parameters
        # TODO: Move this to a config file
        self.HEADER = 64
        self.PORT = port
        self.FORMAT = 'utf-8'
        self.server_sni_hostname = 'Sapienza'
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.SERVER = "172.17.0.2"
        self.ADDR = (self.SERVER, self.PORT)

        # Set up SSL parameters
        self.server_cert = '../Keys/server.crt'
        self.client_cert = '../Keys/client.crt'
        self.client_key = '../Keys/client.key'

        self.__connect__()

    ### Connect to the server
    def __connect__(self):
        """
        Creation and connection of the secure channel using SSL protocol
        """
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=self.server_cert)
        context.load_cert_chain(certfile=self.client_cert, keyfile=self.client_key)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = context.wrap_socket(s, server_side=False, server_hostname=self.server_sni_hostname)
        self.conn.connect(self.ADDR)
        return
        
    def disconnect(self):
        print("Disconnecting")
        self.send(self.DISCONNECT_MESSAGE)
        return
    
    def sign_number(self, number_to_sign, reader_address): 
        self.x.execute("SELECT * FROM rsa_private_key WHERE reader_address=?", (reader_address,))
        result = self.x.fetchall()
        print(result)
        private_key = result[0]

        private_key_n = int(private_key[1])
        private_key_d = int(private_key[2])

        msg = bytes(str(number_to_sign), 'utf-8')
        hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
        signature = pow(hash, private_key_d, private_key_n)
        return signature