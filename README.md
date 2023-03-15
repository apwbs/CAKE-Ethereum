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

### Database creation

When these passages are completed, the databases for all the actors involved in the process need to be created. 
Move in the 'files' folder and create/copy the folders you need. To create a database run `sqlite3 name_of_the_database.db`.
When inside that database run `.read database.sql` to instantiate the database with the right tables.

### Key pairs generation

Once all these preliminary steps are completed, you can start running the actual code. An '.env' file must be created in order
to store all the necessary values of the constants. This file must be put in the 'architecture' or 'implementation' folder.

The first thing to do is provide a pair of private and public keys to the readers. Open a container terminal and move in the 
architecture or implementation folder and run `python3 rsa_public_keys.py`. In the file, specify the actors you want 
to give a key pair.

### Attributes assignment

Next, open the attribute certifier file and write down the attributes that you intend to give to the actors of the system.
Then run `python3 attribute_certifier.py` to store those values both in the certifier db and on chain. Copy the resulting
process_instance_id number in the .env file.

### Message ciphering and delivering

To cipher a message and store it on the blockchain, open the 'data_owner.py' file. Firstly, run 'generate_pp_pk()' to 
instantiate the data owner, then modify the file 'data.json' with the data you want to cipher. Then, run the main() function, but
remember to modify the access policy and the entries that you need to cipher with a particular policy: 
lines highlighted with `###LINES###` in the file.

### Key requests

To obtain a key from the authorities there are two ways. The first one (the one in the main) is to send a request using an SLL client-server connection,
the second option is to send a key request on chain and get an IPFS link on chain to open. To send a request via SSL, open
the 'client.py' file, specify the constants like 'reader_address', 'gid' etc. and then run `python3 server_authority*.py`. 
Then, run `python3 client.py` to firstly start the handshake function and then to ask for a key. Send these two messages in different
moments just commenting the action that you do not want to perform. 

### Message reading

Once you have obtained a part of a key from all the authorities,
open the 'reader.py' file and run the generate_public_parameters() function. Then put the right values in the 'message_id' and
'slice_id' constants and run the main() function to read the message.
