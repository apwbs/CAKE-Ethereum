import argparse
import requests
from decouple import config
import ssl

parser = argparse.ArgumentParser()
parser.add_argument('-hs' ,'--handshake', action='store_true')
parser.add_argument('-c' ,'--cipher', action='store_true')
parser.add_argument('-fr', '--full_request', action='store_true', help='Full request')
args = parser.parse_args()
process_instance_id = config('PROCESS_ID') #Process id generated after the attribute certification

entries = [['ID', 'SortAs', 'GlossTerm'],
    ['Acronym', 'Abbrev'],
    ['Specs', 'Dates', 'GlossTerm']]

policy = [process_instance_id + ' and (MANUFACTURER or SUPPLIER)',
        process_instance_id + ' and (MANUFACTURER or (SUPPLIER and ELECTRONICS))',
        process_instance_id + ' and (MANUFACTURER or (SUPPLIER and MECHANICS))']

g = open('../../files/data.json')

message_to_send = g.read()

server_cert = '../Keys/api.crt'
client_cert = '../Keys/client.crt'
client_key = '../Keys/client.key'


context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
context.load_cert_chain(certfile=client_cert, keyfile=client_key)

input = {'process_id': process_instance_id,
    'entries': entries,
    'policy' : policy, 
    'message': message_to_send}


if args.handshake:
    response = requests.post('http://127.0.0.1:8888/dataOwner/handshake',
        json = input,  cert=(client_cert, client_key), verify=server_cert)
    exit()

if args.cipher:
    response = requests.post('http://127.0.0.1:8888/dataOwner/cipher',
        json = input,  cert=(client_cert, client_key), verify=server_cert)
    exit()

if args.full_request:
    response = requests.post('http://127.0.0.1:8888/dataOwner/fullrequest',
        json = input,  cert=(client_cert, client_key), verify=server_cert)
    exit()