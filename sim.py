import time
import threading
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

# ===============================
# Parámetros del sistema simulado
# ===============================
SP_MIN = 1.0
SP_MAX = 24.0
TOLERANCIA_SP = 0.5

DT = 0.1  # tiempo de muestreo [s]

# Planta (tanque)
k_u = 0.8      # ganancia del actuador
k_d = 0.15     # descarga natural

# PID
Kp = 1.8
Ki = 0.15
Kd = 0.6

# ===============================
# Variables de simulación
# ===============================
nivel = 5.0
u = 0.0
e_prev = 0.0
i_term = 0.0

t0 = time.time()
time_data = []
nivel_data = []
control_data = []

# ===============================
# Funciones de control
# ===============================
def pid_control(sp, y):
    global e_prev, i_term

    e = sp - y
    i_term += e * DT
    d = (e - e_prev) / DT

    u = Kp * e + Ki * i_term + Kd * d
    u = max(min(u, 10), -10)  # saturación

    e_prev = e
    return u

def simulate_step():
    global nivel, u

    sp = setpoint_var.get()

    if control_mode.get() == "PID":
        u = pid_control(sp, nivel)
    else:
        # Simulación simple de "Gain Scheduling"
        if abs(sp - nivel) < 1.5:
            u = pid_control(sp, nivel) * 0.5
        else:
            u = pid_control(sp, nivel)

    # Planta
    nivel_dot = k_u * u - k_d * nivel
    nivel += nivel_dot * DT

    nivel = max(0, nivel)

    t = time.time() - t0
    time_data.append(t)
    nivel_data.append(nivel)
    control_data.append(u)

    if len(time_data) > 200:
        time_data.pop(0)
        nivel_data.pop(0)
        control_data.pop(0)

    root.after(0, update_plot)

def simulation_loop():
    log_event("Simulación iniciada (modo virtual)")
    while True:
        simulate_step()
        time.sleep(DT)

# ===============================
# GUI
# ===============================
root = tk.Tk()
root.title("HydraFlow - Control de Nivel (Simulación)")
root.geometry("900x600")

control_mode = tk.StringVar(value="PID")
setpoint_var = tk.DoubleVar(value=5.0)

# ===============================
# Estilos
# ===============================
style = ttk.Style()
style.theme_use("default")

style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
style.configure("Text.TLabel", font=("Segoe UI", 12))
style.configure("OK.TLabel", foreground="green", font=("Segoe UI", 12, "bold"))
style.configure("WARN.TLabel", foreground="blue", font=("Segoe UI", 12, "bold"))
style.configure("ERR.TLabel", foreground="red", font=("Segoe UI", 12, "bold"))

# ===============================
# Layout
# ===============================
container = ttk.Frame(root)
container.pack(fill="both", expand=True)

frames = {}

def show_frame(name):
    frames[name].tkraise()
    status_label.config(text=f"Vista actual: {name}")

# ===============================
# Pantalla Inicio
# ===============================
inicio = ttk.Frame(container)
inicio.grid(row=0, column=0, sticky="nsew")
frames["Inicio"] = inicio

ttk.Label(inicio, text="Monitoreo del Nivel", style="Title.TLabel").pack(pady=10)

fig = Figure(figsize=(6, 4))
ax = fig.add_subplot(111)
ax_ctrl = ax.twinx()

ax.set_xlabel("Tiempo [s]")
ax.set_ylabel("Nivel [cm]")
ax_ctrl.set_ylabel("Control (u)")
ax.grid(True)

line, = ax.plot([], [], lw=2)
line_ctrl, = ax_ctrl.plot([], [], "r--", lw=2)

canvas = FigureCanvasTkAgg(fig, master=inicio)
canvas.get_tk_widget().pack(fill="both", expand=True)

sp_status_label = ttk.Label(inicio, text="Estado SP: --", style="Text.TLabel")
sp_status_label.pack()

control_label = ttk.Label(inicio, text="Control u: --", style="Text.TLabel")
control_label.pack()

# ===============================
# Pantalla Control
# ===============================
control = ttk.Frame(container)
control.grid(row=0, column=0, sticky="nsew")
frames["Control"] = control

ttk.Label(control, text="Control del Sistema", style="Title.TLabel").pack(pady=10)

ttk.Radiobutton(control, text="PID", variable=control_mode, value="PID").pack()
ttk.Radiobutton(control, text="PID + Gain Scheduling", variable=control_mode, value="MPC").pack()

ttk.Label(control, text="Setpoint [cm]").pack()
ttk.Entry(control, textvariable=setpoint_var, width=10).pack()

# ===============================
# Pantalla Diagnóstico
# ===============================
diagnostico = ttk.Frame(container)
diagnostico.grid(row=0, column=0, sticky="nsew")
frames["Diagnóstico"] = diagnostico

log_text = tk.Text(diagnostico, height=12, state="disabled")
log_text.pack(fill="both", expand=True)

# ===============================
# Funciones auxiliares
# ===============================
def log_event(msg):
    ts = time.strftime("%H:%M:%S")
    log_text.configure(state="normal")
    log_text.insert("end", f"[{ts}] {msg}\n")
    log_text.see("end")
    log_text.configure(state="disabled")

def update_plot():
    line.set_data(time_data, nivel_data)
    line_ctrl.set_data(time_data, control_data)

    ax.relim()
    ax.autoscale_view()
    ax_ctrl.relim()
    ax_ctrl.autoscale_view()

    canvas.draw_idle()

    if control_data:
        u_val = control_data[-1]
        sentido = "Llenado" if u_val > 0 else "Vaciado" if u_val < 0 else "Neutral"
        control_label.config(text=f"Control u: {u_val:.2f} ({sentido})")

    if nivel_data:
        error = abs(nivel_data[-1] - setpoint_var.get())
        if error <= TOLERANCIA_SP:
            sp_status_label.config(text="Estado SP: EN SETPOINT", style="OK.TLabel")
        elif error <= 2:
            sp_status_label.config(text="Estado SP: CERCA DEL SETPOINT", style="WARN.TLabel")
        else:
            sp_status_label.config(text="Estado SP: FUERA DE RANGO", style="ERR.TLabel")

# ===============================
# Menú
# ===============================
menu = tk.Menu(root)
root.config(menu=menu)

vistas = tk.Menu(menu, tearoff=0)
vistas.add_command(label="Inicio", command=lambda: show_frame("Inicio"))
vistas.add_command(label="Control", command=lambda: show_frame("Control"))
vistas.add_command(label="Diagnóstico", command=lambda: show_frame("Diagnóstico"))
menu.add_cascade(label="Sistema", menu=vistas)

status_label = ttk.Label(root, text="Vista actual: Inicio")
status_label.pack(side="bottom", fill="x")

# ===============================
# Inicio
# ===============================
show_frame("Inicio")
threading.Thread(target=simulation_loop, daemon=True).start()
root.mainloop()
