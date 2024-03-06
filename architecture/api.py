import sqlite3
from flask import Flask, request
import json
from decouple import config
from hashlib import sha512
from certifier import Certifier
from client import CAKEClient
from data_owner import CAKEDataOwner
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)


import ssl
server_cert = 'Keys/api.crt'
server_key = 'Keys/api.key'
client_certs = 'Keys/client.crt'

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile=server_cert, keyfile=server_key) 
context.load_verify_locations(cafile=client_certs)

def __get_client_args__(request):
    """ Read the arguments from the client request

    This function is used to get the arguments from the client request
    and return them in the correct format to be used by the CAKEClient

    Args:
        request: the request from the client
    
    Returns:
        reader_address: the address of the reader
        message_id: the id of the message
        slice_id: the id of the slice
        process_id: the id of the process (process_instance_id)
    """
    process_id = request.json.get('process_id')
    reader_address = request.json.get('reader_address')
    message_id = request.json.get('message_id')
    slice_id = request.json.get('slice_id')
    '''
    print("Reader_address is: " + reader_address)
    print("Message_id is: " + message_id)
    if slice_id is not None:
        print("Slice_id is: " + slice_id)
    print("Process_id is: " + str(process_id))
    '''
    return reader_address, message_id, slice_id, process_id



@app.route('/')
def go_home():
    """ A simple request to the API welcome message

    This function is used to test if the API is working correctly
    during the development phase

    Returns:
        A welcome message
    """
    return 'Welcome to the CAKE API'

#### Request from client to SKM Server ####

@app.route('/client/handshake/' , methods=['GET', 'POST'])
def client_handshake():
    """ Request to the SKM Server to handshaking

    This function is used to send a request to the SKM Server
    to make an handshake with the reader
 
    Args:
        reader_address: the address of the reader
        message_id: the id of the message
        process_id: the id of the process (process_instance_id)

    Returns:
        The status of the request, 200 if the handshake is completed
    """
    reader_address, message_id, _, process_id = __get_client_args__(request)
    if reader_address == '' or message_id == '':
        return "Missing parameters" , 400   
    client = CAKEClient(message_id=message_id, reader_address=reader_address, process_instance_id=process_id)
    client.handshake()
    return "Handshake completed" , 200


@app.route('/client/generateKey/' , methods=['GET', 'POST'])
def generateKey():
    """ Request to the SKM Server to generate a key

    This function is used to send a request to the SKM Server
    to generate a key for the reader.
    The key is generated only if the handshake is completed.
    
    Args:
        reader_address: the address of the reader
        message_id: the id of the message
        process_id: the id of the process (process_instance_id)
        
    Returns:
        The status of the request, 200 if the key is generated
    """
    reader_address, message_id, _, process_id = __get_client_args__(request)
    if reader_address == '' or message_id == '':
        print("Missing parameters")
        return "Missing parameters" , 400
    client = CAKEClient(message_id=message_id, reader_address=reader_address, process_instance_id = process_id)
    client.generate_key()
    return "Key generated", 200


@app.route('/client/accessData/' , methods=['GET', 'POST'])
def accessData():
    """ Request to the SKM Server to access data

    This function is used to send a request to the SKM Server
    to access data from the reader.
    The data is accessed only if the reader already has the key.

    Args:
        reader_address: the address of the reader
        message_id: the id of the message
        slice_id: the id of the slice
        process_id: the id of the process (process_instance_id)    

    Returns: 
        The status of the request, 200 if the data is accessed
    """
    reader_address, message_id, slice_id, process_id = __get_client_args__(request)
    if reader_address == '' or message_id == '':
        return "Missing parameters" , 400
    client = CAKEClient(message_id=message_id, reader_address=reader_address, slice_id=slice_id, process_instance_id= process_id)
    client.access_data()
    #client.disconnect()   

    return "Data accessed" , 200


##### Request from Data Owner to SDM Server #####

@app.route('/dataOwner/handshake/' , methods=['POST'])
def data_owner_handshake():
    """ Request to the SDM Server to handshaking

    This function is used to send a request to the SDM Server
    to make an handshake with the MANUFACTURER

    Args:
        process_id: the id of the process (process_instance_id)
    
    Returns:
        The status of the request, 200 if the handshake is completed
    """
    data_owner = CAKEDataOwner(process_instance_id=request.json.get('process_id'))
    data_owner.handshake()
    return "Handshake completed", 200


@app.route('/dataOwner/cipher/', methods=['POST'])
def cipher():
    """ Request to the SDM Server to cipher the message from the Manufacturer

    This function is used to send a request to the SDM Server
    to cipher the message from the Manufacturer, setting the policy
    of the decryption.

    Args:
        message: the message to cipher, it's a string read from a json file
        entries:  a list of list of label of the message that has the same policy
        policy: a list containing for each group of label the process_id associated
            and the policy, defining which actors can access the data

    Returns:
        The status of the request, 200 if the cipher is completed
    """
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
    data_owner = CAKEDataOwner(process_instance_id=request.json.get('process_id'))
    data_owner.cipher_data(message, entries_string, policy_string)
    return "Cipher completed", 200

@app.route('/certification/', methods=['POST'])
def certification():
    """ Request to to certify the actors
    
    This function is used to send a request read the actors' public keys,
    the skm's public key and to certify the actors involved in the process

    Args:
        actors: the list of actors involved in the process
        roles: a dictionary that contains for each actor the list of roles associated
    
    Returns:
        The process instance id of the certification process and
        the status of the request, 200 if the certification is completed
    """

    actors = request.json.get('actors')
    roles = request.json.get('roles')
    process_instance_id = Certifier.certify(actors, roles)
    return str(process_instance_id), 200

@app.route('/certification/readpublickey/', methods=['POST'])
def read_public_key():
    """ Read the public keys of the actors

    This function is used to read the public keys of the actors
    that are involved in the process
    
    Args:
        actors: the list of actors involved in the process
        roles: a dictionary that contains for each actor the list of roles associated

    Returns:
        The status of the request, 200 if the keys are read correctly
    """
    actors = request.json.get('actors')
    #roles = request.json.get('roles')
    Certifier.read_public_key(actors)
    return "Public keys read", 200

@app.route('/certification/skmpublickey/', methods=['GET', 'POST'])
def skm_public_key():
    """ Read the public key of the SKM

    This function is used to read the public key of the SKM

    Returns:
        The status of the request, 200 if the keys are read correctly
    """
    Certifier.skm_public_key()
    return "SKM public key read", 200


@app.route('/certification/attributecertification/', methods=['POST'])
def attribute_certification():
    """ Certificate the actors

    This function is used to certificate the actors
    that are involved in the process
    
    Args:
        actors: the list of actors involved in the process
        roles: a dictionary that contains for each actor the list of roles associated
        
    Returns:
        The process instance id of the certification process and
        the status of the request, 200 if the certification is completed
    """
    roles = request.json.get('roles')
    process_instance_id =  Certifier.attribute_certification(roles)

    return str(process_instance_id), 200

@app.route('/test/', methods=['GET', 'POST'])
def test():
    """ Test function

    This function is used to test the server during the development phase.

    Returns:
        A string that says "Test done"
    """
    import os
    os.system("ls")
    return "Test done"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port="8080", ssl_context=context)
