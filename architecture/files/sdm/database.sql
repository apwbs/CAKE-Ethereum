CREATE TABLE handshake_numbers ( 
    process_instance TEXT,
    reader_address TEXT,
    handshake_number TEXT,
    primary key (process_instance, reader_address)
);

CREATE TABLE readers_public_keys ( 
    reader_address TEXT,
    ipfs_file_link_hash TEXT,
    public_key TEXT,
    primary key (reader_address)
);
