import socket
import threading
import sys

HOST = "127.0.0.1"
PORTA = 5000

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((HOST, PORTA))

# Requisito Inicial do Novo Fluxo: Solicitar o nome antes de entrar no chat
nome = input("Escolha seu nome de usuário/apelido: ")
cliente.send(nome.encode())

print("\n==================================================")
print(" Conectado ao Servidor com sucesso!")
print(" Sala atual: geral")
print(" Para mudar de sala digite: /sala #nomedasala")
print("==================================================\n")

# Função executada por uma thread exclusiva para escutar o servidor continuamente
def receber_mensagens():
    while True:
        try:
            mensagem = cliente.recv(1024).decode()
            if not mensagem:
                print("\nConexão encerrada pelo servidor.")
                break
            # Printa a mensagem recebida e quebra a linha
            print(mensagem)
        except:
            print("\nOcorreu um erro na comunicação com o servidor.")
            break
    cliente.close()
    sys.exit()

# Iniciando a thread de recepção de dados
thread_receber = threading.Thread(target=receber_mensagens)
# Daemon garante que se fecharmos o programa principal, a thread fecha junto
thread_receber.daemon = True 
thread_receber.start()

# O loop principal agora fica livre exclusivamente para capturar entradas do teclado e enviar
while True:
    try:
        mensagem = input()
        if mensagem.strip():
            cliente.send(mensagem.encode())
    except KeyboardInterrupt:
        # Tratamento caso o usuário aperte Ctrl+C para sair
        print("\nSaindo do chat...")
        break

cliente.close()