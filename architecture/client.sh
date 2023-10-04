message_id='4361553153723282895'
reader_address='0x0ab13ca71f8c41A506029ea1DB2747513273a9dF'
slice_id='678099069573181131'

python3 client.py --handshake --message_id $message_id --reader_address $reader_address
python3 client.py -gs --message_id $message_id --reader_address $reader_address 
python3 client.py -ad --message_id $message_id --reader_address $reader_address --slice_id $slice_id

#slice id: 6678072391299123667
#slice id: 13635621019063986383
#slice id: 10450506680882014878
#message id: 6780287944816327166