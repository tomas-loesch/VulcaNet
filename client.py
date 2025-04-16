from twisted.internet import reactor, protocol # importando o módulo reactor e protocol do Twisted responsável por gerenciar conexões e eventos assíncronos
import json, sys  # importando os módulos json e sys para manipulação de dados JSON e entrada/saída do sistema

class CallClientProtocol(protocol.Protocol): # definindo a classe CallClientProtocol que herda de protocol.Protocol
    def connectionMade(self): # definindo o método connectionMade que é chamado quando a conexão é estabelecida
        self.transport.write(json.dumps({"command": "ping", "id": "0"}).encode() + b'\n') # enviando um comando de ping para o servidor quando a conexão é estabelecida
        # codificando o comando em JSON e adicionando uma nova linha no final


    def dataReceived(self, data): # definindo o método dataReceived que é chamado quando dados são recebidos do servidor
        for line in data.decode().splitlines():
            if not line.strip():
                continue
            response = json.loads(line) # decodificando os dados recebidos e separando as linhas
            print(response.get("response", "[sem resposta]"))


    def send_command(self, line): # definindo o método send_command que envia comandos para o servidor
        parts = line.strip().split()
        if len(parts) == 2:
            cmd, id_ = parts
            if cmd in ["call", "answer", "reject", "hangup"]: 
                data = json.dumps({"command": cmd, "id": id_}) 
                self.transport.write(data.encode())
                return
        print("Invalid command")

class CallClientFactory(protocol.ClientFactory): # definindo a classe CallClientFactory que herda de protocol.ClientFactory
    def __init__(self): # Factory cria instâncias de protocolo para cada conexão
        self.protocol_instance = None

    def buildProtocol(self, addr): # definindo o método buildProtocol que cria uma nova instância do protocolo
        self.protocol_instance = CallClientProtocol() 
        self.protocol_instance.factory = self 
        return self.protocol_instance # retornando a instância do protocolo

    def clientConnectionFailed(self, connector, reason): # definindo o método clientConnectionFailed que é chamado quando a conexão falha
        print("Connection failed")
        reactor.stop() # encerrando o reactor/loop do Twisted

    def clientConnectionLost(self, connector, reason): # definindo o método clientConnectionLost que é chamado quando a conexão é perdida
        print("Connection lost")
        reactor.stop()

def read_input(factory): # definindo a função read_input que lê a entrada do usuário
    line = sys.stdin.readline()
    if line: 
        if factory.protocol_instance: 
            factory.protocol_instance.send_command(line) # enviando o comando lido para o protocolo
    reactor.callLater(0.1, read_input, factory) # chamando a função novamente após um pequeno atraso, simula um loop de leitura

if __name__ == '__main__':
    factory = CallClientFactory()
    reactor.connectTCP("localhost", 5678, factory)
    reactor.callLater(0.1, read_input, factory) # iniciando a leitura da entrada do usuário
    reactor.run()
