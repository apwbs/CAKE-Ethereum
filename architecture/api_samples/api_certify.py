import requests 

actors = ['MANUFACTURER', 'SUPPLIER1', 'SUPPLIER2']
roles = {'MANUFACTURER': ['MANUFACTURER'],
    'SUPPLIER1': ['SUPPLIER', 'ELECTRONICS'],
    'SUPPLIER2': ['SUPPLIER', 'MECHANICS']}

input = {'actors': actors, 'roles': roles}

response = requests.post('http://127.0.0.1:8888/certification/',
    json = input)

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