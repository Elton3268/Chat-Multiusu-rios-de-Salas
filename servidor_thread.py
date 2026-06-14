import socket
import threading

HOST = "127.0.0.1"
PORTA = 5000

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((HOST, PORTA))
servidor.listen()

print("Servidor iniciando.....")

# Dicionário de clientes: { socket_cliente: {"nome": "apelido", "sala": "#geral"} }
dicionario_clientes = {}

# Envia mensagens apenas para as pessoas que estão na MESMA sala
def broadcast_sala(mensagem, remetente, sala_destino):
    for cliente, info in dicionario_clientes.items():
        # Verifica se o cliente está na mesma sala e se não é o próprio remetente
        if info["sala"] == sala_destino and cliente != remetente:
            try:
                cliente.send(mensagem.encode())
            except:
                # Se o socket falhar, a desconexão será tratada na thread do cliente
                pass

# Função executada por cada thread para gerenciar um cliente específico
def tratar_cliente(cliente, endereco):
    print(f"Novo cliente conectado fisicamente: {endereco}")
    
    # Define valores iniciais padrão para evitar erros caso caia no except antes do registro
    nome_usuario = f"User_{endereco[1]}"
    sala_atual = "#geral"
    
    try:
        # O primeiro dado enviado pelo cliente obrigatoriamente deve ser o seu Nome/Apelido
        nome_recebido = cliente.recv(1024).decode().strip()
        if nome_recebido:
            nome_usuario = nome_recebido
            
        # Registra o cliente inicialmente na sala padrão #geral
        dicionario_clientes[cliente] = {"nome": nome_usuario, "sala": sala_atual}
        
        print(f"Cliente {endereco} registrou-se como: {nome_usuario} na sala {sala_atual}")
        
        # Avisa aos membros da sala #geral que o usuário entrou
        msg_entrada = f"--- {nome_usuario} entrou na sala {sala_atual} ---"
        broadcast_sala(msg_entrada, cliente, sala_atual)
        
        while True:
            # Aguarda e recebe as mensagens do cliente
            mensagem = cliente.recv(1024).decode()
            
            # Se o cliente fechar a conexão, o recv retorna vazio
            if not mensagem: 
                break
                
            # Verifica se o usuário enviou o comando de troca de sala: /sala #nome_da_sala
            if mensagem.startswith("/sala "):
                nova_sala = mensagem.split(" ")[1].strip()
                
                # Notifica a sala antiga sobre a saída do usuário
                msg_saida_sala = f"--- {nome_usuario}  mudou de sala  ---"
                broadcast_sala(msg_saida_sala, cliente, sala_atual)
                
                # Altera a sala atual do cliente no dicionário de controle
                sala_atual = nova_sala
                dicionario_clientes[cliente]["sala"] = sala_atual
                
                # Confirma para o próprio usuário que ele mudou de sala com sucesso
                cliente.send(f"--- Você entrou na sala {sala_atual} ---\n".encode())
                
                # Notifica os usuários da nova sala sobre a chegada dele
                msg_entrada_sala = f"--- {nome_usuario} entrou na sala {sala_atual} ---"
                broadcast_sala(msg_entrada_sala, cliente, sala_atual)
                
            else:
                # Mensagem normal: Formata e envia exclusivamente para os membros da mesma sala
                msg_formatada = f"[{sala_atual}] {nome_usuario}: {mensagem}"
                print(f"Transmitindo: {msg_formatada}")
                broadcast_sala(msg_formatada, cliente, sala_atual)
                
    except Exception as erro:
        print(f"Erro na conexão com {endereco}: {erro}")
    
    # Bloco de finalização: Executado se o loop quebrar ou se ocorrer uma exceção
    if cliente in dicionario_clientes:
        info_usuario = dicionario_clientes[cliente]
        msg_desconexao = f"--- {info_usuario['nome']} desconectou-se ---"
        broadcast_sala(msg_desconexao, cliente, info_usuario["sala"])
        del dicionario_clientes[cliente]
        
    print(f"Cliente {endereco} desconectado do sistema. Total online: {len(dicionario_clientes)}")
    cliente.close()

# Loop principal do servidor para aceitar novas conexões permanentemente
while True:
    cliente, endereco = servidor.accept()
    thread = threading.Thread(target=tratar_cliente, args=(cliente, endereco))
    thread.start()
