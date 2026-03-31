# 💬 Projeto de Comunicação via Sockets - Redes de Computadores

Este projeto foi desenvolvido como parte de um trabalho prático da disciplina de **Infraestrutura de Redes e Comunicação**. A aplicação implementa uma comunicação básica entre **cliente** e **servidor** utilizando **sockets TCP em Python**, com foco na criação da base inicial do sistema de transmissão confiável que será expandido nas próximas etapas do trabalho.

## 📌 Objetivo da Etapa Atual

Nesta etapa do projeto, o objetivo é implementar:

1. a conexão entre cliente e servidor via socket;
2. o **handshake inicial** da comunicação;
3. a troca de parâmetros básicos no início da conexão, como:
   - **modo de operação**;
   - **tamanho máximo da mensagem**.

Essa etapa corresponde à base da aplicação, preparando a estrutura para as próximas implementações do trabalho.

## ⚙️ Tecnologias Utilizadas

- Python 3.x
- Biblioteca `socket` (nativa do Python)
- Protocolo de transporte: **TCP/IP**

## 📁 Estrutura do Projeto

```text
.
├── client.py
├── server.py
└── README.md
```

## 🔄 Funcionamento

1. O servidor é iniciado e fica aguardando conexão na porta configurada.
2. O cliente se conecta ao servidor.
3. O cliente informa os dados iniciais da comunicação:

- modo de operação (gbn ou rs)
- tamanho máximo da mensagem

4. Essas informações são enviadas ao servidor no handshake inicial.
5. O servidor valida os dados recebidos.
6. O servidor retorna uma resposta de confirmação ao cliente.

## 🤝 Handshake Inicial

O handshake é utilizado para estabelecer os parâmetros iniciais da comunicação entre cliente e servidor.

- Dados enviados pelo cliente

* modo de operação
  - gbn
  - rs
* tamanho máximo da mensagem - valor inteiro - mínimo de 30
  Exemplo de mensagem enviada
  gbn,30
  Exemplo de resposta do servidor
  Handshake OK | modo=gbn | tamanho_max=30

## 📏 Sobre o tamanho máximo da mensagem

O sistema solicita um limite máximo para a mensagem, definido no início da comunicação.

Esse valor:

deve ser informado pelo cliente;
deve ser um número inteiro;
deve ser maior ou igual a 30.

## ▶️ Como Executar

1. Iniciar o servidor
   python server.py
2. Em outro terminal, iniciar o cliente
   python client.py
3. Interagir com o sistema
   Informe o modo desejado (gbn ou rs);
   Informe o tamanho máximo da mensagem;
   Aguarde a resposta do servidor após o handshake.

## 🧪 Exemplo de execução

- Cliente
  Escolha o modo (gbn/rs): gbn
  Digite o tamanho máximo da mensagem (mínimo 30): 30
  Resposta do servidor: Handshake OK | modo=gbn | tamanho_max=30
- Servidor
  Servidor aguardando conexão na porta 2048...
  Conectado a ('127.0.0.1', XXXXX)
  Handshake recebido: gbn,30

🤖 Uso de IA

Foi utilizada IA como apoio para:

interpretar o enunciado do trabalho;
organizar a estrutura do README;
auxiliar na redação da documentação desta etapa;
esclarecer a interpretação de requisitos da primeira implementação.

A utilização da IA ocorreu apenas como apoio à organização e documentação. O código final foi revisado e compreendido pelo grupo antes da entrega.

## 👥 Equipe

- Artur Antunes
- Danilo Duleba
- Gabriel Pontes
- Gabriel Roma
- João Cláudio Beltrão
- Kaique Alves
- Luca Albuquerque
- Luiz Flavius Veras
- Ricardo Machado
- Victor Uen
