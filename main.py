import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request


class Blockchain:
    def __init__(self):
        self.current_transactions = []  # список для хранения транзакций
        self.chain = []  # список для хранения всех блоков
        self.nodes = set()  # список узлов

        # Генезис блок - самый первый блок без предыдущего
        genesis = self.new_block(previous_hash='1', proof=100)
        self.chain = [genesis]

    def register_node(self, address):
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:

            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def valid_chain(self, chain):
        """
                Проверяем, является ли внесенный в блок хеш корректным
                chain(list) -  blockchain
                возвращаем булевую переменную: True  или  False
                """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(block):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
                Это  алгоритм Консенсуса, он разрешает конфликты,
                заменяя нашу цепь на самую длинную в цепи
                Возвращает булевую переменную
                """
        neighbours = self.nodes
        new_chain = None

        # Ищем только цепи, длиннее нашей
        max_length = len(self.chain)

        # Захватываем и проверяем все цепи из всех узлов сети
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            print(response)
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Проверяем, является ли длина самой длинной, а цепь - валидной
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Заменяем нашу цепь, если найдем другую валидную и более длинную
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash):
        """
               Создание нового блока
               proof(integer) -  Доказательства проведенной работы
               previous_hash - Хеш предыдущего блока
               Возвращаем новый блок
               """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transactions = []
        return block

    # внесение новой транзакции
    def new_transaction(self, sender, recipient, amount):
        """
                Вносим новую транзакцию
                sender -  Адрес отправителя
                recipient(string) -  Адрес получателя
                amount(integer) - Сумма
                Возвращаем индекс блока, который будет хранить эту транзакцию
                """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    # Декоратор property — это функция, которая принимает другую функцию в качестве аргумента
    # и возвращает ещё одну функцию
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    # staticmethod используется для преобразования функции в статическую функцию.
    # Статический метод-это метод, который принадлежит классу, а не экземпляру класса
    # Статические методы не требуют создания экземпляра
    def hash(block):
        # Создает хэш SHA-256 блока
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    # майнинг
    def proof_of_work(self, current_block):
        while self.valid_proof(current_block) is False:
            current_block["proof"] += 1
        return current_block

    def valid_proof(self, block):
        guess = self.hash(block)
        return guess[:4] == "0000"


app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


# майнинг нового блока
@app.route('/mine', methods=['GET'])
def mine():
    # if port == "5000":
    #     return jsonify({'message': 'You dont have rules :('}), 200
    # else:
    last_block = blockchain.last_block
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(0, previous_hash)
    proofed = blockchain.proof_of_work(block)
    blockchain.chain.append(proofed)
    response = {
        'message': "New Block Forged",
        'index': proofed['index'],
        'transactions': proofed['transactions'],
        'proof': proofed['proof'],
        'previous_hash': proofed['previous_hash'],
    }
    return jsonify(response), 200


# создание новой транзакции в блоке
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


# вывод всех цепочек
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


# принятие список новых узлов в форме URL-ов
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


# реализации алгоритма Консенсуса, который решает любые конфликты, связанные с подтверждением того,
# что узел находиться в своей цепи
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


@app.route('/ping', methods=['GET'])
def ping():
    return "", 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)
