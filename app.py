import socket
import threading
import time
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

UDP_IP = "127.0.0.1"   # Cambiar por IP del STM32
UDP_PORT_RX = 5005    # Puerto donde recibís nivel
UDP_PORT_TX = 5006    # Puerto donde enviás comandos
sock_rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_rx.bind((UDP_IP, UDP_PORT_RX))

sock_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

t0 = time.time()
nivel_data = []
time_data = []
def udp_listener():
    while True:
        data, _ = sock_rx.recvfrom(1024)
        try:
            nivel = float(data.decode())
            t = time.time() - t0

            nivel_data.append(nivel)
            time_data.append(t)

            if len(nivel_data) > 100:
                nivel_data.pop(0)
                time_data.pop(0)

            root.after(0, update_plot)

        except:
            pass

def send_control_mode():
    mode = control_mode.get()
    msg = f"MODE:{mode}".encode()
    sock_tx.sendto(msg, (UDP_IP, UDP_PORT_TX))
    status_label.config(text=f"Modo activo: {mode}")

def update_plot():
    line.set_data(time_data, nivel_data)
    ax.relim()
    ax.autoscale_view()
    canvas.draw_idle()

# ===============================
# Ventana principal
# ===============================
root = tk.Tk()
root.title("HydraFlow - Control de Nivel y Flujo")
root.geometry("900x600")
root.minsize(800, 500)
root.configure(bg="#EAF6FB")


# ===============================
# Variables globales
# ===============================
control_mode = tk.StringVar(value="PID")

# ===============================
style = ttk.Style()
style.theme_use("default")

style.configure(
    "Title.TLabel",
    font=("Segoe UI", 20, "bold")
)

style.configure(
    "Status.TLabel",
    font=("Segoe UI", 10),
    foreground="gray"
)

style.configure(
    "Main.TFrame",
    background="#EAF6FB"
)

style.configure(
    "Panel.TFrame",
    background="#D6EEF8",
    padding=20
)

style.configure(
    "Title.TLabel",
    font=("Segoe UI", 20, "bold"),
    background="#D6EEF8",
    foreground="#1F2D3D"
)

style.configure(
    "Text.TLabel",
    font=("Segoe UI", 12),
    background="#D6EEF8",
    foreground="#1F2D3D"
)

style.configure(
    "Status.TLabel",
    font=("Segoe UI", 10),
    background="#EAF6FB",
    foreground="#7FA0E0"
)

style.configure(
    "Control.TButton",
    font=("Segoe UI", 11),
    padding=8
)


# Contenedor principal

container = ttk.Frame(root, style="Main.TFrame")
container.pack(fill="both", expand=True)

container.grid_rowconfigure(0, weight=1)
container.grid_columnconfigure(0, weight=1)

# Diccionario de pantallas

frames = {}

def show_frame(name):
    frame = frames[name]
    frame.tkraise()
    status_label.config(text=f"Vista actual: {name}")

# ===============================
# Pantalla: Inicio
# ===============================
inicio = ttk.Frame(container)
inicio.grid(row=0, column=0, sticky="nsew")

panel_inicio = ttk.Frame(inicio, style="Panel.TFrame")
panel_inicio.pack(expand=True)

ttk.Label(
    panel_inicio,
    text="Pantalla de Inicio",
    style="Title.TLabel"
).pack(pady=(0, 10))

ttk.Label(
    panel_inicio,
    text="Monitoreo general de nivel y flujo",
    font=("Segoe UI", 12)
).pack()

frames["Inicio"] = inicio
# ----- Gráfica de nivel -----
fig = Figure(figsize=(6, 4), dpi=100)
ax = fig.add_subplot(111)

ax.set_title("Nivel del Tanque")
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Nivel [cm]")
ax.grid(True)

line, = ax.plot([], [], lw=2)
canvas = FigureCanvasTkAgg(fig, master=panel_inicio)
canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)

# ===============================
# Pantalla: Control
# ===============================
control = ttk.Frame(container)
control.grid(row=0, column=0, sticky="nsew")
panel_control = ttk.Frame(control, style="Panel.TFrame")
panel_control.pack(expand=True)


ttk.Label(
    panel_control,
    text="Pantalla de Control",
    style="Title.TLabel"
).pack(pady=(0, 10))

ttk.Label(
    panel_control,
    text="Modo de Control",
    style="Text.TLabel"
).pack(pady=(10, 5))

radio_pid = ttk.Radiobutton(
    panel_control,
    text="Control PID",
    variable=control_mode,
    value="PID",
    command=send_control_mode
)
radio_pid.pack(anchor="w", padx=20)

radio_mpc = ttk.Radiobutton(
    panel_control,
    text="Control MPC",
    variable=control_mode,
    value="MPC",
    command=send_control_mode
)
radio_mpc.pack(anchor="w", padx=20)


frames["Control"] = control

# ===============================
# Pantalla: Diagnóstico
# ===============================
diagnostico = ttk.Frame(container)
diagnostico.grid(row=0, column=0, sticky="nsew")

panel_diag = ttk.Frame(diagnostico, style="Panel.TFrame")
panel_diag.pack(expand=True)

ttk.Label(
    panel_diag,
    text="Monitoreo y Diagnóstico",
    style="Title.TLabel"
).pack(pady=(0, 10))

ttk.Label(
    panel_diag,
    text="Estado de conexión, errores y alarmas",
    font=("Segoe UI", 12)
).pack()

frames["Diagnóstico"] = diagnostico

# ===============================
# Menú superior
# ===============================
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

menu_vistas = tk.Menu(menu_bar, tearoff=0)
menu_vistas.add_command(label="Inicio", command=lambda: show_frame("Inicio"))
menu_vistas.add_command(label="Control", command=lambda: show_frame("Control"))
menu_vistas.add_command(label="Diagnóstico", command=lambda: show_frame("Diagnóstico"))
menu_bar.add_cascade(label="Vistas", menu=menu_vistas)

menu_bar.add_command(label="Salir", command=root.quit)

# ===============================
# Barra de estado inferior
# ===============================
status_bar = ttk.Frame(root, padding=(10, 5))
status_bar.pack(side="bottom", fill="x")

status_label = ttk.Label(
    status_bar,
    text="Vista actual: Inicio",
    style="Status.TLabel"
)
status_label.pack(side="left")

# ===============================
# Mostrar pantalla inicial
# ===============================
show_frame("Inicio")
thread = threading.Thread(target=udp_listener, daemon=True)
thread.start()

root.mainloop()
