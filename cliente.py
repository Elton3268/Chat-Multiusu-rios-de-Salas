import socket
import threading
import sys
import time

PORTA = 5000
ip_servidor_encontrado = None

# Função que testa um único IP específico para ver se o servidor responde
def sondar_ip(ip_alvo):
    global ip_servidor_encontrado
    if ip_servidor_encontrado: # Se alguém já achou, interrompe as outras threads
        return
        
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.settimeout(0.8) # Tempo de resposta rápido por IP
    try:
        udp.sendto("CADE_O_SERVIDOR".encode(), (ip_alvo, 5001))
        mensagem, endereco = udp.recvfrom(1024)
        if mensagem.decode() == "ESTOU_AQUI":
            ip_servidor_encontrado = endereco[0]
    except:
        pass
    finally:
        udp.close()

# Função que varre a sub-rede por amostragem paralela
def descobrir_servidor_por_varredura():
    print("Iniciando varredura inteligente na sub-rede local...")
    
    # Descobrir o próprio IP local conectado à internet
    s_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s_temp.connect(("8.8.8.8", 80))
        meu_ip = s_temp.getsockname()[0]
    except:
        meu_ip = "127.0.0.1"
    finally:
        s_temp.close()
        
    if meu_ip == "127.0.0.1":
        return None
        
    # Extrai a raiz da rede
    partes_ip = meu_ip.split(".")
    raiz_subrede = f"{partes_ip[0]}.{partes_ip[1]}.{partes_ip[2]}."
    
    threads_varredura = []
    
    # Cria threads para testar todos os 254 endereços possíveis da rede simultaneamente
    for i in range(1, 255):
        ip_alvo = f"{raiz_subrede}{i}"
        t = threading.Thread(target=sondar_ip, args=(ip_alvo,))
        threads_varredura.append(t)
        t.start()
        
    # Aguarda um curto período para dar tempo das threads terminarem as checagens
    time.sleep(1.2)
    
    if ip_servidor_encontrado:
        print(f"Servidor localizado automaticamente via varredura no IP: {ip_servidor_encontrado}\n")
        return ip_servidor_encontrado
        
    return None

# Tenta localizar usando mapeamento de sub-rede
HOST = descobrir_servidor_por_varredura()

if not HOST:
    print("Não foi possível localizar o servidor na sub-rede de forma automatizada.")
    sys.exit()

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    cliente.connect((HOST, PORTA))
except Exception as erro:
    print(f"Erro de conexão com o IP localizado {HOST}: {erro}")
    sys.exit()

nome = input("Escolha seu nome de usuário/apelido para o chat: ")
cliente.send(nome.encode())

print("\n==================================================")
print(" Conectado ao Servidor de Chat via Rede Local")
print(" Sala inicial padrão: geral")
print(" Para mudar de sala digite: /sala nomedasala")
print("==================================================\n")

def receber_mensagens():
    while True:
        try:
            mensagem = cliente.recv(1024).decode()
            if not mensagem:
                print("\nA conexão foi encerrada pelo servidor central.")
                break
            print(mensagem)
        except:
            print("\nOcorreu um erro na recepção de mensagens do servidor.")
            break
            
    cliente.close()
    sys.exit()

thread_receber = threading.Thread(target=receber_mensagens)
thread_receber.daemon = True
thread_receber.start()

while True:
    try:
        mensagem = input()
        if mensagem.strip():
            cliente.send(mensagem.encode())
    except KeyboardInterrupt:
        print("\nSaindo do chat de forma segura...")
        break

cliente.close()