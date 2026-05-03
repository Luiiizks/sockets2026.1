import json
import socket


PORTA = 2048
TAMANHO_PAYLOAD = 4


def escolher_modo():
    while True:
        modo = input("Escolha o modo (gbn/rs): ").strip().lower()
        if modo in ["gbn", "rs"]:
            return modo
        print("Modo invalido. Digite 'gbn' ou 'rs'.")


def escolher_tamanho():
    while True:
        try:
            tamanho = int(input("Digite o tamanho maximo da mensagem (minimo 30): "))
            if tamanho >= 30:
                return tamanho
            print("O tamanho deve ser no minimo 30.")
        except ValueError:
            print("Digite um numero inteiro valido.")


def escolher_envio():
    escolha = input("Enviar em lote? (s/n): ").strip().lower()
    return escolha == "s"


def calcular_checksum(texto):
    return sum(texto.encode()) % 256


def criar_pacotes(mensagem, janela):
    pacotes = []
    partes = [mensagem[i:i + TAMANHO_PAYLOAD] for i in range(0, len(mensagem), TAMANHO_PAYLOAD)]

    for indice, parte in enumerate(partes):
        fim_lote = (indice + 1) % janela == 0 or indice == len(partes) - 1
        pacote = {
            "tipo": "DADOS",
            "sequencia": indice,
            "total": len(partes),
            "conteudo": parte,
            "checksum": calcular_checksum(parte),
            "fim_lote": fim_lote,
            "fim_mensagem": indice == len(partes) - 1,
        }
        pacotes.append(pacote)

    return pacotes


def enviar_json(conexao, dados):
    conexao.send((json.dumps(dados) + "\n").encode())


def receber_linha(conexao, buffer):
    while "\n" not in buffer:
        recebido = conexao.recv(1024).decode()
        if not recebido:
            return None, buffer
        buffer += recebido

    linha, buffer = buffer.split("\n", 1)
    return linha, buffer


def enviar_mensagem(cliente, modo, tamanho_maximo, janela_servidor):
    mensagem = input("Digite a mensagem (ou 'sair' para encerrar): ")

    if mensagem.strip().lower() == "sair":
        enviar_json(cliente, {"tipo": "ENCERRAR"})
        return False

    while not mensagem or len(mensagem) > tamanho_maximo:
        if not mensagem:
            print("A mensagem nao pode ser vazia.")
        else:
            print(f"A mensagem tem {len(mensagem)} caracteres. O limite e {tamanho_maximo}.")
        mensagem = input("Digite a mensagem novamente: ")

    usar_lote = escolher_envio()
    janela = janela_servidor if usar_lote else 1
    pacotes = criar_pacotes(mensagem, janela)
    buffer = ""
    indice = 0

    print(f"Total de pacotes: {len(pacotes)}")

    while indice < len(pacotes):
        lote = pacotes[indice:indice + janela]

        for pacote in lote:
            enviar_json(cliente, pacote)
            print(
                f"Pacote enviado | seq={pacote['sequencia']} | "
                f"conteudo='{pacote['conteudo']}' | checksum={pacote['checksum']}"
            )

        quantidade_acks = len(lote) if modo == "rs" else 1

        for _ in range(quantidade_acks):
            linha, buffer = receber_linha(cliente, buffer)
            if linha is None:
                print("Conexao encerrada pelo servidor.")
                return False

            ack = json.loads(linha)
            print(
                f"ACK recebido | modo={ack['modo']} | "
                f"seq={ack['sequencia']} | status={ack['status']}"
            )

        indice += janela

    return True


def main():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(("localhost", PORTA))

    modo = escolher_modo()
    tamanho = escolher_tamanho()

    cliente.send(f"{modo},{tamanho}".encode())
    resposta = cliente.recv(256).decode().strip()
    print("Resposta do servidor:", resposta)

    if not resposta.startswith("Handshake OK"):
        cliente.close()
        return

    janela_servidor = int(resposta.split("janela=")[1])

    while enviar_mensagem(cliente, modo, tamanho, janela_servidor):
        print()

    cliente.close()


if __name__ == "__main__":
    main()
