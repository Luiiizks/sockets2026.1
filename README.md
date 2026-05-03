# Projeto de Comunicacao via Sockets

Trabalho pratico da disciplina de Infraestrutura de Redes e Comunicacao.

A aplicacao usa sockets TCP em Python para fazer a comunicacao entre cliente e servidor. Nesta segunda entrega, o sistema ja faz o handshake inicial e tambem permite a troca de mensagens em um canal sem erros e sem perdas.

## Objetivo desta entrega

Nesta etapa foram implementados:

1. conexao entre cliente e servidor via socket;
2. handshake inicial com modo de operacao e tamanho maximo da mensagem;
3. envio de mensagens de texto do cliente para o servidor;
4. divisao da mensagem em pacotes com ate 4 caracteres;
5. envio de pacotes isolados ou em lote;
6. confirmacoes do servidor para o cliente;
7. reconstrucao da mensagem completa no servidor.

## Tecnologias

- Python 3
- Biblioteca `socket`
- Biblioteca `json`

## Arquivos

```text
.
├── client.py
├── server.py
└── README.md
```

## Protocolo usado

O handshake e enviado pelo cliente no formato:

```text
modo,tamanho_maximo
```

Exemplo:

```text
gbn,30
```

O servidor responde:

```text
Handshake OK | modo=gbn | tamanho_max=30 | janela=5
```

Depois do handshake, as mensagens sao enviadas em JSON, uma por linha. Cada pacote possui:

```json
{
  "tipo": "DADOS",
  "sequencia": 0,
  "total": 4,
  "conteudo": "test",
  "checksum": 192,
  "fim_lote": false,
  "fim_mensagem": false
}
```

O campo `conteudo` tem no maximo 4 caracteres.

As confirmacoes tambem sao enviadas em JSON:

```json
{
  "tipo": "ACK",
  "modo": "gbn",
  "sequencia": 3,
  "status": "ok"
}
```

## Modos

- `rs`: o servidor confirma cada pacote recebido.
- `gbn`: o servidor envia uma confirmacao cumulativa ao final de cada lote.

A janela inicial e definida pelo servidor com valor 5. Quando o cliente escolhe enviar pacote isolado, a janela usada fica com valor 1.

## Como executar

Primeiro, inicie o servidor:

```bash
python3 server.py
```

Depois, em outro terminal, inicie o cliente:

```bash
python3 client.py
```

No cliente:

1. escolha o modo `gbn` ou `rs`;
2. informe o tamanho maximo da mensagem, no minimo 30;
3. digite a mensagem;
4. escolha se deseja enviar em lote ou pacote por pacote.

Para encerrar, digite:

```text
sair
```

## Exemplo de uso

Cliente:

```text
Escolha o modo (gbn/rs): gbn
Digite o tamanho maximo da mensagem (minimo 30): 30
Resposta do servidor: Handshake OK | modo=gbn | tamanho_max=30 | janela=5
Digite a mensagem (ou 'sair' para encerrar): teste de redes
Enviar em lote? (s/n): s
Total de pacotes: 4
Pacote enviado | seq=0 | conteudo='test' | checksum=192
ACK recebido | modo=gbn | seq=3 | status=ok
```

Servidor:

```text
Servidor aguardando conexao na porta 2048...
Conectado a ('127.0.0.1', XXXXX)
Handshake recebido: gbn,30
Pacote recebido | seq=0 | total=4 | conteudo='test' | checksum=192
Mensagem completa: teste de redes
```

## O que ainda fica para a proxima entrega

Para a entrega final ainda falta simular erros e perdas de pacotes e fazer o comportamento correto de retransmissao.

## Uso de IA

Foi utilizada IA como apoio para interpretar o enunciado, revisar a organizacao do codigo e ajustar a documentacao. O grupo revisou o resultado antes da entrega.

## Equipe

- Artur Antunes
- Danilo Duleba
- Gabriel Pontes
- Gabriel Roma
- Joao Claudio Beltrao
- Kaique Alves
- Luca Albuquerque
- Luiz Flavius Veras
- Ricardo Machado
- Victor Uen
