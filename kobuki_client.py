import socket

server_ip = 'localhost'
server_port = 8000

def send_command(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((server_ip, server_port))
        sock.sendall(command.encode('utf-8'))
        response = sock.recv(1024)
        print('Response:', response.decode('utf-8'))

# Example usage
while True:
    command = input('Enter command (UP, DOWN, LEFT, RIGHT, STOP): ')
    if command in ['UP', 'DOWN', 'LEFT', 'RIGHT', 'STOP']:
        send_command(command)
    else:
        print('Invalid command. Please enter UP, DOWN, LEFT, RIGHT, or STOP.')
