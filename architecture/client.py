import json
import socket
import ssl
from hashlib import sha512
from decouple import config
import sqlite3

# Connection to SQLite3 reader database
connection = sqlite3.connect('files/reader/reader.db')
x = connection.cursor()

process_instance_id = config('PROCESS_INSTANCE_ID')

HEADER = 64
PORT = 5051
FORMAT = 'utf-8'
server_sni_hostname = 'example.com'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "172.17.0.2"
ADDR = (SERVER, PORT)
server_cert = 'Keys/server.crt'
client_cert = 'Keys/client.crt'
client_key = 'Keys/client.key'

"""
creation and connection of the secure channel using SSL protocol
"""

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
context.load_cert_chain(certfile=client_cert, keyfile=client_key)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = context.wrap_socket(s, server_side=False, server_hostname=server_sni_hostname)
conn.connect(ADDR)


def sign_number(message_id):
    x.execute("SELECT * FROM handshake_number WHERE process_instance=? AND message_id=? AND reader_address=?",
              (process_instance_id, message_id, reader_address))
    result = x.fetchall()
    number_to_sign = result[0][3]

    x.execute("SELECT * FROM rsa_private_key WHERE reader_address=?", (reader_address,))
    result = x.fetchall()
    private_key = result[0]

    private_key_n = int(private_key[1])
    private_key_d = int(private_key[2])

    msg = bytes(str(number_to_sign), 'utf-8')
    hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
    signature = pow(hash, private_key_d, private_key_n)
    # print("Signature:", hex(signature))
    return signature



"""
function to handle the sending and receiving messages.
"""


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)
    receive = conn.recv(6000).decode(FORMAT)
    if len(receive) != 0:

        if receive[:15] == 'number to sign:':
            x.execute("INSERT OR IGNORE INTO handshake_number VALUES (?,?,?,?)",
                      (process_instance_id, message_id, reader_address, receive[16:]))
            connection.commit()

        if receive[:25] == 'Here is IPFS link and key':
            key = receive.split('\n\n')[0].split("b'")[1].rstrip("'")
            ipfs_link = receive.split('\n\n')[1]

            x.execute("INSERT OR IGNORE INTO decription_keys VALUES (?,?,?,?,?)",
                      (process_instance_id, message_id, reader_address, ipfs_link, key))
            connection.commit()

        if receive[:26] == 'Here is plaintext and salt':
            plaintext = receive.split('\n\n')[0].split('Here is plaintext and salt: ')[1]
            salt = receive.split('\n\n')[1]

            x.execute("INSERT OR IGNORE INTO plaintext VALUES (?,?,?,?,?,?)",
                      (process_instance_id, message_id, slice_id, reader_address, plaintext, salt))
            connection.commit()
            print(plaintext)


message_id = '16969972429370955301'
slice_id = '10021169745631875263'
reader_address = '0x9e7767d3753DBA2B546f93E8b20802162d88C885'

# send("Start handshake||" + str(message_id) + '||' + reader_address)

signature_sending = sign_number(message_id)

# send("Generate my key||" + message_id + '||' + reader_address + '||' + str(signature_sending))

send("Access my data||" + message_id + '||' + slice_id + '||' + reader_address + '||' + str(signature_sending))

# exit()

send(DISCONNECT_MESSAGE)
