from kobukidriver import Kobuki
import socket

kobuki_instance = Kobuki()

def move(left_velocity, right_velocity):
    botspeed = (left_velocity + right_velocity) / 2
    
    if left_velocity == right_velocity:
        botradius = 0
    else:
        botradius = (230 * (left_velocity + right_velocity)) / (2 * (right_velocity - left_velocity))

    cs = 0
    barr = bytearray([170, 85, 6, 1, 4])
    barr += int(botspeed).to_bytes(2, byteorder='little', signed=True)
    barr += int(botradius).to_bytes(2, byteorder='little', signed=True)
    
    for i in range(2, len(barr) - 1):
        cs = cs ^ barr[i]
    
    barr += cs.to_bytes(1, byteorder='big')
    Kobuki.seri.write(barr)

def handle_connection(client_socket):
    while True:
        command = client_socket.recv(1024).decode('utf-8').strip()
        print(f'Received command: "{command}"')
        if not command:
            continue
        
        if command == 'U':
            move(100, 100)
        elif command == 'D':
            move(-100, -100)
        elif command == 'L':
            move(0, 200)
        elif command == 'R':
            move(200, 0)
        elif command == 'S':
            move(0, 0)
        else:
            response = 'Invalid command.'
            client_socket.sendall(response.encode('utf-8'))
            continue
        
        response = f'Command "{command}" executed.'
        client_socket.sendall(response.encode('utf-8'))

server_ip = '0.0.0.0'
server_port = 8000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((server_ip, server_port))
server.listen(1)
print(f'Listening on {server_ip}:{server_port}')

while True:
    client_sock, address = server.accept()
    print(f'Accepted connection from {address}')
    handle_connection(client_sock)
