from web3 import Web3
from decouple import config
import json
import base64

web3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/059e54a94bca48d893f1b2d45470c002"))
compiled_contract_path = 'blockchain/build/contracts/CAKEContract.json'
deployed_contract_address = config('SMART_CONTRACT_CAKE_ETH')


def get_nonce(ETH_address):
    return web3.eth.get_transaction_count(ETH_address)


def send_MessageIPFSLink(dataOwner_address, private_key, message_id, hash_file):
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)
        contract_abi = contract_json['abi']

    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)

    tx = {
        'nonce': get_nonce(dataOwner_address),
        'gasPrice': web3.eth.gas_price,
        'from': dataOwner_address
    }
    message_bytes = hash_file.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    message = contract.functions.setIPFSLink(int(message_id), dataOwner_address, base64_bytes[:32],
                                             base64_bytes[32:]).buildTransaction(tx)
    signed_transaction = web3.eth.account.sign_transaction(message, private_key)
    transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    print(f'tx_hash: {web3.toHex(transaction_hash)}')
    tx_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash, timeout=600)
    # print(tx_receipt)


def retrieve_MessageIPFSLink(message_id):
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)
        contract_abi = contract_json['abi']

    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)

    message = contract.functions.getIPFSLink(int(message_id)).call()
    sender = message[0]
    message_bytes = base64.b64decode(message[1])
    ipfs_link = message_bytes.decode('ascii')
    return ipfs_link, sender


def send_users_attributes(attribute_certifier_address, private_key, process_instance_id, hash_file):
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)
        contract_abi = contract_json['abi']

    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)

    tx = {
        'nonce': get_nonce(attribute_certifier_address),
        'gasPrice': web3.eth.gas_price,
        'from': attribute_certifier_address
    }
    message_bytes = hash_file.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    # in caso aggiungere il sender con msg.sender in Solidity anche qui. Da valutare
    message = contract.functions.setUserAttributes(int(process_instance_id), base64_bytes[:32],
                                                   base64_bytes[32:]).buildTransaction(tx)
    signed_transaction = web3.eth.account.sign_transaction(message, private_key)
    transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    print(f'tx_hash: {web3.toHex(transaction_hash)}')
    tx_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash, timeout=600)
    # print(tx_receipt)


def retrieve_users_attributes(process_instance_id):
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)
        contract_abi = contract_json['abi']

    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)

    message = contract.functions.getUserAttributes(int(process_instance_id)).call()
    message_bytes = base64.b64decode(message)
    message = message_bytes.decode('ascii')
    return message


def send_publicKey(reader_address, private_key, hash_file):
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)
        contract_abi = contract_json['abi']

    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)

    tx = {
        'nonce': get_nonce(reader_address),
        'gasPrice': web3.eth.gas_price,
        'from': reader_address
    }
    message_bytes = hash_file.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    message = contract.functions.setPublicKeys(base64_bytes[:32], base64_bytes[32:]).buildTransaction(tx)
    signed_transaction = web3.eth.account.sign_transaction(message, private_key)
    transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    print(f'tx_hash: {web3.toHex(transaction_hash)}')
    tx_receipt = web3.eth.wait_for_transaction_receipt(transaction_hash, timeout=600)
    # print(tx_receipt)


def retrieve_publicKey(reader_address):
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)
        contract_abi = contract_json['abi']

    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)

    message = contract.functions.getPublicKeys(reader_address).call()
    message_bytes = base64.b64decode(message)
    message1 = message_bytes.decode('ascii')
    return message1
