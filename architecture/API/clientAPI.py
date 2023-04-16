import sqlite3
from flask import Flask, request
import json
from decouple import config
import ssl
import socket 
from hashlib import sha512

app = Flask(__name__)

class CAKEClient:
    def __init__(self):
        # Connection to SQLite3 reader database
        self.connection = sqlite3.connect('../files/reader/reader.db')

        self.x = self.connection.cursor()

        # Read process instance id from .env file
        self.process_instance_id = config('PROCESS_INSTANCE_ID')
        print("Process instance id:", self.process_instance_id)
        # Set up connection parameters
        # TODO: Move this to a config file
        self.HEADER = 64
        self.PORT = 5051
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
        
    def sign_number(self, message_id, reader_address):
        self.x.execute("SELECT * FROM handshake_number WHERE process_instance=? AND message_id=? AND reader_address=?",
                (self.process_instance_id, message_id, reader_address))
        result = self.x.fetchall()
        number_to_sign = result[0][3]

        self.x.execute("SELECT * FROM rsa_private_key WHERE reader_address=?", (reader_address,))
        result = self.x.fetchall()
        print(result)
        private_key = result[0]

        private_key_n = int(private_key[1])
        private_key_d = int(private_key[2])

        msg = bytes(str(number_to_sign), 'utf-8')
        hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
        signature = pow(hash, private_key_d, private_key_n)
        # print("Signature:", hex(signature))
        return signature

    def send(self, msg, message_id = None, reader_address = None, slice_id = None):
        message = msg.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.conn.send(send_length)
        self.conn.send(message)
        receive = self.conn.recv(6000).decode(self.FORMAT)
        if len(receive) != 0:
            print(receive)
            if receive[:15] == 'number to sign:':
                self.x.execute("INSERT OR IGNORE INTO handshake_number VALUES (?,?,?,?)",
                        (self.process_instance_id, message_id, reader_address, receive[16:]))
                self.connection.commit()

            if receive[:25] == 'Here is IPFS link and key':
                key = receive.split('\n\n')[0].split("b'")[1].rstrip("'")
                ipfs_link = receive.split('\n\n')[1]
    
                self.x.execute("INSERT OR IGNORE INTO decription_keys VALUES (?,?,?,?,?)",
                        (self.process_instance_id, message_id, reader_address, ipfs_link, key))
                self.connection.commit()

            if receive[:26] == 'Here is plaintext and salt':
                plaintext = receive.split('\n\n')[0].split('Here is plaintext and salt: ')[1]
                salt = receive.split('\n\n')[1]

                self.x.execute("INSERT OR IGNORE INTO plaintext VALUES (?,?,?,?,?,?)",
                        (self.process_instance_id, message_id, slice_id, reader_address, plaintext, salt))
                self.connection.commit()
                print(plaintext)
        return receive
    
    def disconnect(self):
        self.send(self.DISCONNECT_MESSAGE)
        return ""
    
    def handshake(self, reader_address, message_id):
        self.send("Start handshake||" + str(message_id) + '||' + reader_address, message_id, reader_address)
        return ""
    
    def generate_key(self, reader_address, message_id):
        signature_sending = self.sign_number(message_id, reader_address)
        self.send("Generate my key||" + message_id + '||' + reader_address + '||' + str(signature_sending), message_id, reader_address)
        return ""
    
    def access_data(self, reader_address, message_id, slice_id):
        signature_sending = self.sign_number(message_id, reader_address)
        return self.send("Access my data||" + message_id + '||' + slice_id + '||' + reader_address + '||' + str(signature_sending), message_id, reader_address, slice_id)

@app.route('/')
def go_home():
    return 'Welcome to the CAKE API'


@app.route('/handshake/' , methods=['GET', 'POST'])
def handshake():
    reader_address = request.args.get('reader_address', default = '', type = str)
    message_id = request.args.get('message_id', default = '', type = str)
    if reader_address == '' or message_id == '':
        return "Missing parameters" , 400
    client = CAKEClient()
    client.handshake(reader_address, message_id)
    client.disconnect()
    return "Handshake completed" , 200

@app.route('/generateKey/' , methods=['GET', 'POST'])
def generateKey():
    reader_address = request.args.get('reader_address', default = '', type = str)
    message_id = request.args.get('message_id', default = '', type = str)
    if reader_address == '' or message_id == '':
        print("Missing parameters")
        return "Missing parameters" , 400
    print("Reader_address is: " + reader_address)
    print("Message_id is: " + message_id)
    client = CAKEClient()
    client.generate_key(reader_address, message_id)
    client.disconnect()
    return "Key generated"

@app.route('/accessData/' , methods=['GET', 'POST'])
def accessData():
    reader_address = request.args.get('reader_address', default = '', type = str)
    message_id = request.args.get('message_id', default = '', type = str)
    slice_id = request.args.get('slice_id', default = '', type = str)
    if reader_address == '' or message_id == '' or slice_id == '':
        return "Missing parameters" , 400
    print("Reader_address is: " + reader_address)
    print("Message_id is: " + message_id)
    print("Slice_id is: " + slice_id)
    client = CAKEClient()
    client.access_data(reader_address, message_id, slice_id)
    client.disconnect()   

    return "Data accessed"

# This is a full request, it does handshake, generate key and access data
@app.route('/fullrequest/' , methods=['GET', 'POST'])
def fullrequest():
    reader_address = request.args.get('reader_address', default = '', type = str)
    message_id = request.args.get('message_id', default = '', type = str)
    slice_id = request.args.get('slice_id', default = '', type = str)
    if reader_address == '' or message_id == '' or slice_id == '':
        return "Missing parameters" , 400
    client = CAKEClient()
    client.handshake(reader_address, message_id)
    client.disconnect()
    client.generate_key(reader_address, message_id)
    client.disconnect()
    client.access_data(reader_address, message_id, slice_id)
    client.disconnect()
    return "Handshake completed"

@app.route('/test/', methods=['GET', 'POST'])
def test():
    content = request.args.get('content', default = 'test', type = str)
    filter = request.args.get('filter', default = '*', type = str)
    print("Content is " + content)
    return content

if __name__ == '__main__':
    app.run(port=8888)
