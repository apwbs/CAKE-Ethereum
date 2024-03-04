import requests
import argparse
from decouple import config
import ssl

parser = argparse.ArgumentParser()
parser.add_argument('-hs', '--handshake', action='store_true', help='Handshake')
parser.add_argument('-gk', '--generate_key', action='store_true', help='Generate key')
parser.add_argument('-ad','--access_data',  action='store_true', help='Access data')
parser.add_argument('-fr', '--full_request', action='store_true', help='Full request')
parser.add_argument('-s', '--slice', type=int, default=0)
parser.add_argument('-r', '--reader', type=int, default=0)
args = parser.parse_args()

process_instance_id = config('PROCESS_ID') #Process id generated after the attribute certification
slice_id = config('SLICE_ID_' + str(args.slice))
message_id = config('MESSAGE_ID')
reader_address = config('READER_' + str(args.reader))

server_cert = '../Keys/api.crt'
client_cert = '../Keys/client.crt'
client_key = '../Keys/client.key'


context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
context.load_cert_chain(certfile=client_cert, keyfile=client_key)


print("process_instance_id: {}".format(process_instance_id))
print("slice_id: {}".format(slice_id))
print("message_id: {}".format(message_id))
print("reader_address: {}".format(reader_address))

input = {'process_id' : process_instance_id,
    'slice_id' : slice_id,
    'message_id': message_id,
    'reader_address' : reader_address}

if args.handshake:
    response = requests.post('http://127.0.0.1:8888/client/handshake',
        json = input, cert=(client_cert, client_key), verify=server_cert)
    exit()
if args.generate_key:
    response = requests.post('http://127.0.0.1:8888/client/generateKey',
        json = input, cert=(client_cert, client_key), verify=server_cert)
    exit()
if args.access_data:
    response = requests.post('http://127.0.0.1:8888/client/accessData',
        json = input,  cert=(client_cert, client_key), verify=server_cert)
    exit()
if args.full_request:
    response = requests.post('http://127.0.0.1:8888/client/fullRequest',
        json = input)
    print(response.text, cert=(client_cert, client_key), verify=server_cert)
    exit()