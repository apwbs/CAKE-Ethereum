    
from decouple import config
from hashlib import sha512
from CAKEBridge import CAKEBridge

class CAKEDataOwner(CAKEBridge):

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
        signature_sending = self.sign_number(self.process_instance_id, self.manufacturer_address)
        self.send("Cipher this message||" + message_to_send + '||' + entries_string + '||' + policy_string + '||' + self.manufacturer_address   + '||' + str(signature_sending))
        self.disconnect()
        return