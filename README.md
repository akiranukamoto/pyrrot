# Pyrrot

Pyrrot é um simples serviço feito em python para simular a resposta de aplicações rest.

$ pip install pyrrot
$ pyrrot -c caminho_das_configuracoes

## Setup Local

Assumindo que você tenha o python 3.6 instalado.

#### 1. Clone o projeto:

    $ git clone git@github.com:akiranukamoto/pyrrot.git
    $ cd pyrrot

#### 2. Criar um virtualenv para o projeto e instalar dependências:

    $ python -m venv .venv
    $ python setup.py install

#### 3. Inicializar a aplicação:

    $ pyrrot -c caminho_das_configuracoes

## Executar testes

    $ pytest tests/

## Configuração (yml)

Um simple exemplo de um yml para a configuração de uma api:

```
- name: "Get users"
  description: ""
  when:
    path: users
    method: GET
    type: application/json
    header:
      TRACKID: abc123456
    query:
      foo: bar
  then:
    type: application/json
    header:
      TRACKID: abc123456
    body:
      name: John Doe
      identity: 666
    code: 200
```

### Regex:
Path, header, body e query aceitam regex:

```
- name: "Insert customers"
  description: ""
  when:
    path: $regex=.*customers.*
    method: POST
    type: application/json
    header:
      TRACKID: $regex=.*access.*
    body:
      name: $regex=(?i).*Cola.*
      identity: $regex=^([2-9]|1[0-6])$
  then:
    type: application/json
    header:
      TRACKID: abc123456
    body:
      name: Coca Cola
      identity: 1234567
    code: 201
```