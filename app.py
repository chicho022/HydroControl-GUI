import socket
import threading
import time
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

#UDP_IP = "192.168.56.1"   # Cambiar por IP del STM32
UDP_PORT_RX = 5005    # Puerto donde recibís nivel
UDP_PORT_TX = 5006    # Puerto donde enviás comandos
UDP_IP_RX = "0.0.0.0"          # para bind (GUI escucha)
UDP_IP_TX = "192.168.1.12"     # IP DEL ESP32 o SIMULADOR
SP_MIN = 1.0   # cm
SP_MAX = 24.0  # cm
TOLERANCIA_SP = 0.5  # cm
sock_rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_rx.bind((UDP_IP_RX, UDP_PORT_RX))

sock_tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

t0 = time.time()
nivel_data = []
time_data = []
control_data = []


def send_control_mode():
    mode = control_mode.get()
    msg = f"MODE:{mode}".encode()
    sock_tx.sendto(msg, (UDP_IP_TX, UDP_PORT_TX))
    status_label.config(text=f"Modo activo: {mode}")
    log_event(f"Modo de control cambiado a {mode}")


def send_setpoint():
    try:
        sp = setpoint_var.get()

        # Validación de rango
        if sp < SP_MIN or sp > SP_MAX:
            status_label.config(
                text=f"Setpoint fuera de rango ({SP_MIN}–{SP_MAX} cm)"
            )
            return

        msg = f"SP:{sp:.2f}".encode()
        sock_tx.sendto(msg, (UDP_IP_TX, UDP_PORT_TX))
        status_label.config(text=f"Setpoint aplicado: {sp:.2f} cm")
        log_event(f"Setpoint enviado: {sp:.2f} cm")


    except tk.TclError:
        status_label.config(text="Setpoint inválido (no numérico)")
def udp_listener():
    log_event("Escuchando datos UDP...")
    while True:
        data, _ = sock_rx.recvfrom(1024)
        try:
            decoded = data.decode().strip()
            nivel, control = map(float, decoded.split(","))

            t = time.time() - t0

            nivel_data.append(nivel)
            control_data.append(control)
            time_data.append(t)

            if len(time_data) > 100:
                nivel_data.pop(0)
                control_data.pop(0)
                time_data.pop(0)

            root.after(0, update_plot)

        except:
            pass

def log_event(msg):
    timestamp = time.strftime("%H:%M:%S")
    log_text.configure(state="normal")
    log_text.insert("end", f"[{timestamp}] {msg}\n")
    log_text.see("end")
    log_text.configure(state="disabled")


def update_plot():
    line.set_data(time_data, nivel_data)
    line_ctrl.set_data(time_data, control_data)

    canvas.draw_idle()

    # Actualizar valor numérico del control
    if control_data:
        u = control_data[-1]

        if u > 0:
            sentido = "Llenado"
        elif u < 0:
            sentido = "Vaciado"
        else:
            sentido = "Neutral"

        control_label.config(
            text=f"Control u: {u:.1f}  ({sentido})"
        )
    if time_data:
        t_max = time_data[-1]

        if t_max > AX_T_WINDOW:
            ax.set_xlim(t_max - AX_T_WINDOW, t_max)
        else:
            ax.set_xlim(0, AX_T_WINDOW)

        # ----- Indicador de setpoint -----
        if nivel_data:
            nivel_actual = nivel_data[-1]
            sp = setpoint_var.get()
            error = abs(nivel_actual - sp)

            if error <= TOLERANCIA_SP:
                sp_status_label.config(
                    text="Estado SP: EN SETPOINT",
                    style="OK.TLabel"
                )

            elif error <= 2.0:
                sp_status_label.config(
                    text="Estado SP: CERCA DEL SETPOINT",
                    style="WARN.TLabel"
                )

            else:
                sp_status_label.config(
                    text="Estado SP: FUERA DE RANGO",
                    style="ERR.TLabel"
                )
                # ----- Nivel actual -----
        if nivel_data:
            nivel_actual = nivel_data[-1]
            nivel_label.config(
                text=f"Nivel actual: {nivel_actual:.2f} cm"
            )

        # ----- Setpoint actual -----
        sp = setpoint_var.get()
        sp_value_label.config(
            text=f"Setpoint: {sp:.2f} cm"
)

    



# ===============================
# Ventana principal
# ===============================
root = tk.Tk()
root.title("HydraFlow - Control de Nivel y Flujo")
root.geometry("900x600")
root.minsize(1000,800)
root.configure(bg="#E5E5E5")



# ===============================
# Variables globales
# ===============================
control_mode = tk.StringVar(value="PID")
setpoint_var = tk.DoubleVar(master=root, value=0.0)

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
    "Subtitle.TLabel",
    font=("Segoe UI", 13),
    background="#D6EEF8",
    foreground="#1F5E88"
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
style.configure(
    "OK.TLabel",
    font=("Segoe UI", 12, "bold"),
    foreground="#1B8A3D",  # verde
    background="#D6EEF8"
)
style.configure(
    "Value.TLabel",
    font=("Consolas", 12, "bold"),
    background="#D6EEF8",
    foreground="#0F3554"
)
style.configure(
    "WARN.TLabel",
    font=("Segoe UI", 12, "bold"),
    foreground="#1E88E5",  # celeste
    background="#D6EEF8"
)

style.configure(
    "ERR.TLabel",
    font=("Segoe UI", 12, "bold"),
    foreground="#C62828",  # rojo
    background="#D6EEF8"
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
panel_inicio.pack(expand=True, padx=40, pady=20)


ttk.Label(
    panel_inicio,
    text="Pantalla de Inicio",
    style="Title.TLabel"
).pack(pady=(0, 10))

ttk.Label(
    panel_inicio,
    text="Monitoreo general de nivel y flujo",
    style="Subtitle.TLabel"
).pack()
nivel_label = ttk.Label(
    panel_inicio,
    text="Nivel actual: -- cm",
    style="Value.TLabel"
)
nivel_label.pack(pady=(5, 0))

sp_value_label = ttk.Label(
    panel_inicio,
    text="Setpoint: -- cm",
    style="Value.TLabel"
)
sp_value_label.pack(pady=(5, 0))

frames["Inicio"] = inicio
# ----- Gráfica de nivel -----
fig = Figure(figsize=(8, 5), dpi=100)
ax = fig.add_subplot(111)
ax_ctrl = ax.twinx()
ax_ctrl.set_ylabel("Control (u)")
ax_ctrl.axhline(0, color="gray", linestyle=":", linewidth=1)
ax.set_facecolor("#F3FAFD")
ax_ctrl.set_facecolor("#F3FAFD")

ax.tick_params(colors="#1F2D3D")
ax_ctrl.tick_params(colors="#1F2D3D")

ax.spines["top"].set_visible(False)
ax_ctrl.spines["top"].set_visible(False)

# ===== Límites fijos =====
AX_T_WINDOW = 30        # segundos visibles en X
AX_NIVEL_MIN = 0
AX_NIVEL_MAX = 26       # un poco más que 24 cm
AX_CTRL_MIN = -255
AX_CTRL_MAX = 255

ax.set_ylim(AX_NIVEL_MIN, AX_NIVEL_MAX)
ax_ctrl.set_ylim(AX_CTRL_MIN, AX_CTRL_MAX)

ax.set_xlim(0, AX_T_WINDOW)

ax.set_title("Nivel del Tanque")
ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Nivel [cm]")
ax.grid(True)

line, = ax.plot([], [], lw=2)
line_ctrl, = ax_ctrl.plot(
    [], [],
    color="tab:red",
    linestyle="--",
    lw=2,
    label="Control (u)"
)
line.set_color("#0F3554")        # nivel
line_ctrl.set_color("#C62828")  # control
ax_ctrl.set_ylabel("Control (u)")
canvas = FigureCanvasTkAgg(fig, master=panel_inicio)
canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)


sp_status_label = ttk.Label(
    panel_inicio,
    text="Estado SP: --",
    style="Text.TLabel"
)
sp_status_label.pack(pady=(5, 0))

control_label = ttk.Label(
    panel_inicio,
    text="Control u: -- (Neutral)",
    style="Text.TLabel"
)
control_label.pack(pady=(5, 0))



# ===============================
# Pantalla: Control
# ===============================
control = ttk.Frame(container)
control.grid(row=0, column=0, sticky="nsew")
panel_control = ttk.Frame(control, style="Panel.TFrame")
panel_control.pack(expand=True, padx=40, pady=20)



ttk.Label(
    panel_control,
    text="Control del Sistema",
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
    text="Control + Gain Scheduling",
    variable=control_mode,
    value="MPC",
    command=send_control_mode
)
radio_mpc.pack(anchor="w", padx=20)

ttk.Label(
    panel_control,
    text="Setpoint de Nivel [cm]",
    style="Text.TLabel"
).pack(pady=(15, 5))

entry_sp = ttk.Entry(
    panel_control,
    textvariable=setpoint_var,
    width=10
)
entry_sp.pack()
ttk.Label(
    panel_control,
    text="Rango permitido: 1 – 24 cm",
    style="Text.TLabel"
).pack()

btn_sp = ttk.Button(
    panel_control,
    text="Enviar Setpoint",
    style="Control.TButton",
    command=send_setpoint
)
btn_sp.pack(pady=8)


frames["Control"] = control

# ===============================
# Pantalla: Diagnóstico
# ===============================
diagnostico = ttk.Frame(container)
diagnostico.grid(row=0, column=0, sticky="nsew")

panel_diag = ttk.Frame(diagnostico, style="Panel.TFrame")
log_text = tk.Text(
    panel_diag,
    height=12,
    width=70,
    state="disabled",
    wrap="word",
    bg="#FFFFFF",
    fg="#1F2D3D",
    font=("Consolas", 10)
)
log_text.pack(pady=10, fill="both", expand=True)
panel_diag.configure(style="Panel.TFrame")
panel_diag.pack(expand=True, padx=40, pady=20)


ttk.Label(
    panel_diag,
    text="Monitoreo y Diagnóstico",
    style="Title.TLabel"
).pack(pady=(0, 10))

ttk.Label(
    panel_diag,
    text="Estado de conexión, errores y alarmas",
    style="Subtitle.TLabel"
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
menu_bar.add_cascade(label="Sistema", menu=menu_vistas)
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
