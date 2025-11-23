import socket

# Configurações do Servidor
SERVER_IP = '0.0.0.0'  # Escuta em todas as interfaces
SERVER_PORT = 58000    # Porta definida no enunciado [cite: 49]

# Estrutura de dados para armazenar os peers
# Formato: { seq_number: {'ip': 'x.x.x.x', 'port': 'yyyy'} }
peers_db = {}
current_seq_num = 1    # O primeiro peer recebe SQN 1 [cite: 9]

def main():
    global current_seq_num
    
    # Criar socket UDP (SOCK_DGRAM) [cite: 8, 161]
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        sock.bind((SERVER_IP, SERVER_PORT))
        print(f"[*] Servidor de Peers iniciado em {SERVER_IP}:{SERVER_PORT} (UDP)")
    except Exception as e:
        print(f"[!] Erro ao iniciar servidor: {e}")
        return

    while True:
        try:
            # Receber dados (buffer de 1024 bytes deve chegar)
            data, client_addr = sock.recvfrom(1024) # [cite: 162]
            message = data.decode('utf-8').strip()
            print(f"[LOG] Recebido de {client_addr}: {message}")

            # Processar comando
            parts = message.split()
            if not parts:
                continue
            
            command = parts[0].upper()
            response = "NOK" # Resposta padrão em caso de erro

            # --- COMANDO REG (Registar) [cite: 90] ---
            if command == "REG" and len(parts) == 2:
                lnkport = parts[1]
                client_ip = client_addr[0] # IP vem do cabeçalho UDP
                
                # Atribuir número de sequência e guardar
                seq = current_seq_num
                peers_db[seq] = {'ip': client_ip, 'port': lnkport}
                
                print(f"[+] Peer registado: {client_ip}:{lnkport} com SQN {seq}")
                response = f"SQN {seq}" # Resposta: SQN seqnumber [cite: 92]
                current_seq_num += 1

            # --- COMANDO PEERS (Listar) [cite: 98] ---
            elif command == "PEERS":
                # Formato da resposta:
                # LST
                # IP:port#seq
                # (linha vazia)
                lines = ["LST"]
                for seq, info in peers_db.items():
                    # Formato especificado: IPaddress:lnkport#seqnumber [cite: 101]
                    line = f"{info['ip']}:{info['port']}#{seq}"
                    lines.append(line)
                
                response = "\n".join(lines) + "\n" # Termina com linha vazia

            # --- COMANDO UNR (Remover) [cite: 94] ---
            elif command == "UNR" and len(parts) == 2:
                try:
                    seq_to_remove = int(parts[1])
                    if seq_to_remove in peers_db:
                        del peers_db[seq_to_remove]
                        print(f"[-] Peer removido: SQN {seq_to_remove}")
                        response = "OK" # [cite: 97]
                    else:
                        print(f"[!] Tentativa de remover SQN inexistente: {seq_to_remove}")
                        response = "NOK"
                except ValueError:
                    response = "NOK"

            # Enviar resposta de volta ao cliente
            sock.sendto(response.encode('utf-8'), client_addr)

        except KeyboardInterrupt:
            print("\nEncerrando servidor...")
            break
        except Exception as e:
            print(f"[!] Erro no loop: {e}")

    sock.close()

if __name__ == "__main__":
    main()