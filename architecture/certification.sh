# Read public key of manufacter and suppliers
python3 reader_public_key.py --reader 'MANUFACTER'
echo "Readed public key of manufacter"
python3 reader_public_key.py --reader 'SUPPLIER1'
echo "Readed public key of supplier1"
python3 reader_public_key.py --reader 'SUPPLIER2'
echo "Readed public key of supplier2"

python3 skm_public_key.py
echo "Readed public key of skm"


python3 attribute_certifier.py 
echo "Attribute certifier done"
