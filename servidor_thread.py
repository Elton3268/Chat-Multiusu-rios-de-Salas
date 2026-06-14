import socket
import threading

HOST = "0.0.0.0"
PORTA = 5000

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((HOST, PORTA))
servidor.listen()

print("Servidor de Chat iniciado e aguardando conexões na rede local.....")

dicionario_clientes = {}

def broadcast_sala(mensagem, remetente, sala_destino):
    for cliente, info in list(dicionario_clientes.items()):
        if info["sala"] == sala_destino and cliente != remetente:
            try:
                cliente.send(mensagem.encode())
            except:
                pass

# Escuta requisições diretas de descoberta
def responder_discovery():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp.bind(("0.0.0.0", 5001))
    
    while True:
        try:
            mensagem, endereco_cliente = udp.recvfrom(1024)
            if mensagem.decode() == "CADE_O_SERVIDOR":
                udp.sendto("ESTOU_AQUI".encode(), endereco_cliente)
        except:
            pass

thread_discovery = threading.Thread(target=responder_discovery)
thread_discovery.daemon = True
thread_discovery.start()

def tratar_cliente(cliente, endereco):
    print(f"Novo usuário conectado via LAN: {endereco}")
    nome_usuario = f"User_{endereco[1]}"
    sala_atual = "geral" 
    
    try:
        nome_recebido = cliente.recv(1024).decode().strip()
        if nome_recebido:
            nome_usuario = nome_recebido
            
        dicionario_clientes[cliente] = {"nome": nome_usuario, "sala": sala_atual}
        print(f"Cliente {endereco} registrou-se como: {nome_usuario}")
        
        msg_entrada = f"--- {nome_usuario} entrou na sala {sala_atual} ---"
        broadcast_sala(msg_entrada, cliente, sala_atual)
        
        while True:
            mensagem = cliente.recv(1024).decode()
            if not mensagem: 
                break
                
            if mensagem.startswith("/sala "):
                nova_sala = mensagem.split(" ")[1].strip() # Captura o nome enviado pelo cliente
                msg_saida_sala = f"--- {nome_usuario} mudou de sala ---"
                broadcast_sala(msg_saida_sala, cliente, sala_atual)
                
                sala_atual = nova_sala
                dicionario_clientes[cliente]["sala"] = sala_atual
                
                # Envia confirmação ao usuário sem o prefixo "#"
                cliente.send(f"--- Você entrou na sala {sala_atual} ---\n".encode())
                
                # Notifica os outros membros da sala
                msg_entrada_sala = f"--- {nome_usuario} entrou na sala ---"
                broadcast_sala(msg_entrada_sala, cliente, sala_atual)
            else:
                msg_formatada = f"[{sala_atual}] {nome_usuario}: {mensagem}"
                print(f"Transmitindo: {msg_formatada}")
                broadcast_sala(msg_formatada, cliente, sala_atual)
                
    except Exception as erro:
        print(f"Erro na conexão com {endereco}: {erro}")
    
    if cliente in dicionario_clientes:
        info_usuario = dicionario_clientes[cliente]
        msg_desconexao = f"--- {info_usuario['nome']} desconectou-se ---"
        broadcast_sala(msg_desconexao, cliente, info_usuario["sala"])
        del dicionario_clientes[cliente]
        
    print(f"Cliente {endereco} desconectado. Total online: {len(dicionario_clientes)}")
    cliente.close()

while True:
    try:
        cliente, endereco = servidor.accept()
        thread = threading.Thread(target=tratar_cliente, args=(cliente, endereco))
        thread.start()
    except KeyboardInterrupt:
        print("\nEncerrando o servidor...")
        break