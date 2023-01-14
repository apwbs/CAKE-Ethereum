CREATE TABLE decription_keys ( 
    process_instance TEXT,
    message_id TEXT,
    reader_address TEXT,
    ipfs_message_link TEXT,
    decription_key TEXT,
    primary key (process_instance, message_id, reader_address)
);

CREATE TABLE plaintext ( 
    process_instance TEXT,
    message_id TEXT,
    slice_id TEXT,
    reader_address TEXT,
    plaintext TEXT,
    salt TEXT,
    primary key (process_instance, message_id, slice_id, reader_address)
);

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
    message_id TEXT,
    reader_address TEXT,
    number_to_sign TEXT,
    primary key (process_instance, message_id, reader_address)
);
