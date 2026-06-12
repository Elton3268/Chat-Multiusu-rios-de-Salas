import socket
import threading # permite criar multiplas threads, permite executar várias tarefas ao mesmo tempo

HOST = "127.0.0.1"
PORTA = 5000

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

servidor.bind((HOST, PORTA)) # associando endereço de IP e porta

servidor.listen() # servidor em modo de escuta

print("Servidor iniciando.....")

lista_clientes = [] # lista de clientes

def broadcast(mensagem, remetente):

    for cliente in lista_clientes:
        # verifica se é o determinado cliente que enviou
        if cliente != remetente:
            cliente.send(mensagem.encode())

# criando uma função que será executada por cada thread
def tratar_cliente(cliente, endereco):

    print(f"Novo cliente conectado:  {endereco}")

    while True: # fica recebendo mensagens do cliente

        # Tratamento de erros:
        try:
            # a mensagem recebe até 1024 bytes depois decodifica
            mensagem = cliente.recv(1024).decode() # Recebe mensagens continuamente.

            if not mensagem: # Se o cliente fechar o recv retorna vazio
                break # encerra o loop
            
            print(f"{endereco}: {mensagem}") # mostrando a mensagem, exemplo: (127.0.0.1, 53120): ola
            broadcast(mensagem, cliente)
        
        except: # se ocorrer qualquer erro o loop termina

            break
    
    print(f"Cliente {endereco} desconectado") # mostra quem saiu

    cliente.close() # encerrando a conexão daquele determinado cliente

while True: # loop do servidor

    cliente, endereco = servidor.accept() # aguardando alguém conectar

    # Assim que o cliente se conecta é adicionado dentro da lista
    lista_clientes.append(cliente)

    print("Clientes conectados:", len(lista_clientes)) # imprime o tamanho da lista dos clientes

    #  target= -> Vai executar a função (tratar_cliente),  args=() -> coloca os parâmetros
    thread = threading.Thread(target=tratar_cliente, args=(cliente, endereco))

    thread.start() # Iniciando thread