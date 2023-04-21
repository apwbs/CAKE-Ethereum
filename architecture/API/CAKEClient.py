from decouple import config
from hashlib import sha512
from CAKEBridge import CAKEBridge

### This class is equivalent to the content of ../client.py
class CAKEClient(CAKEBridge):
    ### Initialize the class with the information to connect to the server and the DB.
    ### The information of message_id, reader_address and slice_id are optional,
    ### they are used to sign the message and the can be changed or setted later
    def __init__(self, process_instance_id = config('PROCESS_INSTANCE_ID'), message_id = "", reader_address = "", slice_id = ""):

        super().__init__(path_to_db='../files/reader/reader.db', port=5051, process_instance_id=process_instance_id)
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
        print(message)
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
        signature_sending = self.sign_number()
        self.send("Generate my key||" + self.message_id + '||' + self.reader_address + '||' + str(signature_sending))
        self.disconnect()
        return
    
    def access_data(self):
        signature_sending = self.sign_number()
        self.send("Access my data||" + self.message_id + '||' + self.slice_id + '||' + self.reader_address + '||' + str(signature_sending))
        self.disconnect()
        return
    
    def full_request(self):
        self.handshake()
        self.generate_key()
        self.access_data()
        return
    
    def sign_number(self):
        self.x.execute("SELECT * FROM handshake_number WHERE process_instance=? AND message_id=? AND reader_address=?",
                    (self.process_instance_id, self.message_id, self.reader_address))
        result = self.x.fetchall()
        print(result)
        number_to_sign = result[0][3]
        return super().sign_number(number_to_sign, self.reader_address)    