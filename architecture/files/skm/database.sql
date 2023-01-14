CREATE TABLE rsa_public_key (
    reader_address TEXT,
    ipfs_file_link_hash TEXT,
    publicKey TEXT,
    primary key (reader_address)
);

CREATE TABLE rsa_private_key (
    reader_address TEXT,
    privateKey TEXT,
    primary key (reader_address)
);

CREATE TABLE generated_key_reader (
    process_instance_id TEXT,
    message_id TEXT,
    ipfs_message_link TEXT,
    reader_address TEXT,
    secret_key TEXT,
    primary key (process_instance_id, message_id, reader_address)
);

CREATE TABLE handshake_numbers ( 
    process_instance TEXT,
    message_id TEXT,
    reader_address TEXT,
    handshake_number TEXT,
    primary key (process_instance, message_id, reader_address)
);

CREATE TABLE readers_public_keys ( 
    reader_address TEXT,
    ipfs_file_link_hash TEXT,
    public_key TEXT,
    primary key (reader_address)
);
