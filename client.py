import json
import socket


PORTA = 2048
TAMANHO_PAYLOAD = 4
TIMEOUT = 2.5
CHAVE = "redes"


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


def escolher_pacote(texto, total):
    while True:
        try:
            pacote = int(input(texto))
            if pacote == -1 or 0 <= pacote < total:
                return pacote
            print("Informe -1 ou um numero de pacote valido.")
        except ValueError:
            print("Digite um numero inteiro.")


def escolher_falhas(total):
    simular = input("Simular erro/perda? (s/n): ").strip().lower()

    if simular != "s":
        return -1, -1

    erro = escolher_pacote("Pacote com erro de integridade (-1 para nenhum): ", total)
    perda = escolher_pacote("Pacote perdido uma vez (-1 para nenhum): ", total)
    return erro, perda


def calcular_checksum(texto):
    return sum(texto.encode()) % 256


def criptografar(texto):
    texto_bytes = texto.encode()
    chave_bytes = CHAVE.encode()
    cifrado = bytes(
        texto_bytes[i] ^ chave_bytes[i % len(chave_bytes)]
        for i in range(len(texto_bytes))
    )
    return cifrado.hex()


def criar_pacotes(mensagem, janela):
    pacotes = []
    partes = [mensagem[i:i + TAMANHO_PAYLOAD] for i in range(0, len(mensagem), TAMANHO_PAYLOAD)]

    for indice, parte in enumerate(partes):
        fim_lote = (indice + 1) % janela == 0 or indice == len(partes) - 1
        pacote = {
            "tipo": "DADOS",
            "sequencia": indice,
            "total": len(partes),
            "conteudo": criptografar(parte),
            "checksum": calcular_checksum(parte),
            "tamanho": len(parte),
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


def enviar_pacote(cliente, pacote, erro, perda, tentativas):
    sequencia = pacote["sequencia"]

    if sequencia == perda and tentativas[sequencia] == 0:
        tentativas[sequencia] += 1
        print(f"Perda simulada | seq={sequencia}")
        return

    pacote_envio = pacote.copy()

    if sequencia == erro and tentativas[sequencia] == 0:
        pacote_envio["conteudo"] = criptografar("#" * pacote["tamanho"])
        print(f"Erro simulado | seq={sequencia}")

    enviar_json(cliente, pacote_envio)
    tentativas[sequencia] += 1

    print(
        f"Pacote enviado | seq={sequencia} | "
        f"checksum={pacote['checksum']} | tentativa={tentativas[sequencia]}"
    )


def enviar_gbn(cliente, pacotes, janela, erro, perda):
    base = 0
    buffer = ""
    tentativas = [0] * len(pacotes)

    while base < len(pacotes):
        fim = min(base + janela, len(pacotes))

        for indice in range(base, fim):
            enviar_pacote(cliente, pacotes[indice], erro, perda, tentativas)

        try:
            linha, buffer = receber_linha(cliente, buffer)
        except socket.timeout:
            print(f"Timeout | reenviando a partir do pacote {base}")
            continue

        if linha is None:
            return False

        resposta = json.loads(linha)
        print(
            f"{resposta['tipo']} recebido | modo={resposta['modo']} | "
            f"seq={resposta['sequencia']} | status={resposta['status']}"
        )

        if resposta["tipo"] == "ACK":
            base = resposta["sequencia"] + 1
        else:
            base = resposta["sequencia"]

    return True


def enviar_rs(cliente, pacotes, janela, erro, perda):
    pendentes = set(range(len(pacotes)))
    buffer = ""
    tentativas = [0] * len(pacotes)

    while pendentes:
        inicio = min(pendentes)
        janela_atual = [
            indice
            for indice in range(inicio, min(inicio + janela, len(pacotes)))
            if indice in pendentes
        ]
        esperando = set(janela_atual)

        for indice in janela_atual:
            enviar_pacote(cliente, pacotes[indice], erro, perda, tentativas)

        while esperando:
            try:
                linha, buffer = receber_linha(cliente, buffer)
            except socket.timeout:
                print("Timeout | reenviando pacotes pendentes da janela")
                break

            if linha is None:
                return False

            resposta = json.loads(linha)
            sequencia = resposta["sequencia"]

            print(
                f"{resposta['tipo']} recebido | modo={resposta['modo']} | "
                f"seq={sequencia} | status={resposta['status']}"
            )

            if resposta["tipo"] == "ACK" and sequencia in pendentes:
                pendentes.remove(sequencia)

            if sequencia in esperando:
                esperando.remove(sequencia)

    return True


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

    print(f"Total de pacotes: {len(pacotes)}")
    erro, perda = escolher_falhas(len(pacotes))
    cliente.settimeout(TIMEOUT)

    if modo == "gbn":
        return enviar_gbn(cliente, pacotes, janela, erro, perda)

    return enviar_rs(cliente, pacotes, janela, erro, perda)


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
