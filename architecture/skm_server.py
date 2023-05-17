import socket
import ssl
import threading
import key_generation
import decipher_message
from datetime import datetime
import random
import sqlite3
from hashlib import sha512
import block_int
from decouple import config
import ipfshttpclient

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

process_instance_id = config('PROCESS_INSTANCE_ID')

HEADER = 64
PORT = int(config('SKM_PORT'))
server_cert = 'Keys/server.crt'
server_key = 'Keys/server.key'
client_certs = 'Keys/client.crt'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

"""
creation and connection of the secure channel using SSL protocol
"""

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile=server_cert, keyfile=server_key)
context.load_verify_locations(cafile=client_certs)
bindsocket = socket.socket()
bindsocket.bind(ADDR)
bindsocket.listen(5)


def generate(message_id, reader_address):
    return key_generation.main(message_id, reader_address)


def read(message_id, slice_id, reader_address):
    return decipher_message.main(message_id, slice_id, reader_address)


def generate_number_to_sign(message_id, reader_address):
    # Connection to SQLite3 skm database
    connection = sqlite3.connect('files/skm/skm.db')
    x = connection.cursor()

    now = datetime.now()
    now = int(now.strftime("%Y%m%d%H%M%S%f"))
    random.seed(now)
    number_to_sign = random.randint(1, 2 ** 64)

    x.execute("INSERT OR IGNORE INTO handshake_numbers VALUES (?,?,?,?)",
              (str(process_instance_id), message_id, reader_address, str(number_to_sign)))
    connection.commit()
    return number_to_sign


def check_handshake(message_id, reader_address, signature):
    # Connection to SQLite3 skm database
    connection = sqlite3.connect('files/skm/skm.db')
    x = connection.cursor()

    x.execute("SELECT * FROM handshake_numbers WHERE process_instance=?  AND message_id=? AND reader_address=?",
              (str(process_instance_id), message_id, reader_address))
    result = x.fetchall()
    number_to_sign = result[0][3]
    msg = str(number_to_sign).encode()
    public_key_ipfs_link = block_int.retrieve_publicKey(reader_address)
    getfile = api.cat(public_key_ipfs_link)
    getfile = getfile.split(b'###')
    public_key_n = int(getfile[1].decode('utf-8'))
    public_key_e = int(getfile[2].decode('utf-8').rstrip('"'))
    if getfile[0].split(b': ')[1].decode('utf-8') == reader_address:
        hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
        hashFromSignature = pow(int(signature), public_key_e, public_key_n)
        print("Signature valid:", hash == hashFromSignature)
        return hash == hashFromSignature


"""
function that handles the requests from the clients. There are two possible requests, namely the 
creation of a key and the deciphering of a ciphertext.
"""


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            # print(f"[{addr}] {msg}")
            conn.send("Msg received!".encode(FORMAT))
            message = msg.split('§')
            if message[0] == "Start handshake":
                number_to_sign = generate_number_to_sign(message[1], message[2])
                conn.send(b'Number to be signed: ' + str(number_to_sign).encode())
            if message[0] == "Generate my key":
                if check_handshake(message[1], message[2], message[3]):
                    response = generate(message[1], message[2])
                    response_0 = bytes(str(response[0]), FORMAT)
                    response_1 = bytes(str(response[1]), FORMAT)
                    conn.send(b'Here are the IPFS link and key: ' + response_0 + b'\n\n' + response_1)
            if message[0] == "Access my data":
                if check_handshake(message[1], message[3], message[4]):
                    response = read(message[1], message[2], message[3])
                    conn.send(b'Here are the plaintext and salt: ' + response[0] + b'\n\n' + response[1])

    conn.close()


"""
main function starting the server. It listens on a port and waits for a request from a client
"""


def start():
    bindsocket.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        newsocket, fromaddr = bindsocket.accept()
        conn = context.wrap_socket(newsocket, server_side=True)
        thread = threading.Thread(target=handle_client, args=(conn, fromaddr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()
