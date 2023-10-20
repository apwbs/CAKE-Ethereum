# Read public key of manufacter and suppliers
set -e

# READ PUBLIC KEY OF MANUFACTURER AND SUPPLIERS
python3 certifier.py -o 0 --reader 'MANUFACTURER'
echo "✅ Read public key of MANUFACTURER"
python3  certifier.py -o 0  --reader 'SUPPLIER1'
echo "✅ Read public key of SUPPLIER1"
python3  certifier.py -o 0  --reader 'SUPPLIER2'
echo "✅ Read public key of SUPPLIER2"

 # READ PUBLIC KEY OF SKM
python3  certifier.py -o 1
echo "✅ Read public key of skm"

# CERTIFY ATTRIBUTES
python3  certifier.py -o 2
echo "✅ Attribute certifier done"