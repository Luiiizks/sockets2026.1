import json
import socket


PORTA = 2048
JANELA_INICIAL = 5
CHAVE = "redes"


def calcular_checksum(texto):
    return sum(texto.encode()) % 256


def descriptografar(texto):
    dados = bytes.fromhex(texto)
    chave_bytes = CHAVE.encode()
    original = bytes(
        dados[i] ^ chave_bytes[i % len(chave_bytes)]
        for i in range(len(dados))
    )
    return original.decode()


def enviar_json(conexao, dados):
    conexao.send((json.dumps(dados) + "\n").encode())


def enviar_resposta(conexao, tipo, modo, sequencia, status):
    resposta = {
        "tipo": tipo,
        "modo": modo,
        "sequencia": sequencia,
        "status": status,
    }
    enviar_json(conexao, resposta)


def reconstruir_mensagem(recebidos, total):
    if total is None or len(recebidos) != total:
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
    total_mensagem = None
    aguardando_reenvio = False

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
            checksum = pacote["checksum"]
            total = pacote["total"]
            total_mensagem = total

            try:
                conteudo = descriptografar(pacote["conteudo"])
            except Exception:
                conteudo = ""

            checksum_calculado = calcular_checksum(conteudo)

            print(
                f"Pacote recebido | seq={sequencia} | total={total} | "
                f"conteudo='{conteudo}' | checksum={checksum}"
            )

            if modo == "gbn" and aguardando_reenvio:
                if pacote["fim_lote"] or pacote["fim_mensagem"]:
                    aguardando_reenvio = False
                continue

            if checksum != checksum_calculado:
                enviar_resposta(conexao, "ERRO", modo, sequencia, "checksum")
                if modo == "gbn" and not (pacote["fim_lote"] or pacote["fim_mensagem"]):
                    aguardando_reenvio = True
                continue

            if modo == "rs":
                recebidos[sequencia] = conteudo
                enviar_resposta(conexao, "ACK", modo, sequencia, "ok")

            elif modo == "gbn":
                if sequencia < esperado:
                    if pacote["fim_lote"] or pacote["fim_mensagem"]:
                        enviar_resposta(conexao, "ACK", modo, esperado - 1, "ok")
                elif sequencia == esperado:
                    recebidos[sequencia] = conteudo
                    esperado += 1

                    if pacote["fim_lote"] or pacote["fim_mensagem"]:
                        enviar_resposta(conexao, "ACK", modo, esperado - 1, "ok")
                else:
                    enviar_resposta(conexao, "ERRO", modo, esperado, "fora_de_ordem")
                    if not (pacote["fim_lote"] or pacote["fim_mensagem"]):
                        aguardando_reenvio = True

            mensagem = reconstruir_mensagem(recebidos, total_mensagem)

            if mensagem is not None:
                print("Mensagem completa:", mensagem)
                recebidos = {}
                esperado = 0
                total_mensagem = None
                aguardando_reenvio = False

    conexao.close()
    servidor.close()


if __name__ == "__main__":
    main()
