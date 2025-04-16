import cmd # Módulo para simplificar a interação com o usuário
from collections import deque # Método de fila mais eficiente. Pode ser manipulado nas duas extremidades

class Operator: #Criando a classe operador
    def __init__(self, id):
        self.id = id
        self.state = 'available'
        self.current_call = None

class Company(cmd.Cmd): # Criando a classe Company que herda de cmd.Cmd
    prompt = '' # Começo da linha para input

    def __init__(self, operator_ids):
        super().__init__() # Herda o método __init__() da classe cmd.Cmd
        self.operators = {}  

        for id in operator_ids:
            self.operators[id] = Operator(id)  # Adiciona cada operador ao dicionário

        self.call_queue = deque() #Cria uma fila de call usando deque
        self.call_map = {}  # Dicionário para mapear calls a operadores

    def do_call(self, call_id): # Método para receber chamadas, utilizando o módulo cmd
        print(f"Call {call_id} received")
        self._handle_call(call_id) # Chama o método _handle_call para lidar com a call

    def do_answer(self, operator_id): # Método para atender calls
        operator = self.operators.get(operator_id) # Pega o operador pelo id
        if operator and operator.state == 'ringing':
            operator.state = 'busy'
            call_id = operator.current_call
            self.call_map[call_id] = operator_id # Mapeia a call ao operador
            print(f"Call {call_id} answered by operator {operator_id}")
        elif operator and operator.state == 'busy':
            print(f"Operator {operator_id} is busy")
      
    def do_reject(self, operator_id): # Método para rejeitar calls
        operator = self.operators.get(operator_id)
        if operator and operator.state == 'ringing':
            call_id = operator.current_call
            print(f"Call {call_id} rejected by operator {operator_id}")
            operator.state = 'available'
            operator.current_call = None
            self._handle_call(call_id)

    def do_hangup(self, call_id): # Método para encerrar calls
        operator_id = self.call_map.get(call_id)
        if operator_id:
            operator = self.operators[operator_id]
            if operator.state == 'busy':
                print(f"Call {call_id} finished and operator {operator_id} available")
            else:   
                print(f"Call {call_id} missed")
            operator.state = 'available'
            operator.current_call = None
            self.call_map.pop(call_id) # Remove a call do dicionário
            self._deliver_next_call(operator) 
        else:  # A call está tocando para algum operador
            if any(i.current_call == call_id for i in self.operators.values()):
                for i in self.operators.values():
                    if i.current_call == call_id:
                        print(f"Call {call_id} missed")
                        i.state = 'available'
                        i.current_call = None
                        self._deliver_next_call(i)
                        break
            elif call_id in [c for c in self.call_queue]: # A call ainda estava na fila de espera
                self.call_queue.remove(call_id)
                print(f"Call {call_id} missed")

    def _handle_call(self, call_id): # Método para lidar com as calls
        for i in self.operators.values(): # Itera sobre os valores dos operadores
            if i.state == 'available':
                i.state = 'ringing'
                i.current_call = call_id
                print(f"Call {call_id} ringing for operator {i.id}")
                return
        self.call_queue.append(call_id) # Adiciona o id da call na fila
        print(f"Call {call_id} waiting in queue")

    def _deliver_next_call(self, operator): # Método para entregar a próxima call 
        if self.call_queue and operator.state == 'available':
            next_call = self.call_queue.popleft() # Remove a call da fila
            operator.state = 'ringing'
            operator.current_call = next_call
            print(f"Call {next_call} ringing for operator {operator.id}")

    def do_exit(self, _): # Método para encerrar o programa
        print("Exiting.")
        return True

if __name__ == '__main__':
    Company(['A', 'B']).cmdloop() # Inicia o loop de comandos instanciando Company com os operadores A e B
