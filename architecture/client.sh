message_id='15839363558658261024'
reader_address='0x81215eEC040673dB5131f40184477091747ea4A8'
slice_id='15343280084724660903'

python3 client.py --handshake --message_id $message_id --reader_address $reader_address
python3 client.py -gs --message_id $message_id --reader_address $reader_address 
python3 client.py -ad --message_id $message_id --reader_address $reader_address --slice_id $slice_id

#slice id: 15343280084724660903
#slice id: 1293068278316455013
#slice id: 9899746035376444931
#message id: 15839363558658261024