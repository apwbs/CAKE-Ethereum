import sqlite3
from decouple import config
import ssl
import socket 
from hashlib import sha512

class CAKEBridge:
    """A communication bridge between the CAKE servers and the API server

    A class to manage the communication between the CAKE servers and the API server

    Attributes:
        connection (sqlite3.Connection): connection to the database
        x (sqlite3.Cursor): cursor to the database
        process_instance_id (int): process instance id
        HEADER (int): header size
        PORT (int): port number
        FORMAT (str): format
        server_sni_hostname (str): server sni hostname
        DISCONNECT_MESSAGE (str): disconnect message
        SERVER (str): server address
        ADDR (tuple): server address and port
        server_cert (str): server certificate
        client_cert (str): client certificate
        client_key (str): client key
        conn (ssl.SSLSocket): connection to the server
    """
    def __init__(self, path_to_db, port, process_instance_id = config('PROCESS_INSTANCE_ID')):
        """Initialize the CAKEBridge class

        Args:
            path_to_db (str): path to the database
            port (int): port number
            process_instance_id (int, optional): process instance id. Defaults to config('PROCESS_INSTANCE_ID').
        """
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
        self.server_sni_hostname = config('SERVER_SNI_HOSTNAME')
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.SERVER = config('SERVER')
        self.ADDR = (self.SERVER, self.PORT)

        # Set up SSL parameters
        self.server_cert = 'Keys/server.crt'
        self.client_cert = 'Keys/client.crt'
        self.client_key = 'Keys/client.key'

        self.__connect__()

    ### Connect to the server
    def __connect__(self):
        """Creation and connection of the secure channel using SSL protocol """
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=self.server_cert)
        context.load_cert_chain(certfile=self.client_cert, keyfile=self.client_key)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = context.wrap_socket(s, server_side=False, server_hostname=self.server_sni_hostname)
        self.conn.connect(self.ADDR)
        return
        
    def disconnect(self):
        """Disconnect from the server"""
        print("Disconnecting")
        self.send(self.DISCONNECT_MESSAGE)
        return
    
    def sign_number(self, number_to_sign, reader_address):
        """Sign a number using the private key of the reader
        
        Args:
            number_to_sign (int): Number to be signed
            reader_address (str): address of the reader
        
        Returns:
            int: signature of the number
        """
        self.x.execute("SELECT * FROM rsa_private_key WHERE reader_address=?", (reader_address,))
        result = self.x.fetchall()
        private_key = result[0]

        private_key_n = int(private_key[1])
        private_key_d = int(private_key[2])

        msg = bytes(str(number_to_sign), 'utf-8')
        hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
        signature = pow(hash, private_key_d, private_key_n)
        return signature