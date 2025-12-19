# HydraFlow – Interfaz Gráfica de Control de Nivel y Flujo

## Descripción general

**HydraFlow** es una interfaz gráfica desarrollada en **Python** utilizando **Tkinter (programación orientada a objetos)** y **Matplotlib**, diseñada para el monitoreo y control en tiempo real de un sistema de control de nivel de tanque.

El sistema utiliza un **controlador PID** y un **PID con Gain Scheduling**, implementados en un **STM32**, con un **ESP32** actuando como pasarela de comunicación entre la GUI y el sistema embebido mediante **UDP** y **UART**.

La interfaz permite:
- Visualizar el nivel del tanque en tiempo real
- Visualizar la señal de control aplicada
- Modificar el setpoint del sistema
- Cambiar el modo de control
- Monitorear el estado del sistema y eventos de diagnóstico

Proyecto desarrollado en el contexto de la materia **Sistemas Embebidos**.

---

## Arquitectura del sistema

PC (GUI - Python)
│
│ UDP
▼
ESP32 (Gateway de red)
│
│ UART
▼
STM32 (Control PID / Gain Scheduling)


---

## Requisitos del sistema

### Software
- Python 3.9 o superior
- Windows o Linux

### Librerías necesarias
```bash
pip install matplotlib

Funcionalidades de la GUI
Pantalla de Inicio

Gráfica en tiempo real con:

Nivel del tanque [cm]

Señal de control u

Ejes fijos para facilitar análisis visual

Indicador de estado del setpoint:

EN SETPOINT (±0.5 cm)

CERCA DEL SETPOINT

FUERA DE RANGO

Visualización numérica:

Nivel actual

Señal de control con signo

Sentido de actuación:

Llenado

Vaciado

Neutral

Pantalla de Control

Selección del modo de control:

PID

PID + Gain Scheduling

Ingreso de setpoint:

Rango permitido: 1 – 24 cm

Envío del setpoint al sistema en tiempo real

COMUNICACION UDP
UDP_IP_RX = "0.0.0.0"        # La GUI escucha en todas las interfaces
UDP_PORT_RX = 5005           # Puerto de recepción
UDP_IP_TX = "192.168.1.12"   # IP del ESP32
UDP_PORT_TX = 5006           # Puerto de envío

Formato de datos recibidos

Los datos enviados desde el ESP32 hacia la GUI tienen el formato:

Formato de datos recibidos

Los datos enviados desde el ESP32 hacia la GUI tienen el formato:

Manual de uso
1. Preparación del sistema

Encender el STM32 y el ESP32

Conectar ambos dispositivos a la misma red WiFi

Verificar la IP asignada al ESP32

Configurar dicha IP en la variable UDP_IP_TX de la GUI

2. Ejecución de la interfaz

3. Control del sistema

Ir al menú Sistema → Control

Seleccionar el modo de control deseado

Introducir el setpoint (entre 1 y 24 cm)

Presionar Enviar Setpoint

4. Monitoreo en tiempo real
Ir a Pantalla de Inicio

Observar:

Evolución del nivel del tanque

Señal de control aplicada

Estado del setpoint

5. Diagnóstico

Ir a Sistema → Diagnóstico

Revisar:

Estado de conexión

Eventos del sistema

Confirmación de comandos enviados


