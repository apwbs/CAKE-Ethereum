# Fine-grained Data Access Control for Collaborative Process Execution on Blockchain

This repository contains the latest version of the CAKE approach presented in the paper "[Fine-grained Data Access Control for
Collaborative Process Execution on Blockchain](https://arxiv.org/abs/2207.08484)" (DOI: [10.1007/978-3-031-16168-1_4](https://doi.org/10.1007/978-3-031-16168-1_4); slides are available on [SlideShare](https://www.slideshare.net/EdoardoMarangone/finegrained-data-access-control-for-collaborative-process-execution-on-blockchain-253133788)). For the **Algorand**-based implementation, please check out [github.com/apwbs/CAKE-Algorand](https://github.com/apwbs/CAKE-Algorand/)!

For the impatient: in this [Docker Hub repository](https://hub.docker.com/repository/docker/apwbs/cake/general) you can find readily available Docker Images to play with the Ethereum and Algorand implementations of the CAKE approach!


## Guide

### Requirements
There are two ways to run the system. The first one is to download the corresponding Docker Image for the Ethereum implementation stored at the [Docker Hub](https://hub.docker.com/repository/docker/apwbs/cake/general).

Otherwise, it is (strongly) recommended to install Docker and create a new image running Ubuntu 18.04 and then start one
or more containers from that image. To do this, firstly use the DockerFile running `docker build -t image_name PATH_TO_THE_DOCKERFILE/DockerFiles/`
to create a docker image. Then run `docker run -it -v PATH_TO_CAKE-EthereumFOLDER/CAKE-Ethereum/:/CAKE-Ethereum image_name`
to create a container starting from the image created in the previous step. To run the first instance of a container run
`docker start container_name`, then run `docker attach container_name`. To run other independent instances of the same container run
`docker exec -it container_name bin/bash`. Running other instances (from the second on) of the same container with 
`docker start` and `docker attach` will not make them independent. Every command in one instance will be applied also in the
other instances. Using `docker exec` you can open as many independent containers as you like.

The following libraries must be installed inside the container: python3.6, [charm](https://github.com/JHUISI/charm), 
[rsa](https://pypi.org/project/rsa/), [web3](https://web3py.readthedocs.io/en/stable/quickstart.html) (python-version), 
[python-decouple](https://pypi.org/project/python-decouple/), [truffle](https://trufflesuite.com/docs/truffle/how-to/install/),
[nodejs and npm](https://nodejs.dev/en/) (recommended node version 16.19.0, npm version 8.19.3), 
sqlite3 (python3 -m pip install sqlite3), ipfs (for local node) run:
1. python3.6 -m pip install ipfshttpclient
2. wget https://dist.ipfs.io/go-ipfs/v0.7.0/go-ipfs_v0.7.0_linux-amd64.tar.gz
3. tar -xvzf go-ipfs_v0.7.0_linux-amd64.tar.gz
4. cd go-ipfs
5. sudo bash install.sh
6. ipfs init
7. ipfs daemon (in another terminal window).

If the installation of 'charm' fails, try running these commands: 
1. sudo apt-get install libgmp3-dev libssl-dev
2. wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz
3. tar xvf pbc-0.5.14.tar.gz
4. cd pbc-0.5.14
5. ("sudo apt-get install flex bison" may be necessary, depending on what you already have on your system)
6. ./configure
7. make
8. sudo make install
9. pip install sovrin

If the installation fails again, try these commands too:
1. sudo apt-get git
2. sudo apt-get install m4
3. git clone https://github.com/JHUISI/charm.git
4. cd charm
5. sudo ./configure.sh
6. sudo make
7. sudo make install
8. sudo ldconfig
9. sudo -H pip install sovrin

In order to check if 'charm' is successfully installed, try run `python3` (inside the container) and then `import charm`. 
If there are no errors displayed, the package is correctly installed.

### Contracts deployment

The first thing to do is to deploy the smart contract on the blockchain. 
To do that, create a [Metamask](https://metamask.io/) wallet and fund an account with some Eth in the Goerli testnet 
with a [Goerli faucet](https://goerlifaucet.com/). Then create an account on [Infura](https://www.infura.io/) 
and obtain a key for the Goerli testnet.

Enter the 'blockchain' folder and create a '.env' file. Put two constants in there:
1. 'MNEMONIC'=the secret words of the Metamask wallet
2. 'PROJECT_ID'=the project ID obtained from Infura

After doing this, open a terminal and run `truffle init`. Copy the folders 'contracts' and 'migrations' from the repo
and also the 'truffle-config.js' file. Then run `truffle migrate --network goerli` and wait for the deployment of the 
contract on chain.

## Inizializzation

When these passages are completed, the databases for all the actors involved in the process need to be created, and then you have to read the keys of the addresses involved and certify on the blockchain the attributes assignment.
Once all these preliminary steps are completed, you can start running the actual code. An '.env' file must be created in order to store all the necessary values of the constants. This file must be put in the 'architecture' or 'implementation' folder. The first thing to do is provide a pair of private and public keys to the readers.
To specify the actors you want to give a pair, you have to open 'certification.sh' and use this two lined for each actors involved on the top of the shell script:
```python
python3 reader_public_key.py --reader 'NAME_OF_THE_ACTOR'
echo "✅ Readed public key of NAME_OF_THE_ACTOR"
```
To modify the attribute assignment it is necessary to open the 'attribute_certifier.py' file, import the public addresses of the actors involved, and modify the assignment of the `dict_users` variable.
```python

an_actor_address = config('NAME_OF_THE_ACTOR')
manufacturer_address = config('ADDRESS_MANUFACTURER')
supplier1_address = config('ADDRESS_SUPPLIER1')
supplier2_address = config('ADDRESS_SUPPLIER2')


dict_users = {

    an_actor_address = [str(process_instance_id), 'AN_ATTRIBUTE', 'ANOTHER_ATTRIBUTE'],

    manufacturer_address: [str(process_instance_id), 'MANUFACTURER'],

    supplier1_address: [str(process_instance_id), 'SUPPLIER', 'ELECTRONICS'],

    supplier2_address: [str(process_instance_id), 'SUPPLIER', 'MECHANICS']
}
```
Now, move in the 'architecture' folder with your terminal, and run `sh initiaize.sh`.
Alternatively, you can perform database initialization or reset and other steps separately by running respectively `sh rest.sh` and `sh certification.sh`.

### Message ciphering and delivering

Firstly, run the SDM server with `python3 sdm_server.py`.
The message to be encrypted must be saved in the path 'CAKE-Algorand/architecture/file/data.json'. The following example is an instance of a cipherable message.

```json
{
    "ID": "SGML",
    "SortAs": "LMGS",
    "GlossTerm": "Standard Generalized Markup Language",
    "Acronym": "GSML",
    "Abbrev": "ISO 8879:1986",
    "Specs": "928162",
    "Dates": "NOW"
}
```

Then, modify the access policy and the entries that you need to cipher with a particular policy: lines highlighted with `###LINES###`.

```python
entries = [['ID', 'SortAs', 'GlossTerm'], ['Acronym', 'Abbrev'], ['Specs', 'Dates']] 
```
```python
policy = ['1358911044885481786 and (MANUFACTURER or SUPPLIER)',
          '1358911044885481786 and (MANUFACTURER or (SUPPLIER and ELECTRONICS))',
          '1358911044885481786 and (MANUFACTURER or (SUPPLIER and MECHANICS))']
```

Now run with your terminal `sh data_owner.sh`. 

The run `sh data_owner.py` to make an handshake an a ciphering request. It's also possible to split these two action running `python3 data_owner.py -hs` to handshake and `python3 data_owner.py -c` to cipher.
At this point,the SDM Server will print the 'slice_id' and 'message_id' values, these information will be used to key requesting.
```
[STARTING] server is starting...
[LISTENING] Server is listening on 172.17.0.2
[NEW CONNECTION] ('172.17.0.2', 58680) connected.
[ACTIVE CONNECTIONS] 1
Handshake successful
slice id: 11405747102899531556
slice id: 3622467048620169296
slice id: 8386550832079592906
message id: 6389222717092303342
ipfs hash: QmXoat6pFTVWqahzXvCQTgQ37y7GjUjCBikqFe2cYGUyCi
```

To send a request via SSL, open the 'client.sh' file, specify the constants like 'reader_address', 'message_id' and 'slice_id, then run ```python3 skm_server.py```. Then, run ```sh client.py```. This command make an handshake between the reader and the skm_server, then it request a key generation and in the end it use to access to the data.
If the policy allows it, you will read the data you requested on the terminal.
If the address used has already performed a handshake and a key generation request, it will be necessary to use ```sh client.py``` setting the variables in the same way.

## API Guide
CAKE also has an API to manage its interaction, this section describes its structure and use.

### Requirement
To use the api you need to install flask, open the terminal and run `pip install flask`.
To interract with the API you need to user requests library. So your python script have to import it.  
```python
    import requests 

    #YOUR CODE
```
### Initizialization
The database resetting and the deployment of the contract cannot be done using the API, you have to open your terminal and run in 'CAKE-Algorand/architecture' `sh resetDB.sh` and `sh deploy.sh`. At this point is possible to lunch the API, running `python3 API/api.py`.

The terminal will show the base path to use to interract the API (in the following example it is 'http://127.0.0.1:8888/')

```
root@7e473ad21d74:/CAKE-Algorand/architecture# python3 API/api.py 
 * Serving Flask app 'api' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:8888/ (Press CTRL+C to quit)
```

At this point the API is running, an it's possible interract with it.
To test if api is correctly working you can run this script anche check if the request status is 200.

```python
    import requests

    response = requests.get('http://127.0.0.1:8888/')
```

### Read keys and attribute certification

Using the API it is possible to read the keys of the skm server actors, and assign the desired roles to the actors involved.
It is necessary to define a list with the names of the actors, remember that the name must be the same used inside the env when the address and public key of the actor are specified.
In addition to a list of strings with the actors involved, a dictionary must be defined that associates the roles assigned to the actors involved. Each actor can have multiple roles, and each role can be assigned multiple times.
These two data structures will have to be inserted in a dictionary, with 'actors' and 'roles' as keys respectively, and given as input as in the following example during the request to the api server.

```python
    import requests 

    actors = ['MANUFACTURER', 'SUPPLIER1', 'SUPPLIER2']
    roles = {'MANUFACTURER': ['MANUFACTURER'],
        'SUPPLIER1': ['SUPPLIER', 'ELECTRONICS'],
        'SUPPLIER2': ['SUPPLIER', 'MECHANICS']}

    input = {'actors': actors, 'roles': roles}

    response = requests.post('http://127.0.0.1:8888/certification', json = input)

```
This method return as response the process, to access to this value you can use `response.text`. This value has to be stored on the .env.
At the end of this run, you have to lunch the SDM and SKM servers using `python3 sdm_server.py` and `python3 skm_server.py`.

This request can be splitted in the following three differents request to the api server, like in the following three subsections. For a correct functioning it is necessary to carry out these operations in the proposed order.

#### Read public key

Using the method in the example is possible to ask to server to read the keys of the actors stored in the '.env' files.
It is necessary to construct a list with the names of the actors, and then a insert the list into a dictionary with the key 'actors', like to what was described previously. This dictionary will be input like in the example.
```python
    import requests 

    actors = ['MANUFACTURER', 'SUPPLIER1', 'SUPPLIER2']

    input = {'actors': actors}

    response = requests.post('http://127.0.0.1:8888/certification/readpublickey',
        json = input)

```

#### Read SKM's key

Using the method in the example is possible to ask to server to read the key of the SKM server stored in the '.env'.
This method doen't need any input.

```python
    import requests 

    response = requests.post('http://127.0.0.1:8888/certification/skmpublickey')

```

#### Attribute certification

This method allows you to certify on the blockchain the roles assigned to the actors, whose key has previously been read. A dictionary must be defined that associates the roles assigned to the actors involved. Each actor can have multiple roles, and each role can be assigned multiple times.
This dictonary will have to be inserted in a dictionary, with 'roles' as key, and given as input as in the following example during the request to the api server.

```python
    import requests 

    roles = {'MANUFACTURER': ['MANUFACTURER'],
        'SUPPLIER1': ['SUPPLIER', 'ELECTRONICS'],
         'SUPPLIER2': ['SUPPLIER', 'MECHANICS']}

    input = {'roles': roles}

    response = requests.post('http://127.0.0.1:8888/certification/attributecertification',
        json = input)

```

This method return as response the process, to access to this value you can use `response.text`. This value has to be stored on the .env.
At the end of this run, you have to lunch the SDM and SKM servers using `python3 sdm_server.py` and `python3 skm_server.py`.

### Interraction with SDM 

The python script described in this section allows to send message to the SDM server using the API, allowing to cipher a message.
The following example is an instance of a cipherable message

```json
{
    "ID": "SGML",
    "SortAs": "LMGS",
    "GlossTerm": "Standard Generalized Markup Language",
    "Acronym": "GSML",
    "Abbrev": "ISO 8879:1986",
    "Specs": "928162",
    "Dates": "NOW"
}
```

#### Handshake
To make an handshake it's necessary to build a dictionary with the process instance id corrisponding to the key 'process_id', and to send a post request to 'dataOwner/handshake'.
Note that the process instance id is the only value that will be input from here on using as `int`.

```python
    import requests 

    process_instance_id = 1234567890 #Process id generated after the attribute certification
    
    input = {'process_id' : process_instance_id}

    response = requests.post('http://127.0.0.1:8888/dataOwner/handshake',
        json = input)
```

#### Cipher
If the handshaking operation is completed correctly, you can proceed with the encryption of the message.
You have to build a dictionary, with the described information associated with the following keys:
- `'processe_id'` : the process_id showed at the end of attribute certification
- `'entries'` : a list in which each element is a group of entries of the message to be encrypted which will be associated with the same privacy. These groups are represented by a list of strings, where the strings are associated with the keys of the json file.
- `'policy'` : a string list containing the process_id and the specific policy for the group of entries with the same index in the 'entries' vector. The correct formatting can be seen in the next code example.
- `'message'` : a string generated from reading the json file containg the messago to cipher

```python
    import requests 

    process_instance_id = 1234567890 #Process id generated after the attribute certification
    
    entries = [['ID', 'SortAs', 'GlossTerm'],
        ['Acronym', 'Abbrev'],
        ['Specs', 'Dates', 'GlossTerm']]

    policy = [process_instance_id + ' and (MANUFACTURER or SUPPLIER)',
          process_instance_id + ' and (MANUFACTURER or (SUPPLIER and ELECTRONICS))',
          process_instance_id + ' and (MANUFACTURER or (SUPPLIER and MECHANICS))']

    g = open('your/data.json')

    message_to_send = g.read()

    input = {'process_id': process_instance_id,
        'entries': entries,
        'policy' : policy, 
        'message': message_to_send}

    response = requests.post('http://127.0.0.1:8888/dataOwner/cipher',
        json = input)
```
At the end of this operation it is important to take note of the slice_id and message_id values generated and displayed on the terminal where the sdm server runs.

```
[ACTIVE CONNECTIONS] 1
Handshake successful
slice id: 5375500895703771247
slice id: 17604598720062938551
slice id: 10338915769088273764
message id: 13846106420650213324
```

The slice_id values represent the groups of labels defined in entries, while the message_id is an identifier of the encrypted message.

### Interraction with SKM
This section describes the methods that allow you to interact with the SKM Server, allowing you to make a handshake with the actors, generate a key and have access to encrypted messages.
#### Handshake

Also this time a handshaking is necessary, therefore it is necessary to indicate the address of the reader inside the dictionary given in input using the key 'reader address'. It is also necessary to enter the ID of the message to be decrypted using 'message_id' as key, and the process_id as in the previous step.

```python
    import requests 

    process_instance_id = 1234567890 #Process id generated after the attribute certification
    message_id = '13846106420650213324' 
    reader_address = 'N2C374IRX7HEX2YEQWJBTRSVRHRUV4ZSF76S54WV4COTHRUNYRCI47R3WU'

    input = {'process_id' : process_instance_id,
        'message_id': message_id,
        'reader_address' : reader_address}

    response = requests.post('http://127.0.0.1:8888/client/handshake',
        json = input)

```

#### Generate Keys

At this point using the same dictionary of the previous step it is possible to generate a key for the reader.

```python
    import requests 

    process_instance_id = 1234567890 #Process id generated after the attribute certification
    message_id = '456'
    reader_address = 'N2C374IRX7HEX2YEQWJBTRSVRHRUV4ZSF76S54WV4COTHRUNYRCI47R3WU'

    input = {'process_id' : process_instance_id,
        'message_id': message_id,
        'reader_address' : reader_address}

    response = requests.post('http://127.0.0.1:8888/client/generateKey',
        json = input)

```

#### Access Data

By adding the value of the slice id corresponding to the portion of the message to be decrypted to the previously defined dictionary, it is finally possible to access it.

```python
    import requests 

    process_instance_id = 1234567890 #Process id generated after the attribute certification
    slice_id = '123'
    message_id = '456'
    reader_address = 'N2C374IRX7HEX2YEQWJBTRSVRHRUV4ZSF76S54WV4COTHRUNYRCI47R3WU'

    input = {'process_id' : process_instance_id,
        'slice_id' : slice_id,
        'message_id': message_id,
        'reader_address' : reader_address}

    response = requests.post('http://127.0.0.1:8888/client/accessData',
        json = input)

```

At this point it will be possible for the reader to make access requests for any slice_id of the message without having to carry out the previous two steps.