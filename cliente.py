import socket

HOST = "127.0.0.1"
PORTA = 5000

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# conectando ao servidor
cliente.connect((HOST, PORTA))

while True:

    mensagem = input("Digite uma mensagem: ")

    cliente.send(mensagem.encode())