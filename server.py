import socket

def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(("localhost", 2048))
    servidor.listen(1)

    print("aguardando conexão na porta 2048...")
    conexao, addr = servidor.accept()
    print(f"Conectado a {addr}")

    dados = conexao.recv(256).decode().strip()
    print("Handshake recebido:", dados)

    try:
        modo, tamanho = dados.split(",")
        tamanho = int(tamanho)

        if modo not in ["gbn", "rs"]:
            resposta = "modo inválido."
        elif tamanho < 30:
            resposta = "Defina um limite maximo(no minimo 30)."
        else:
            resposta = f"Handshake OK | modo={modo} | tamanho_max={tamanho}"

    except:
        resposta = "Erro ao interpretar handshake."

    conexao.send(resposta.encode())
    conexao.close()
    servidor.close()

if __name__ == "__main__":
    main()