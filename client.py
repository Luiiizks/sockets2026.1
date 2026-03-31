import socket

def escolher_modo():
    while True:
        modo = input("Escolha o modo (gbn/rs): ").strip().lower()
        if modo in ["gbn", "rs"]:
            return modo
        print("Modo inválido. Digite 'gbn' ou 'rs'.")

def escolher_tamanho():
    while True:
        try:
            tamanho = int(input("Digite o tamanho máximo da mensagem (mínimo 30): "))
            if tamanho >= 30:
                return tamanho
            print("O tamanho deve ser no mínimo 30.")
        except ValueError:
            print("Digite um número inteiro válido.")

def main():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(("localhost", 2048))

    modo = escolher_modo()
    tamanho = escolher_tamanho()

    handshake = f"{modo},{tamanho}"
    cliente.send(handshake.encode())

    resposta = cliente.recv(256).decode()
    print("Resposta do servidor:", resposta)

    cliente.close()

if __name__ == "__main__":
    main()