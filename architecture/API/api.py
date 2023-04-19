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
    reader_address, message_id = getClientArgs(request)
    if reader_address == '' or message_id == '':
        return "Missing parameters" , 400   
    client = CAKEClient(message_id=message_id, reader_address=reader_address)
    client.handshake()
    #client.disconnect()
    return "Handshake completed" , 200

@app.route('/client/generateKey/' , methods=['GET', 'POST'])
def generateKey():
    reader_address, message_id = getClientArgs(request)
    if reader_address == '' or message_id == '':
        print("Missing parameters")
        return "Missing parameters" , 400
    client = CAKEClient(message_id=message_id, reader_address=reader_address)
    client.generate_key()
    return "Key generated"

@app.route('/client/accessData/' , methods=['GET', 'POST'])
def accessData():
    reader_address, message_id, slice_id = getClientArgs(request)
    if reader_address == '' or message_id == '' or slice_id == '':
        return "Missing parameters" , 400
    client = CAKEClient(message_id=message_id, reader_address=reader_address, slice_id=slice_id)
    client.access_data()
    #client.disconnect()   

    return "Data accessed"

# This is a full request, it does handshake, generate key and access data
@app.route('/client/fullrequest/' , methods=['GET', 'POST'])
def clinet_fullrequest():
    reader_address, message_id, slice_id = getClientArgs(request)
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

##### Request from Data Owner to SDM Server #####

@app.route('/dataowner/handshake/' , methods=['GET', 'POST'])
def handshake():
    data_owner = CAKEDataOwner()
    data_owner.handshake()
    return "Handshake completed"

@app.route('/dataOwner/cipher/', methods=['POST'])
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

@app.route('/dataOwner/fullrequest/', methods=['POST'])
def dataowner_fullrequest():
    handshake()
    cipher()
    return "Full request completed"

@app.route('/certification/', methods=['POST'])
def certification():
    roles = request.form.get('roles', default = '', type = list)
    Certifier.certify(roles)
    return "Certification done"


if __name__ == '__main__':
    app.run(port=8888)
