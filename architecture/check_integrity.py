import hashlib
import sqlite3
from decouple import config
import ipfshttpclient
import json

api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

process_instance_id = config('PROCESS_INSTANCE_ID')

# Connection to SQLite3 reader database
connection = sqlite3.connect('files/reader/reader.db')
x = connection.cursor()


def check_plaintext(process_instance_id, message_id, reader_address, slice_id):
    x.execute("SELECT * FROM decription_keys WHERE process_instance=? AND message_id=? AND reader_address=?",
              (str(process_instance_id), str(message_id), reader_address))
    result = x.fetchall()
    message_ipfs_link = result[0][3]
    getfile = api.cat(message_ipfs_link)
    j2 = json.loads(getfile)
    body = json.loads(j2['body'])

    if len(body) == 1:
        message_hex = body[0][0][0]
        #print(message_hex)

        x.execute("SELECT * FROM plaintext WHERE process_instance=? AND message_id=? AND slice_id=?",
        (str(process_instance_id), str(message_id), str(0)))
        result = x.fetchall()
        plaintext = result[0][4]
        salt = result[0][5]

        combined = plaintext + salt
        combined = combined.encode()
        combined_hashed = hashlib.sha256(combined)
        hex_dig = combined_hashed.hexdigest()
        if hex_dig == message_hex:
            print("Message integrity is OK")
        else:
            print("Message integrity is NOT OK")
        #print(hex_dig == message_hex)

    else:
        for i, elem in enumerate(body):
            slice_number = body[i][0][0][0]
            if slice_number == int(slice_id):
                message_hex = body[i][0][0][1]

                x.execute("SELECT * FROM plaintext WHERE process_instance=? AND message_id=? AND slice_id=?",
                    (str(process_instance_id), str(message_id), str(slice_id)))
                result = x.fetchall()
                plaintext = result[0][4]
                salt = result[0][5]

                combined = plaintext + salt
                combined = combined.encode()
                combined_hashed = hashlib.sha256(combined)
                hex_dig = combined_hashed.hexdigest()

                #print(hex_dig == message_hex)
                if hex_dig == message_hex:
                    print("Message integrity is OK")
                else:
                    print("Message integrity is NOT OK")


if __name__ == "__main__":
    message_id = 16969972429370955301
    slice_id = 6877338788473590293
    reader_address = '0x826cBc23f60f256D9CCB9286b25409edC2b91332'
    check_plaintext(process_instance_id, message_id, reader_address, slice_id)
