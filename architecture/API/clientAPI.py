import sqlite3
from flask import Flask, request
import json
from decouple import config
import ssl
import socket 
from hashlib import sha512

app = Flask(__name__)

def sign_number(database, process_instance_id, message_id, reader_address): 
    database.execute("SELECT * FROM handshake_number WHERE process_instance=? AND message_id=? AND reader_address=?",
            (process_instance_id, message_id, reader_address))
    result = database.fetchall()
    print(result)
    number_to_sign = result[0][3]

    database.execute("SELECT * FROM rsa_private_key WHERE reader_address=?", (reader_address,))
    result = database.fetchall()
    print(result)
    private_key = result[0]

    private_key_n = int(private_key[1])
    private_key_d = int(private_key[2])

    msg = bytes(str(number_to_sign), 'utf-8')
    hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
    signature = pow(hash, private_key_d, private_key_n)
    return signature

class CAKEConnection:
    def __init__(self, path_to_db, port):
        self.connection = sqlite3.connect(path_to_db)

        self.x = self.connection.cursor()

        # Read process instance id from .env file
        self.process_instance_id = config('PROCESS_INSTANCE_ID')
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


### This class is equivalent to the content of ../client.py
class CAKEClient(CAKEConnection):
    ### Initialize the class with the information to connect to the server and the DB.
    ### The information of message_id, reader_address and slice_id are optional,
    ### they are used to sign the message and the can be changed or setted later
    def __init__(self, message_id = "", reader_address = "", slice_id = ""):

        super().__init__(path_to_db='../files/reader/reader.db', port=5051)
        self.__setArgs__(message_id, reader_address, slice_id)
        return

    def __setArgs__(self, message_id, reader_address, slice_id = ""):
        self.message_id = message_id
        self.reader_address = reader_address
        self.slice_id = slice_id
        return

    def send(self, msg):
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
                        (self.process_instance_id, self.message_id, self.reader_address, receive[16:]))
                self.connection.commit()

            if receive[:25] == 'Here is IPFS link and key':
                key = receive.split('\n\n')[0].split("b'")[1].rstrip("'")
                ipfs_link = receive.split('\n\n')[1]
    
                self.x.execute("INSERT OR IGNORE INTO decription_keys VALUES (?,?,?,?,?)",
                        (self.process_instance_id, self.message_id, self.reader_address, ipfs_link, key))
                self.connection.commit()

            if receive[:26] == 'Here is plaintext and salt':
                plaintext = receive.split('\n\n')[0].split('Here is plaintext and salt: ')[1]
                salt = receive.split('\n\n')[1]

                self.x.execute("INSERT OR IGNORE INTO plaintext VALUES (?,?,?,?,?,?)",
                        (self.process_instance_id, self.message_id, self.slice_id, self.reader_address, plaintext, salt))
                self.connection.commit()
                print(plaintext)
        return receive
    
        
    def handshake(self):
        self.send("Start handshake||" + str(self.message_id) + '||' + self.reader_address)
        self.disconnect()
        return
    
    def generate_key(self):
        signature_sending = sign_number(self.x, self.process_instance_id, self.message_id, self.reader_address)
        self.send("Generate my key||" + self.message_id + '||' + self.reader_address + '||' + str(signature_sending))
        self.disconnect()
        return
    
    def access_data(self):
        signature_sending = sign_number(self.x, self.process_instance_id, self.message_id, self.reader_address)
        self.send("Access my data||" + self.message_id + '||' + self.slice_id + '||' + self.reader_address + '||' + str(signature_sending))
        self.disconnect()
        return
    
class CAKEDataOwner(CAKEConnection):

    def __init__(self):
        super().__init__("../files/data_owner/data_owner.db", 5050)
        self.manufacturer_address = config('ADDRESS_MANUFACTURER')
        return
    
    """
    function to handle the sending and receiving messages.
    """
    def send(self, msg):
        message = msg.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.conn.send(send_length)
        # print(send_length)
        self.conn.send(message)
        receive = self.conn.recv(6000).decode(self.FORMAT)
        if len(receive) != 0:
            print(receive)
            if receive[:15] == 'Number to sign:':
                self.x.execute("INSERT OR IGNORE INTO handshake_number VALUES (?,?,?)",
                        (self.process_instance_id, self.sender, receive[16:]))
                self.connection.commit()

            if receive[:23] == 'Here is the message_id:':
                self.x.execute("INSERT OR IGNORE INTO messages VALUES (?,?,?)", (self.process_instance_id, self.sender, receive[16:]))
                self.connection.commit()

    def handshake(self):
        print("Start handshake")
        self.send("Start handshake||" + self.manufacturer_address)
        self.disconnect()
        return
    
    def cipher_data(self, message_to_send, entries_string, policy_string):
        signature_sending = sign_number(self.x, self.process_instance_id, self.manufacturer_address)
        self.send("Cipher this message||" + message_to_send + '||' + entries_string + '||' + policy_string + '||' + self.manufacturer_address   + '||' + str(signature_sending))
        self.disconnect()
        return


def getArgs(request):
    if request.method == 'GET':
        reader_address = request.args.get('reader_address', default = '', type = str)
        message_id = request.args.get('message_id', default = '', type = str)
        slice_id = request.args.get('slice_id', default = '', type = str)
    elif request.method == 'POST':
        reader_address = request.form.get('reader_address', default = '', type = str)
        message_id = request.form.get('message_id', default = '', type = str)
        slice_id = request.form.get('slice_id', default = '', type = str)

    print("Reader_address is: " + reader_address)
    print("Message_id is: " + message_id)
    if slice_id != '':
        print("Slice_id is: " + slice_id)
    return reader_address, message_id, slice_id


@app.route('/')
def go_home():
    return 'Welcome to the CAKE API'

#### Request from client to SKM Server ####
@app.route('/client/handshake/' , methods=['GET', 'POST'])
def handshake():
    reader_address, message_id = getArgs(request)
    if reader_address == '' or message_id == '':
        return "Missing parameters" , 400   
    client = CAKEClient(message_id=message_id, reader_address=reader_address)
    client.handshake()
    #client.disconnect()
    return "Handshake completed" , 200

@app.route('/client/generateKey/' , methods=['GET', 'POST'])
def generateKey():
    reader_address, message_id = getArgs(request)
    if reader_address == '' or message_id == '':
        print("Missing parameters")
        return "Missing parameters" , 400
    client = CAKEClient(message_id=message_id, reader_address=reader_address)
    client.generate_key()
    return "Key generated"

@app.route('/client/accessData/' , methods=['GET', 'POST'])
def accessData():
    reader_address, message_id, slice_id = getArgs(request)
    if reader_address == '' or message_id == '' or slice_id == '':
        return "Missing parameters" , 400
    client = CAKEClient(message_id=message_id, reader_address=reader_address, slice_id=slice_id)
    client.access_data()
    #client.disconnect()   

    return "Data accessed"

# This is a full request, it does handshake, generate key and access data
@app.route('/client/fullrequest/' , methods=['GET', 'POST'])
def clinet_fullrequest():
    reader_address, message_id, slice_id = getArgs(request)
    if reader_address == '' or message_id == '' or slice_id == '':
        return "Missing parameters" , 400
    client = CAKEClient(message_id=message_id, reader_address=reader_address, slice_id=slice_id)
    client.handshake()
    print("Handshake launched")
    client.generate_key()
    print("Key generation launched")    
    client.access_data()
    print("Data access launched")
    return "Handshake completed"

@app.route('dataowner/handshake/' , methods=['GET', 'POST'])
def handshake():
    data_owner = CAKEDataOwner()
    data_owner.handshake()
    return "Handshake completed"

@app.route('dataOwner/cipher/', methods=['POST'])
def cipher():
    message_json = request.form.get('message', default = '', type = str)
    if message_json == '':
        return "Missing parameters" , 400
    entries = request.form.get('entries', default = '', type = list)
    if len(entries) == 0:
        return "Missing parameters" , 400
    policy = request.form.get('policy', default = '', type = list)
    if len(policy.count) == 0:
        return "Missing parameters" , 400
    
    #TODO: Check if it is mandatory
    if entries.count != policy.count:
        return "Entries and policy legth doesn't match" , 400   

    entries_string = '###'.join(str(x) for x in entries)
    policy_string = '###'.join(str(x) for x in policy)
    
    data_owner = CAKEDataOwner()
    data_owner.cipher_data(message_json, entries_string, policy_string)
    return "Cipher completed"

@app.route('dataOwner/fullrequest/', methods=['POST'])
def dataowner_fullrequest():
    handshake()
    cipher()
    return "Full request completed"

if __name__ == '__main__':
    app.run(port=8888)
