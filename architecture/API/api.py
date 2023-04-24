import sqlite3
from flask import Flask, request
import json
from decouple import config
from hashlib import sha512
from certifier import Certifier
from CAKEClient import CAKEClient
from CAKEDataOwner import CAKEDataOwner

app = Flask(__name__)

def getClientArgs(request):
    process_id = request.json.get('process_id')
    reader_address = request.json.get('reader_address')
    message_id = request.json.get('message_id')
    slice_id = request.json.get('slice_id')

    print("Reader_address is: " + reader_address)
    print("Message_id is: " + message_id)
    if slice_id is not None:
        print("Slice_id is: " + slice_id)
    print("Process_id is: " + str(process_id))
    return reader_address, message_id, slice_id, process_id

def getDataOwnerArgs(request):
    return

@app.route('/')
def go_home():
    return 'Welcome to the CAKE API'

#### Request from client to SKM Server ####
@app.route('/client/handshake/' , methods=['GET', 'POST'])
def client_handshake():
    reader_address, message_id, _, process_id = getClientArgs(request)
    if reader_address == '' or message_id == '':
        return "Missing parameters" , 400   
    client = CAKEClient(message_id=message_id, reader_address=reader_address, process_instance_id=process_id)
    client.handshake()
    #client.disconnect()
    return "Handshake completed" , 200

@app.route('/client/generateKey/' , methods=['GET', 'POST'])
def generateKey():
    reader_address, message_id, _, process_id = getClientArgs(request)
    if reader_address == '' or message_id == '':
        print("Missing parameters")
        return "Missing parameters" , 400
    client = CAKEClient(message_id=message_id, reader_address=reader_address, process_instance_id = process_id)
    client.generate_key()
    return "Key generated"

@app.route('/client/accessData/' , methods=['GET', 'POST'])
def accessData():
    reader_address, message_id, slice_id, process_id = getClientArgs(request)
    if reader_address == '' or message_id == '' or slice_id == '':
        return "Missing parameters" , 400
    client = CAKEClient(message_id=message_id, reader_address=reader_address, slice_id=slice_id, process_instance_id= process_id)
    client.access_data()
    #client.disconnect()   

    return "Data accessed"

# This is a full request, it does handshake, generate key and access data
@app.route('/client/fullrequest/' , methods=['GET', 'POST'])
def client_fullrequest():
    reader_address, message_id, slice_id, process_id = getClientArgs(request)
    if reader_address == '' or message_id == '' or slice_id == '':
        return "Missing parameters" , 400
    client = CAKEClient(message_id=message_id, reader_address=reader_address, slice_id=slice_id, process_instance_id= process_id)
    client.handshake()
    print("Handshake launched")
    client = CAKEClient(message_id=message_id, reader_address=reader_address, slice_id=slice_id, process_instance_id= process_id)
    client.generate_key()
    print("Key generation launched")    
    client = CAKEClient(message_id=message_id, reader_address=reader_address, slice_id=slice_id, process_instance_id= process_id)
    client.access_data()
    print("Data access launched")
    return "Handshake completed"

##### Request from Data Owner to SDM Server #####

@app.route('/dataOwner/handshake/' , methods=['POST'])
def data_owner_handshake():
    data_owner = CAKEDataOwner(process_instance_id=request.json.get('process_id'))
    data_owner.handshake()
    return "Handshake completed"

@app.route('/dataOwner/cipher/', methods=['POST'])
def cipher():
    message = request.json.get('message')
    if len(message) == 0:
        return "Missing parameters" , 400
    entries = request.json.get('entries')
    policy = request.json.get('policy')
    if len(entries) == 0:
        return "Missing parameters" , 400
    if len(policy) == 0:
        return "Missing parameters" , 400
    
    #TODO: Check if it is mandatory
    if len(entries) != len(policy):
        return "Entries and policy legth doesn't match" , 400   

    entries_string = '###'.join(str(x) for x in entries)
    policy_string = '###'.join(str(x) for x in policy)

    print("Message is: " + message)
    print("Entries are: " + entries_string)
    print("Policy is: " + policy_string)

    data_owner = CAKEDataOwner(process_instance_id=request.json.get('process_id'))
    data_owner.cipher_data(message, entries_string, policy_string)
    return "Cipher completed"

@app.route('/dataOwner/fullrequest/', methods=['POST'])
def dataowner_fullrequest():
    message = request.json.get('message')
    if len(message) == 0:
        return "Missing parameters" , 400
    entries = request.json.get('entries')
    policy = request.json.get('policy')
    if len(entries) == 0:
        return "Missing parameters" , 400
    if len(policy) == 0:
        return "Missing parameters" , 400
    
    #TODO: Check if it is mandatory
    if len(entries) != len(policy):
        return "Entries and policy legth doesn't match" , 400   

    entries_string = '###'.join(str(x) for x in entries)
    policy_string = '###'.join(str(x) for x in policy)
    message = json.dumps(message)
    data_owner = CAKEDataOwner(process_instance_id=request.json.get('process_id'))
    data_owner.handshake()
    data_owner = CAKEDataOwner(process_instance_id=request.json.get('process_id'))
    data_owner.cipher_data(message, entries_string, policy_string)
    return "Full request completed"

@app.route('/certification/', methods=['POST'])
def certification():
    actors = request.json.get('actors')
    roles = request.json.get('roles')
    Certifier.certify(actors, roles)
    return "Certification done"

@app.route('/certification/readpublickey/', methods=['POST'])
def read_public_key():
    actors = request.json.get('actors')
    #roles = request.json.get('roles')
    Certifier.read_public_key(actors)
    return "Public keys read"

@app.route('/certification/skmpublickey/', methods=['GET', 'POST'])
def skm_public_key():
    Certifier.skm_public_key()
    return "SKM public key read"

@app.route('/certification/attributecertification/', methods=['POST'])
def attribute_certification():
    #actors = request.json.get('actors')
    roles = request.json.get('roles')
    Certifier.attribute_certification(roles)
    return "Attribute certification done"

if __name__ == '__main__':
    app.run(port=8888)
