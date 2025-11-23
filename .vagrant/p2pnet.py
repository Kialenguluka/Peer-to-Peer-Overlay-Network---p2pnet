import socket
import sys
import argparse
import select

class P2PNode:
    def __init__(self, server_ip, server_port, lnk_port, max_neighbors, hop_count):
        # Configurações
        self.server_addr = (server_ip, server_port)
        self.lnk_port = lnk_port
        self.max_neighbors = max_neighbors
        self.hop_count = hop_count
        
        self.seq_number = None
        self.neighbors_info = {} # {sock: {'ip':..., 'port':..., 'seq':..., 'type':...}}
        
        # --- NOVO: Gestão de Conteúdos ---
        self.identifiers = set() # Lista de IDs que eu conheço
        
        # Tabela de Encaminhamento para Respostas de Pesquisa
        # Chave: Identifier | Valor: Lista de sockets que me perguntaram por ele
        # Ex: "filme.avi" -> [sock_vizinho_A, sock_vizinho_B]
        self.pending_searches = {}

        # Sockets
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.settimeout(2.0)

        self.tcp_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.tcp_listener.bind(('0.0.0.0', self.lnk_port))
            self.tcp_listener.listen(5)
            print(f"[*] Servidor TCP a escutar na porta {self.lnk_port}")
        except Exception as e:
            print(f"[!] Erro ao abrir porta TCP {self.lnk_port}: {e}")
            sys.exit(1)

        self.inputs = [sys.stdin, self.tcp_listener]

    # --- UDP (REG, UNR, PEERS) ---
    def send_udp_cmd(self, message):
        try:
            self.udp_socket.sendto(message.encode('utf-8'), self.server_addr)
            data, _ = self.udp_socket.recvfrom(4096)
            return data.decode('utf-8').strip()
        except socket.timeout:
            return None
        except Exception as e:
            return None

    def register(self):
        msg = f"REG {self.lnk_port}"
        resp = self.send_udp_cmd(msg)
        if resp and resp.startswith("SQN"):
            try:
                self.seq_number = int(resp.split()[1])
                print(f"[*] Registado com SQN: {self.seq_number}")
                return True
            except: pass
        print(f"[!] Falha registo: {resp}")
        return False

    def unregister(self):
        if self.seq_number is None: return
        self.send_udp_cmd(f"UNR {self.seq_number}")
        self.seq_number = None

    def get_peers_list(self):
        resp = self.send_udp_cmd("PEERS")
        if resp and resp.startswith("LST"):
            return [line.strip() for line in resp.split('\n')[1:] if line.strip()]
        return []

    # --- TCP: CONEXÃO ---
    def connect_to_peer(self, peer_str):
        try:
            addr_part, seq_part = peer_str.split('#')
            target_ip, target_port = addr_part.split(':')
            target_seq = int(seq_part)
            target_port = int(target_port)

            if target_seq >= self.seq_number: return False
            if target_seq == self.seq_number: return False
            if len(self.neighbors_info) >= self.max_neighbors: return False
            for info in self.neighbors_info.values():
                if info['seq'] == target_seq: return False

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5.0)
            s.connect((target_ip, target_port))
            s.send(f"LNK {self.seq_number}".encode('utf-8'))
            resp = s.recv(1024).decode('utf-8').strip()
            
            if resp == "CNF":
                s.settimeout(None)
                self.inputs.append(s)
                self.neighbors_info[s] = {'ip': target_ip, 'port': target_port, 'seq': target_seq, 'type': 'Externo'}
                return True
            else:
                s.close()
                return False
        except: return False

    def handle_new_connection(self):
        try:
            client_sock, client_addr = self.tcp_listener.accept()
            self.inputs.append(client_sock)
            self.neighbors_info[client_sock] = {'ip': client_addr[0], 'port': client_addr[1], 'seq': None, 'type': 'Interno'}
        except: pass

    # --- TCP: MENSAGENS E PESQUISA ---
    def handle_peer_message(self, sock):
        try:
            data = sock.recv(1024)
            if not data:
                self.remove_neighbor(sock)
                return

            message = data.decode('utf-8').strip()
            # print(f"[DEBUG RX] {message}")

            parts = message.split()
            cmd = parts[0]

            # 1. Handshake LNK
            if cmd == "LNK" and len(parts) == 2:
                neighbor_seq = int(parts[1])
                if sock in self.neighbors_info:
                    self.neighbors_info[sock]['seq'] = neighbor_seq
                sock.send(b"CNF\n")

            # 2. Pesquisa QRY (Recebi uma pergunta)
            # Formato: QRY identifier hopcount
            elif cmd == "QRY" and len(parts) == 3:
                ident = parts[1]
                hops = int(parts[2])

                # A. Eu tenho o conteúdo?
                if ident in self.identifiers:
                    # Respondo FND para quem perguntou
                    # print(f"    -> Tenho '{ident}'. A enviar FND.")
                    sock.send(f"FND {ident}\n".encode('utf-8'))
                
                # B. Não tenho. Devo reencaminhar?
                elif hops > 1:
                    # print(f"    -> Não tenho '{ident}'. Reencaminhando (Hops: {hops-1})...")
                    # Registar que este socket está à espera da resposta
                    if ident not in self.pending_searches:
                        self.pending_searches[ident] = []
                    self.pending_searches[ident].append(sock)

                    # Enviar para TODOS os outros vizinhos (Flooding)
                    msg = f"QRY {ident} {hops - 1}\n"
                    for neighbor in self.neighbors_info:
                        if neighbor != sock: # Não enviar de volta para quem perguntou
                            try:
                                neighbor.send(msg.encode('utf-8'))
                            except: pass
                
                # C. Não tenho e hops acabou -> Enviar NOTFND (Opcional, mas boa prática)
                else:
                    sock.send(f"NOTFND {ident}\n".encode('utf-8'))

            # 3. Resposta FND (Encontrado!)
            elif cmd == "FND" and len(parts) == 2:
                ident = parts[1]
                
                # A. Fui eu que iniciei a pesquisa? (Verificar flag especial ou se não há pendentes mas eu iniciei)
                # Simplificação: Se está nos pendentes com valor 'SELF', fui eu.
                if ident in self.pending_searches and 'SELF' in self.pending_searches[ident]:
                    if ident not in self.identifiers:
                        print(f"[*] SUCESSO! Identificador '{ident}' encontrado na rede.")
                        self.identifiers.add(ident)
                        # Limpar busca
                        del self.pending_searches[ident]
                
                # B. Sou apenas um intermediário?
                elif ident in self.pending_searches:
                    # Reencaminhar FND para quem me perguntou
                    # print(f"    -> Reencaminhando FND '{ident}' para a origem.")
                    msg = f"FND {ident}\n"
                    for origin_sock in self.pending_searches[ident]:
                        if origin_sock != 'SELF':
                            try:
                                origin_sock.send(msg.encode('utf-8'))
                            except: pass
                    # Limpar busca (Intermediários não guardam conteúdo - Secção 1)
                    del self.pending_searches[ident]

            # 4. Resposta NOTFND (Não encontrado)
            elif cmd == "NOTFND":
                pass # Ignorar ou tratar para estatísticas

        except Exception as e:
            # print(f"[!] Erro msg TCP: {e}")
            self.remove_neighbor(sock)

    def remove_neighbor(self, sock):
        if sock in self.inputs: self.inputs.remove(sock)
        if sock in self.neighbors_info: del self.neighbors_info[sock]
        sock.close()

    # --- COMANDOS DO UTILIZADOR ---
    def cmd_join(self):
        if self.seq_number is not None:
            print("[!] Já registado.")
            return
        if not self.register(): return
        peers = self.get_peers_list()
        count = 0
        for p in peers:
            if self.connect_to_peer(p): count += 1
            if len(self.neighbors_info) >= self.max_neighbors: break
        print(f"[*] Conectado a {count} novos vizinhos.")

    def handle_user_input(self):
        line = sys.stdin.readline()
        if not line: return False
        parts = line.strip().split()
        if not parts: return True

        cmd = parts[0].lower()
        
        if cmd == "join":
            self.cmd_join()
        elif cmd == "leave":
            self.unregister()
            for s in list(self.neighbors_info.keys()): self.remove_neighbor(s)
            print("[*] Saiu da rede.")
        
        # --- COMANDOS DE CONTEÚDO ---
        elif cmd == "post" and len(parts) == 2:
            ident = parts[1]
            self.identifiers.add(ident)
            print(f"[*] Identificador '{ident}' adicionado.")
        
        elif cmd == "unpost" and len(parts) == 2:
            ident = parts[1]
            if ident in self.identifiers:
                self.identifiers.remove(ident)
                print(f"[*] Identificador '{ident}' removido.")
            else:
                print("[!] Não conheço esse identificador.")

        elif cmd == "list" and len(parts) > 1 and parts[1] == "identifiers":
            print(f"Identificadores conhecidos: {list(self.identifiers)}")

        elif cmd == "search" and len(parts) == 2:
            ident = parts[1]
            if ident in self.identifiers:
                print(f"[*] Já possui '{ident}' localmente.")
            else:
                print(f">>> A pesquisar '{ident}' na rede (Hops={self.hop_count})...")
                # Marcar que fui eu que pedi ('SELF')
                self.pending_searches[ident] = ['SELF']
                # Enviar QRY para TODOS os vizinhos
                msg = f"QRY {ident} {self.hop_count}\n"
                for sock in self.neighbors_info:
                    try:
                        sock.send(msg.encode('utf-8'))
                    except: pass

        elif cmd == "show" and len(parts) > 1 and parts[1] == "neighbors":
            print(f"Vizinhos: {len(self.neighbors_info)}")
            for info in self.neighbors_info.values():
                print(f"- SQN {info['seq']} ({info['type']}) IP {info['ip']}")

        elif cmd == "exit":
            self.unregister()
            sys.exit(0)
        else:
            print("Comando desconhecido ou incompleto.")
        
        sys.stdout.write("> ")
        sys.stdout.flush()
        return True

    def run(self):
        print(f"--- P2PNet (Porta: {self.lnk_port}) ---")
        sys.stdout.write("> ")
        sys.stdout.flush()
        while True:
            try:
                readable, _, _ = select.select(self.inputs, [], [])
                for src in readable:
                    if src == sys.stdin:
                        if not self.handle_user_input(): return
                    elif src == self.tcp_listener:
                        self.handle_new_connection()
                    else:
                        self.handle_peer_message(src)
            except KeyboardInterrupt:
                self.unregister()
                break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", default="192.168.56.21")
    parser.add_argument("-p", type=int, default=58000)
    parser.add_argument("-l", type=int, required=True)
    parser.add_argument("-n", type=int, default=2)
    parser.add_argument("-h_count", type=int, default=3)
    args = parser.parse_args()
    P2PNode(args.s, args.p, args.l, args.n, args.h_count).run()