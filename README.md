# Projeto de Comunicacao via Sockets

Trabalho pratico da disciplina de Infraestrutura de Redes e Comunicacao.

A aplicacao usa sockets TCP em Python para fazer a comunicacao entre cliente e servidor. Nesta entrega final, o sistema envia mensagens em pacotes, confirma o recebimento e consegue simular erro e perda para testar a retransmissao.

## Objetivo da entrega final

Nesta etapa foram implementados:

1. conexao entre cliente e servidor via socket;
2. handshake inicial com modo de operacao e tamanho maximo da mensagem;
3. envio de mensagens divididas em pacotes de ate 4 caracteres;
4. numero de sequencia em cada pacote;
5. checksum para verificar integridade;
6. ACK para confirmar pacote recebido corretamente;
7. ERRO para avisar pacote com problema;
8. temporizador no cliente;
9. retransmissao quando ocorre erro ou perda;
10. janela de envio com valor inicial 5, definida pelo servidor;
11. simulacao deterministica de erro e perda escolhida no cliente;
12. criptografia simetrica simples na troca das mensagens.

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
4. escolha se deseja enviar em lote;
5. escolha se deseja simular erro ou perda.

Para encerrar, digite:

```text
sair
```

## Modos

- `gbn`: usa confirmacao cumulativa. Quando ocorre erro ou perda, o cliente reenvia a partir do pacote com problema.
- `rs`: usa repeticao seletiva. Quando ocorre erro ou perda, o cliente reenvia apenas os pacotes pendentes.

## Protocolo usado

O handshake e enviado assim:

```text
modo,tamanho_maximo
```

Exemplo:

```text
gbn,30
```

Resposta do servidor:

```text
Handshake OK | modo=gbn | tamanho_max=30 | janela=5
```

Depois do handshake, os pacotes sao enviados em JSON, um por linha.

Exemplo de pacote:

```json
{
  "tipo": "DADOS",
  "sequencia": 0,
  "total": 3,
  "conteudo": "06001107",
  "checksum": 192,
  "tamanho": 4,
  "fim_lote": false,
  "fim_mensagem": false
}
```

O campo `conteudo` vai criptografado. O servidor descriptografa, confere o checksum e envia `ACK` ou `ERRO`.

Exemplo de resposta:

```json
{
  "tipo": "ACK",
  "modo": "gbn",
  "sequencia": 2,
  "status": "ok"
}
```

## Simulacao de falhas

Depois de digitar a mensagem, o cliente pergunta:

```text
Simular erro/perda? (s/n):
```

Se responder `s`, escolha o numero do pacote que deve ter erro e o numero do pacote que deve ser perdido uma vez.

Use `-1` quando nao quiser simular uma das falhas.

Exemplo:

```text
Pacote com erro de integridade (-1 para nenhum): 1
Pacote perdido uma vez (-1 para nenhum): -1
```

Nesse caso, o pacote 1 sera enviado errado na primeira tentativa. O servidor responde `ERRO` e o cliente retransmite.

## Pontos extras

Foram implementados:

- checksum para checagem de integridade;
- criptografia simetrica simples usando uma chave compartilhada no cliente e no servidor.

## Exemplo de uso

Cliente:

```text
Escolha o modo (gbn/rs): gbn
Digite o tamanho maximo da mensagem (minimo 30): 30
Resposta do servidor: Handshake OK | modo=gbn | tamanho_max=30 | janela=5
Digite a mensagem (ou 'sair' para encerrar): teste final
Enviar em lote? (s/n): s
Total de pacotes: 3
Simular erro/perda? (s/n): s
Pacote com erro de integridade (-1 para nenhum): 1
Pacote perdido uma vez (-1 para nenhum): -1
Pacote enviado | seq=0 | checksum=192 | tentativa=1
Erro simulado | seq=1
Pacote enviado | seq=1 | checksum=84 | tentativa=1
Pacote enviado | seq=2 | checksum=59 | tentativa=1
ERRO recebido | modo=gbn | seq=1 | status=checksum
Pacote enviado | seq=1 | checksum=84 | tentativa=2
Pacote enviado | seq=2 | checksum=59 | tentativa=2
ACK recebido | modo=gbn | seq=2 | status=ok
```

Servidor:

```text
Servidor aguardando conexao na porta 2048...
Conectado a ('127.0.0.1', XXXXX)
Handshake recebido: gbn,30
Pacote recebido | seq=0 | total=3 | conteudo='test' | checksum=192
Pacote recebido | seq=1 | total=3 | conteudo='####' | checksum=84
Pacote recebido | seq=2 | total=3 | conteudo='nal' | checksum=59
Pacote recebido | seq=1 | total=3 | conteudo='e fi' | checksum=84
Pacote recebido | seq=2 | total=3 | conteudo='nal' | checksum=59
Mensagem completa: teste final
```

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
