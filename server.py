import json
import socket


PORTA = 2048
JANELA_INICIAL = 5


def calcular_checksum(texto):
    return sum(texto.encode()) % 256


def enviar_json(conexao, dados):
    conexao.send((json.dumps(dados) + "\n").encode())


def enviar_ack(conexao, modo, sequencia, status):
    ack = {
        "tipo": "ACK",
        "modo": modo,
        "sequencia": sequencia,
        "status": status,
    }
    enviar_json(conexao, ack)


def reconstruir_mensagem(recebidos, total):
    if len(recebidos) != total:
        return None
    return "".join(recebidos[i] for i in range(total))


def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(("0.0.0.0", PORTA))
    servidor.listen(1)

    print(f"Servidor aguardando conexao na porta {PORTA}...")
    conexao, addr = servidor.accept()
    print(f"Conectado a {addr}")

    dados = conexao.recv(256).decode().strip()
    print("Handshake recebido:", dados)

    try:
        modo, tamanho = dados.split(",")
        tamanho = int(tamanho)

        if modo not in ["gbn", "rs"]:
            resposta = "Erro: modo invalido"
        elif tamanho < 30:
            resposta = "Erro: tamanho maximo deve ser no minimo 30"
        else:
            resposta = f"Handshake OK | modo={modo} | tamanho_max={tamanho} | janela={JANELA_INICIAL}"
    except ValueError:
        resposta = "Erro ao interpretar handshake"

    conexao.send(resposta.encode())

    if not resposta.startswith("Handshake OK"):
        conexao.close()
        servidor.close()
        return

    buffer = ""
    recebidos = {}
    esperado = 0

    while True:
        dados = conexao.recv(1024).decode()

        if not dados:
            print("Conexao encerrada pelo cliente.")
            break

        buffer += dados

        while "\n" in buffer:
            linha, buffer = buffer.split("\n", 1)

            if not linha.strip():
                continue

            pacote = json.loads(linha)

            if pacote["tipo"] == "ENCERRAR":
                print("Cliente encerrou a comunicacao.")
                conexao.close()
                servidor.close()
                return

            sequencia = pacote["sequencia"]
            conteudo = pacote["conteudo"]
            checksum = pacote["checksum"]
            total = pacote["total"]
            checksum_calculado = calcular_checksum(conteudo)

            print(
                f"Pacote recebido | seq={sequencia} | total={total} | "
                f"conteudo='{conteudo}' | checksum={checksum}"
            )

            if checksum != checksum_calculado:
                enviar_ack(conexao, modo, sequencia, "erro_checksum")
                continue

            if modo == "rs":
                recebidos[sequencia] = conteudo
                enviar_ack(conexao, modo, sequencia, "ok")

            elif modo == "gbn":
                if sequencia == esperado:
                    recebidos[sequencia] = conteudo
                    esperado += 1
                    status = "ok"
                else:
                    status = "fora_de_ordem"

                if pacote["fim_lote"] or pacote["fim_mensagem"]:
                    enviar_ack(conexao, modo, esperado - 1, status)

            if pacote["fim_mensagem"]:
                mensagem = reconstruir_mensagem(recebidos, total)

                if mensagem is not None:
                    print("Mensagem completa:", mensagem)
                else:
                    print("Mensagem incompleta.")

                recebidos = {}
                esperado = 0

    conexao.close()
    servidor.close()


if __name__ == "__main__":
    main()
