message_id='6780287944816327166'
reader_address='0x22b9d3F9b828B1ec90B2b331d06C42842846E8D6'
slice_id='6678072391299123667'

python3 client.py --handshake --message_id $message_id --reader_address $reader_address
python3 client.py -gs --message_id $message_id --reader_address $reader_address 
python3 client.py -ad --message_id $message_id --reader_address $reader_address --slice_id $slice_id

#slice id: 6678072391299123667
#slice id: 13635621019063986383
#slice id: 10450506680882014878
#message id: 6780287944816327166