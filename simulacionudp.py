import socket
import time
import math

UDP_IP = "127.0.0.1"
UDP_PORT_GUI = 5005     # GUI recibe aquí
UDP_PORT_CMD = 5006     # GUI envía SP y modo

sock_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_rx.bind((UDP_IP, UDP_PORT_CMD))
sock_rx.setblocking(False)

# ===============================
# Variables del sistema
# ===============================
nivel = 5.0          # cm
u = 0.0              # control
sp = 10.0            # setpoint
modo = "PID"

dt = 0.1             # 10 Hz
tau = 4.0            # constante del tanque
k = 0.8              # ganancia del actuador

# PID simple
Kp = 2.0
Ki = 0.4
Kd = 0.2
e_prev = 0.0
i_term = 0.0

print("Simulador UDP iniciado")

while True:
    # ===============================
    # Leer comandos de la GUI
    # ===============================
    try:
        data, _ = sock_rx.recvfrom(1024)
        msg = data.decode()

        if msg.startswith("SP:"):
            sp = float(msg.split(":")[1])
            print(f"Nuevo SP: {sp}")

        elif msg.startswith("MODE:"):
            modo = msg.split(":")[1]
            print(f"Modo: {modo}")

    except:
        pass

    # ===============================
    # Control
    # ===============================
    e = sp - nivel
    i_term += e * dt
    d = (e - e_prev) / dt
    e_prev = e

    if modo == "PID":
        u = Kp * e + Ki * i_term + Kd * d
    else:
        u = 1.5 * e  # "otro controlador" simulado

    # Saturación
    u = max(min(u, 10), -10)

    # ===============================
    # Dinámica del tanque (1er orden)
    # ===============================
    nivel += dt * (-nivel / tau + k * u)
    nivel = max(nivel, 0)

    # ===============================
    # Enviar a la GUI
    # ===============================
    msg = f"{nivel:.2f},{u:.2f}"
    sock_tx.sendto(msg.encode(), (UDP_IP, UDP_PORT_GUI))

    time.sleep(dt)
