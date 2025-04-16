from twisted.internet import reactor, protocol
from company import Company # Importando a classe Company do módulo company que tem a lógica de gerenciamento de calls
import json

class CompanyProtocol(protocol.Protocol): # Definindo a classe CompanyProtocol que herda de protocol.Protocol
    def connectionMade(self): # Método chamado quando a conexão é estabelecida
        self.factory.clients.append(self) # Adiciona o cliente à lista de clientes da fábrica

    def connectionLost(self, reason): # Método chamado quando a conexão é perdida
        self.factory.clients.remove(self)

    def dataReceived(self, data): # Método chamado quando dados são recebidos do cliente 
        cmd = json.loads(data.decode()) # Decodifica os dados recebidos
        responses = self.factory.company.handle_command(cmd) # Chama o método handle_command da classe Company para processar o comando
        for msg in responses: # Para cada resposta recebida, envia a resposta de volta para o cliente
            self.send_response(msg) 
        

    def send_response(self, message): # Método para enviar a resposta de volta para o cliente
        response = json.dumps({"response": message}).encode() # Codifica a mensagem em JSON
        self.transport.write(response + b'\n') 

class CompanyFactory(protocol.Factory): # Definindo a classe CompanyFactory que herda de protocol.Factory
    def __init__(self):
        self.company = Company(['A', 'B']) # Instancia a classe Company com os IDs dos operadores
        self.clients = [] # Lista para armazenar os clientes conectados

    def buildProtocol(self, addr): # Método chamado para construir o protocolo para cada conexão
        proto = CompanyProtocol() # Instancia a classe CompanyProtocol
        proto.factory = self 
        return proto 
 
if __name__ == '__main__':
    reactor.listenTCP(5678, CompanyFactory()) # Inicia o servidor TCP na porta 5678
    print("Server listening on port 5678...")
    reactor.run() # Inicia o loop do reactor para processar eventos assíncronos
