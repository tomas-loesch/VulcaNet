from collections import deque

class Operator:
    def __init__(self, id):
        self.id = id
        self.state = 'available'
        self.current_call = None

class Company:
    def __init__(self, operator_ids):
        self.operators = {}  

        for id in operator_ids:
            self.operators[id] = Operator(id)

        self.call_queue = deque()
        self.call_map = {}

    def handle_command(self, cmd):
        command = cmd.get("command")
        id_ = cmd.get("id")
        if command == "call":
            return self._do_call(id_)
        elif command == "answer":
            return self._do_answer(id_)
        elif command == "reject":
            return self._do_reject(id_)
        elif command == "hangup":
            return self._do_hangup(id_)
        elif command == "ping":
            return ["Digite os comandos: call, answer, reject, hangup"]
        return f"Unknown command: {command}"

    def _do_call(self, call_id):
        output = [f"Call {call_id} received"]
        for i in self.operators.values():
            if i.state == 'available':
                i.state = 'ringing'
                i.current_call = call_id
                output.append(f"Call {call_id} ringing for operator {i.id}")
                return output
        self.call_queue.append(call_id)
        output.append(f"Call {call_id} waiting in queue")
        return output

    def _do_answer(self, operator_id):
        operator = self.operators.get(operator_id)
        if operator and operator.state == 'ringing':
            operator.state = 'busy'
            call_id = operator.current_call
            self.call_map[call_id] = operator_id
            return [f"Call {call_id} answered by operator {operator_id}"]
        elif operator and operator.state == 'busy':
            return [f"Operator {operator_id} is busy"]

    def _do_reject(self, operator_id):
        operator = self.operators.get(operator_id)
        if operator and operator.state == 'ringing':
            call_id = operator.current_call
            operator.state = 'available'
            operator.current_call = None
            retry = self._rejected(call_id) # Manda a chamada de novo pro operador disponível
            return [f"Call {call_id} rejected by operator {operator_id}"] + retry
        

    def _do_hangup(self, call_id):
        responses = []
        operator_id = self.call_map.pop(call_id, None)
        if operator_id:
            operator = self.operators[operator_id]
            if operator.state == 'busy':
                responses.append(f"Call {call_id} finished and operator {operator_id} available")
            else:
                responses.append(f"Call {call_id} missed")
            operator.state = 'available'
            operator.current_call = None
            responses += self._deliver_next_call(operator)
        else:
            if any(i.current_call == call_id for i in self.operators.values()):
                for i in self.operators.values():
                    if i.current_call == call_id:
                        responses.append(f"Call {call_id} missed")
                        i.state = 'available'
                        i.current_call = None
                        responses += self._deliver_next_call(i)
                        break
            elif call_id in [c for c in self.call_queue]: # A call ainda estava na fila de espera
                self.call_queue.remove(call_id)
                responses.append(f"Call {call_id} missed")
        return responses

    def _deliver_next_call(self, operator):
        if self.call_queue and operator.state == 'available':
            next_call = self.call_queue.popleft()
            operator.state = 'ringing'
            operator.current_call = next_call
            return [f"Call {next_call} ringing for operator {operator.id}"]
        return []
    
    def _rejected(self, call_id): # Método para lidar com chamadas rejeitadas sem usar o _do_call e ter um received
        for i in self.operators.values(): # Itera sobre os valores dos operadores
            if i.state == 'available':
                i.state = 'ringing'
                i.current_call = call_id
                return [f"Call {call_id} ringing for operator {i.id}"]
        self.call_queue.append(call_id)
        return [f"Call {call_id} waiting in queue"]
