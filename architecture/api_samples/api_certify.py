import requests
import ssl
server_cert = '../Keys/api.crt'
client_cert = '../Keys/client.crt'
client_key = '../Keys/client.key'


context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
context.load_cert_chain(certfile=client_cert, keyfile=client_key)

actors = ['MANUFACTURER', 'SUPPLIER1', 'SUPPLIER2']
roles = {'MANUFACTURER': ['MANUFACTURER'],
    'SUPPLIER1': ['SUPPLIER', 'ELECTRONICS'],
    'SUPPLIER2': ['SUPPLIER', 'MECHANICS']}

input = {'actors': actors, 'roles': roles}

response = requests.post('https://127.0.0.1:8080/certification/',
    json = input, cert=(client_cert, client_key), verify=server_cert)

print(response.text)

name = 'PROCESS_ID'  
with open('.env', 'r', encoding='utf-8') as file:
    data = file.readlines()
edited = False
for line in data:
    if line.startswith(name):
        data.remove(line)
        break
line = name + "=" + response.text + "\n"
data.append(line)

with open('.env', 'w', encoding='utf-8') as file:
    file.writelines(data)