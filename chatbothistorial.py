import json
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
from nltk.chat.util import Chat, reflections

#Archivo donde se guarda el historial
HISTORIAL_FILE = "historial.json"

#Definir patrones y respuestas del chatbot
patterns_responses = [
    (r'hello|hi|hey|hola|que tal|qué tal|buenos dias|buenos días|buenas tardes|buenas noches', ['¡Hola! ¿Cómo puedo ayudarte hoy?']),
    (r'mondongo', ['mondongo tu']),
    (r'how are you', ['I am just a bot, but I am doing fine!']),
    (r'what is your name', ['I am a chatbot created with NLTK.']),
    (r'quit|exit', ['Goodbye! Have a great day!']),
    (r'(.*) your (.*)', ['Why do you want to know about my {1}?'])
]

chatbot = Chat(patterns_responses, reflections)

#Cargar historial desde JSON
def cargar_historial():
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

#Guardar historial en JSON
def guardar_historial(historial):
    with open(HISTORIAL_FILE, "w", encoding="utf-8") as file:
        json.dump(historial, file, indent=4, ensure_ascii=False)

#Verifica si el usuario existe y muestra su historial
def iniciar_sesion():
    nombre = entry_nombre.get().strip()
    if not nombre:
        messagebox.showwarning("Error", "Por favor, ingrese su nombre")
        return

    historial = cargar_historial()
    if nombre not in historial:
        historial[nombre] = []  #Crear historial vacío para nuevos usuarios
        guardar_historial(historial)

    ventana_login.destroy()  #Cerrar la ventana de login
    mostrar_chat(nombre, historial)

#Ventana de historial
def mostrar_historial(nombre, historial):
    ventana_historial = tk.Toplevel()
    ventana_historial.title(f"Historial de {nombre}")
    ventana_historial.geometry("400x400")
    ventana_historial.configure(bg="#2C3E50")

    historial_text = scrolledtext.ScrolledText(ventana_historial, wrap=tk.WORD, width=50, height=20, bg="#ECF0F1", fg="#2C3E50", font=("Arial", 10))
    historial_text.pack(padx=10, pady=10)
    historial_text.insert(tk.END, "\n".join(historial[nombre]) + "\n")  #Cargar historial completo
    historial_text.config(state=tk.DISABLED)

#Eliminar historial de usuario
def borrar_historial(nombre, historial, chat_text):
    if messagebox.askyesno("Borrar Historial", "¿Estás seguro de que quieres borrar tu historial?"):
        historial[nombre] = []
        guardar_historial(historial)
        chat_text.config(state=tk.NORMAL)
        chat_text.delete(1.0, tk.END)
        chat_text.config(state=tk.DISABLED)
        messagebox.showinfo("Historial Borrado", "Tu historial ha sido eliminado correctamente.")

#Interfaz de chat con historial
def mostrar_chat(nombre, historial):
    ventana_chat = tk.Tk()
    ventana_chat.title(f"Chat de {nombre}")
    ventana_chat.geometry("400x500")
    ventana_chat.configure(bg="#2C3E50")

    chat_text = scrolledtext.ScrolledText(ventana_chat, wrap=tk.WORD, width=50, height=15, bg="#ECF0F1", fg="#2C3E50", font=("Arial", 10))
    chat_text.pack(padx=10, pady=10)
    chat_text.insert(tk.END, "\n".join(historial[nombre]) + "\n")  #Cargar historial reciente
    chat_text.config(state=tk.DISABLED)

    entrada_texto = tk.Entry(ventana_chat, width=40, font=("Arial", 10), bg="#ECF0F1", fg="#2C3E50")
    entrada_texto.pack(pady=5)

    def enviar_mensaje():
        mensaje = entrada_texto.get().strip()
        if mensaje:
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            chat_text.config(state=tk.NORMAL)
            chat_text.insert(tk.END, f"\n{timestamp} You: {mensaje}\n")
            chat_text.config(state=tk.DISABLED)

            respuesta = chatbot.respond(mensaje.lower())
            if respuesta:
                chat_text.config(state=tk.NORMAL)
                chat_text.insert(tk.END, f"{timestamp} SerraBot: {respuesta}\n")
                chat_text.config(state=tk.DISABLED)
                historial[nombre].append(f"{timestamp} You: {mensaje}")
                historial[nombre].append(f"{timestamp} SerraBot: {respuesta}")
                guardar_historial(historial)

            entrada_texto.delete(0, tk.END)

    boton_enviar = tk.Button(ventana_chat, text="Enviar", command=enviar_mensaje, bg="#3498DB", fg="white", font=("Arial", 10, "bold"))
    boton_enviar.pack(pady=5)

    boton_historial = tk.Button(ventana_chat, text="Ver Historial Completo", command=lambda: mostrar_historial(nombre, historial), bg="#E74C3C", fg="white", font=("Arial", 10, "bold"))
    boton_historial.pack(pady=5)

    boton_borrar = tk.Button(ventana_chat, text="Borrar Historial", command=lambda: borrar_historial(nombre, historial, chat_text), bg="#C0392B", fg="white", font=("Arial", 10, "bold"))
    boton_borrar.pack(pady=5)

    ventana_chat.mainloop()

#Ventana de inicio de sesión
ventana_login = tk.Tk()
ventana_login.title("Inicio de Sesión")
ventana_login.geometry("450x350")
ventana_login.configure(bg="#2C3E50")

tk.Label(ventana_login, text="Bienvenido a SerraBot", fg="white", bg="#2C3E50", font=("Arial", 12, "bold")).pack(pady=10)
tk.Label(ventana_login, text="Ingrese su nombre:", fg="white", bg="#2C3E50", font=("Arial", 12, "bold")).pack(pady=10)
entry_nombre = tk.Entry(ventana_login, font=("Arial", 10), bg="#ECF0F1", fg="#2C3E50")
entry_nombre.pack()


btn_ingresar = tk.Button(ventana_login, text="Acceder al chat", command=iniciar_sesion, bg="#27AE60", fg="white", font=("Arial", 10, "bold"))
btn_ingresar.pack(pady=10)

ventana_login.mainloop()
