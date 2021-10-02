import datetime
import hashlib
import json

# O objeto flask pra criar requisições get e produzir páginas
from flask import Flask, jsonify

class Blockchain:
    # Primeiro bloco também chamado de bloco genesis
    def __init__(self):
        # O blockchain é uma lista        
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0')

    # Criação de novos blocos a partir do primeiro
    def create_block(self, proof, previous_hash):
        # O bloco é um dicionário com os itens a seguir
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
        # Inserir novos blocos é fazer append na lista
        self.chain.append(block)
        return block

    # Pegar o bloco anterior 
    def get_previous_block(self):
        return self.chain[-1]

    # Etapa de validação da mineração
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            # Produz o Hash SHA 256 com o nível de dificuldade de 4 zeros a esquerda
            # Encodificação pra texto
            # Converte para Hexadecimal
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            # Se acertar o puzzle criptográfico sai do laço
            # Encontra o Golden Nonce
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    # Uma vez que a mineração for bem sucedida
    # Entra na etapa de validação do bloco para que ele possa ser inserido no blockchain
    # Valida se o proof of work de cada bloco está correto iniciando com 4 zeros
    # Valida se o hash anterior é mesmo o hash do bloco anterior
    def hash(self, block):
        # Transforma o bloco para o formato json
        encoded_block = json.dumps(block, sort_keys = True).encode()
        # Gera o hash deste arquivo
        return hashlib.sha256(encoded_block).hexdigest()
    
    # Valida o blockchain de acordo com os itens comentados dentro da função
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            # Verifica se a cadeia de blocos é válida, os hashs estão linkados corretamente
            if block['previous_hash'] != self.hash(previous_block):
                return False
            # Verifica se cada bloco tem o um proof of work válido
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            # Atualiza o bloco analisado
            previous_block = block
            block_index += 1
        return True


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

blockchain = Blockchain()


@app.route('/mine_block', methods = ['GET'])
# Minerar um novo bloco 
# Está relacionado com o objetivo de criar um novo bloco
def mine_block():
    # Pegamos o bloco anterior
    previous_block = blockchain.get_previous_block()
    # Pegamos o proof do bloco anterior
    # Note que para chamar a função de proof of work é necessário o proof do bloco anterior
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    # Pegamos o hash do bloco anterior
    previous_hash = blockchain.hash(previous_block)
    # Criamos uma variável para receber o retorno da criação do bloco
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Parabens voce acabou de minerar um bloco no blockchain do Gensen <3',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    return jsonify(response), 200


@app.route('/get_chain', methods = ['GET'])
# Função que retorna todo o blockchain e o seu tamanho
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])
# Função que retorna se o blockchain é válido
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message' : 'Sucesso!! Tudo certo com o blockchain :)'}
    else:
        response = {'message' : 'Putz!! Algo errado com o blockchain :('}
    return jsonify(response), 200

app.run(host = '0.0.0.0', port = 5000)