CREATE TABLE rsa_public_key (
    reader_address TEXT,
    ipfs_file_link_hash TEXT,
    publicKey_n TEXT,
    publicKey_e TEXT,
    primary key (reader_address)
);

CREATE TABLE rsa_private_key (
    reader_address TEXT,
    privateKey_n TEXT,
    privateKey_d TEXT,
    primary key (reader_address)
);

CREATE TABLE handshake_number ( 
    process_instance TEXT,
    sender_address TEXT,
    number_to_sign TEXT,
    primary key (process_instance, sender_address)
);

CREATE TABLE messages ( 
    process_instance TEXT,
    message_id TEXT,
    sender_address TEXT,
    primary key (process_instance, message_id)
);
