import socket


def obtener_puerto_disponible(preferido: int, intentos: int = 20) -> int:
    for puerto in range(preferido, preferido + intentos + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("0.0.0.0", puerto))
                return puerto
            except OSError:
                continue
    return preferido
