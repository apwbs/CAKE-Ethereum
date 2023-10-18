import socket
import ssl
from hashlib import sha512
import json
from decouple import config
import sqlite3
import argparse
from connector import Connector

class CAKEDataOwner(Connector):
    """Tools to communicate from the API to the CAKE SDM server

    A class to manage the communication with the CAKE SDM server

    Attributes:
        manufacturer_address (str): manufacturer address
    """

    def __init__(self, process_instance_id = config('PROCESS_INSTANCE_ID')):
        """Initialize the CAKEDataOwner class

        Args:
            process_instance_id (int, optional): process instance id. Defaults to config('PROCESS_INSTANCE_ID').
        """        
        super().__init__("files/data_owner/data_owner.db", int(config('SDM_PORT')), process_instance_id=process_instance_id)
        self.manufacturer_address = config('ADDRESS_MANUFACTURER')
        return
    
    """
    function to handle the sending and receiving messages.
    """
    def send(self, msg):
        """Send a message to the CAKE SDM server

        Send a message to the CAKE SDM server and receive a response

        Args:
            msg (str): message to send
        """
        message = msg.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.conn.send(send_length)
        # print(send_length)
        self.conn.send(message)
        receive = self.conn.recv(6000).decode(self.FORMAT)
        #print(receive)
        if receive.startswith('Number to be signed: '):
            len_initial_message = len('Number to be signed: ')
            self.x.execute("INSERT OR IGNORE INTO handshake_number VALUES (?,?,?)",
                    (self.process_instance_id, self.manufacturer_address, receive[len_initial_message:]))
            self.connection.commit()
        if receive.startswith('Here is the message_id:'):
            self.x.execute("INSERT OR IGNORE INTO messages VALUES (?,?,?)", (self.process_instance_id, self.manufacturer_address, receive[16:]))
            self.connection.commit()

    def handshake(self):
        """Handshake with the CAKE SDM server"""

        print("Start handshake")
        self.send("Start handshake§" + self.manufacturer_address)
        self.disconnect()
        return
    
    def cipher_data(self, message_to_send, entries_string, policy_string):
        """Cipher a message and set the policy
        
        Args:
            message_to_send (str): message to send 
            entries_string (str): entries converted to string
            policy_string (str): policy converted to string"""
        signature_sending = self.sign_number()
        self.send("Cipher this message§" + message_to_send + '§' + entries_string + '§' + policy_string + '§' + self.manufacturer_address   + '§' + str(signature_sending))
        self.disconnect()
        return
    
    def sign_number(self):
        """Sign a number

        Sign a number and return the signature

        Returns:
            str: signature
        """
        self.x.execute("SELECT * FROM handshake_number WHERE process_instance=?", (self.process_instance_id,))
        result = self.x.fetchall()
        number_to_sign = result[0][2]
        return super().sign_number(number_to_sign, self.manufacturer_address)

if __name__ == "__main__":
    NO_SLICE = False
    # f = open('files/data.json')
    manufacturer_address = config('ADDRESS_MANUFACTURER')
    g = open('files/data.json')

    process_instance_id = config('PROCESS_INSTANCE_ID')

    message_to_send = g.read()

    # policy_string = '1604423002081035210 and (MANUFACTURER or (SUPPLIER and ELECTRONICS))'

    entries = [['ID', 'SortAs', 'GlossTerm'], ['Acronym', 'Abbrev'], ['Specs', 'Dates']]
    entries_string = '###'.join(str(x) for x in entries)
    #print(entries_string)
    policy = [process_instance_id + ' and (MANUFACTURER or SUPPLIER)',
            process_instance_id + ' and (MANUFACTURER or (SUPPLIER and ELECTRONICS))',
            process_instance_id + ' and (MANUFACTURER or (SUPPLIER and MECHANICS))']

    policy_string = '###'.join(policy)

    if NO_SLICE:
        data = json.load(open('files/data.json'))
        entries = [list(data.keys())]
        entries_string = '###'.join(str(x) for x in entries)
        print(entries_string)

        policy = process_instance_id + ' and (MANUFACTURER or (SUPPLIER and ELECTRONICS))'
        policy = [policy]
        policy_string = '###'.join(policy)

    sender = manufacturer_address

    parser = argparse.ArgumentParser()
    parser.add_argument('-hs' ,'--hanshake', action='store_true')
    parser.add_argument('-c','--cipher', action='store_true')
    dataOwner= CAKEDataOwner()
    args = parser.parse_args()
    if args.hanshake:
        dataOwner.handshake()

    if args.cipher:
        dataOwner.cipher_data(message_to_send, entries_string, policy_string)