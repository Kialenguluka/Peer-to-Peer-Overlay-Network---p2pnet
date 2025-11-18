# Memorando — Tarefa 3 (Cliente/Servidor Web simples)

Este memorando documenta a implementação e a análise de pacotes para a Tarefa #3.

**Entregáveis incluídos**

- `Vagrantfile` (modificado para rede privada com IP `192.168.56.21` para o servidor).
- `webserver.py`: servidor TCP que escuta em `0.0.0.0:6789` e serve `index.html`.
- `webclient.py`: cliente Python para efetuar `GET` e guardar a resposta.

**Instruções para reprodução dos testes**

1. Levantar as VMs e aceder ao `webserver`:

```powershell
vagrant up
vagrant ssh webserver
cd /vagrant
python3 webserver.py
```

2. A partir da VM `client` (ou do host) executar o teste com `telnet`:

```powershell
telnet 192.168.56.21 6789
# Depois de ligar, escrever manualmente:
GET /index.html HTTP/1.1
Host: 192.168.56.21

# (pressionar Enter duas vezes)
```

3. A partir da VM `client` executar o cliente Python:

```powershell
python3 webclient.py 192.168.56.21 6789 /index.html
```

4. Capturar pacotes com `tcpdump` (no servidor ou no cliente) enquanto executa os testes:

```bash
sudo tcpdump -i any -w /vagrant/telnet_test.pcap port 6789
```

Parar o `tcpdump` depois de terminar os testes (Ctrl+C) e copiar o ficheiro `.pcap` para análise no Wireshark.

**Capturas de ecrã a anexar**

- Resultado do comando: `telnet 192.168.56.21 6789` (mostrar pedido e resposta no ecrã).
- Resultado do comando: `python webclient.py 192.168.56.21 6789 /index.html` (mostrar saída e ficheiro `last_response.txt`).
- Screenshots do Wireshark mostrando handshake, pedido HTTP, resposta HTTP e encerramento da ligação.

**Análise dos pacotes TCP — teste com `telnet`**

Resumo observável (modelo):

- Three-way handshake:
  - Cliente -> Servidor: SYN (porta cliente aleatória -> 6789)
  - Servidor -> Cliente: SYN-ACK (6789 -> porta cliente)
  - Cliente -> Servidor: ACK (porta cliente -> 6789)

- Pedido HTTP (enviado manualmente pelo utilizador via `telnet`):
  - Pacote com payload contendo a linha `GET /index.html HTTP/1.1` e cabeçalhos (Host, etc.).
  - Observar os números de sequência (SEQ) e acknowledgement (ACK) para cada segmento.

- Resposta do servidor:
  - Um ou mais segmentos TCP com payload contendo os headers HTTP (`HTTP/1.1 200 OK`, `Content-Length`, `Content-Type`) e o corpo (HTML).
  - Se o corpo for maior do que MSS, será fragmentado em múltiplos segmentos TCP.

- Fecho da conexão:
  - Normalmente observa-se um par FIN/ACK de cada lado, ou o servidor/cliente fecha com `RST` se houver encerramento abrupto.

Pontos para incluir no memorando:

- Capturas de pacotes destacando os bytes exatos do pedido (`GET ...`) e da resposta (`HTTP/1.1 200 OK`).
- Anotar timestamps para mostrar a latência entre handshake e envio do pedido (no `telnet` haverá atraso por digitação manual).
- Indicar a presença de retransmissões, se existirem, e explicar porque aconteceram (ex.: perda simulada, congestionamento).

**Análise dos pacotes TCP — teste com `webclient.py`**

Resumo observável (modelo):

- O cliente Python automatizado inicia a ligação, envia o pedido `GET` imediatamente após o handshake e espera a resposta.
- Espera-se menor delta de tempo entre handshake e primeiro segmento com payload quando comparado com `telnet`.
- A resposta do servidor segue o mesmo padrão: headers + corpo, possivelmente em múltiplos segmentos.
- O cliente grava a resposta em `last_response.txt` e fecha a ligação (campo `Connection: close` no pedido/ resposta causa o encerramento ordenado).

Pontos para incluir no memorando:

- Captura e inspeção do pacote com o pedido automático — incluir a linha exata enviada pelo cliente Python.
- Captura da resposta do servidor e dos headers importantes (`Content-Length`, `Connection`).
- Comparar tempos e número de pacotes entre o teste `telnet` (manual) e o `webclient.py` (automático).

**Conclusão (modelo)**

Descreva brevemente o que foi verificado: estabelecimento de sessão TCP, entrega do pedido HTTP, envio da resposta, e encerramento ordenado da ligação. Reforce se os pacotes observados correspondem ao comportamento esperado e anexe as capturas e ficheiros `.pcap` como evidência.

---

Nota: substitua as secções "modelo" pelos detalhes reais obtidos nas capturas e pelas screenshots antes de submeter o memorando.
