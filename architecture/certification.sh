# Read public key of manufacter and suppliers
set -e
python3 reader_public_key.py --reader 'MANUFACTURER'
echo "✅ Readed public key of MANUFACTURER"
python3 reader_public_key.py --reader 'SUPPLIER1'
echo "✅ Readed public key of SUPPLIER1"
python3 reader_public_key.py --reader 'SUPPLIER2'
echo "✅ Readed public key of SUPPLIER2"

python3 skm_public_key.py
echo "✅ Readed public key of skm"

python3 attribute_certifier.py 
echo "✅ Attribute certifier done"