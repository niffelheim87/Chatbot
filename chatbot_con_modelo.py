import nltk
import json
import numpy as np
import random
import os
import re
import unicodedata
from sklearn.preprocessing import LabelEncoder
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime

# Archivo donde se guarda el historial
HISTORIAL_FILE = "historial.json"

# Descargar recursos de NLTK
nltk.download('punkt_tab')
nltk.download('wordnet')

# Cargar el modelo
model = load_model("chatbot_model_que_funciona_bak.h5")  # Cambia "chatbot_model_que_funciona_bak.h5" por tu archivo de modelo real

# Cargar los datos de intenciones
intents = json.load(open('output.json'))  # Cambia 'output.json' por tu archivo real

# Inicializar el lematizador y el codificador de etiquetas
lemmatizer = WordNetLemmatizer()
le = LabelEncoder()

# Preprocesar los datos de entrada para la predicción
words = []  # Lista de todas las palabras que aparecerán en los patrones
classes = []  # Lista de las clases (intenciones)
documents = []  # Lista de tuplas (patrón, intención)
ignore_words = ['el', 'la', 'de', 'y', 'a', 'que', 'en', 'los', 'las', 'por']

# Tokenización y lematización de los patrones
for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((pattern, intent['tag']))

    classes.append(intent['tag'])

# Normalización de palabras
words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))

# Codificar las clases (intenciones) con LabelEncoder
classes = sorted(list(set(classes)))
le.fit(classes)

# Imprimir el tamaño de 'words'
print(f"Longitud de 'words': {len(words)}")

# Función para preprocesar el texto de entrada
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)  # Tokeniza la entrada
    sentence_words = [lemmatizer.lemmatize(w.lower()) for w in sentence_words]  # Lematiza
    return sentence_words

# Función para convertir la entrada en un vector de "bolsa de palabras"
def bow(sentence, words, expected_length, show_details=True):
    sentence_words = clean_up_sentence(sentence)  # Tokenize the sentence
    bag = [0] * expected_length  # Initialize the bag with the expected length

    # Populate the bag of words vector
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1

    # Return the bag of words vector
    return np.array(bag)


# Asegúrate de que 'words' tenga el tamaño adecuado
print(f"Longitud de 'words': {len(words)}")




# Función para predecir la clase de la entrada
def predict_class(text, model, expected_length=154):
    p = bow(text, words, expected_length, show_details=False)
    return model.predict(np.array([p]))[0]


# Función para obtener la respuesta basada en la predicción
def getResponse(ints, intents_json):
    try:
        tag = le.inverse_transform([np.argmax(ints)])[0]
    except IndexError:
        return "Lo siento, no entendí eso."
    
    for intent in intents_json['intents']:
        if intent['tag'] == tag:
            return random.choice(intent['responses'])
    
    return "Lo siento, no tengo una respuesta para eso."

# Función principal para la respuesta del chatbot
def chatbot_response(text):
    ints = predict_class(text, model)  # Predice la intención
    res = getResponse(ints, intents)  # Obtiene la respuesta correspondiente
    return res

# Normalizar texto para mejorar la coincidencia de patrones
def normalizar_texto(texto):
    texto = texto.lower()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')  # Elimina tildes
    return texto

# Leer JSON y generar patrones y respuestas
def leer_json_y_generar_patrones_respuestas(ruta_archivo):
    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        data = json.load(archivo)
    
    patrones_respuestas = []
    patrones_unificados = {}

    for intent in data['intents']:
        patterns = intent['patterns']
        responses = intent['responses']
        
        patterns_normalizados = [normalizar_texto(p) for p in patterns]
        regex_pattern = r'\b(' + '|'.join(map(re.escape, patterns_normalizados)) + r')\b'
        
        if regex_pattern in patrones_unificados:
            patrones_unificados[regex_pattern].extend(responses)
        else:
            patrones_unificados[regex_pattern] = responses

    for pattern, responses in patrones_unificados.items():
        patrones_respuestas.append((pattern, responses))

    return patrones_respuestas

# Cargar historial desde JSON
def cargar_historial():
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

# Guardar historial en JSON
def guardar_historial(historial):
    with open(HISTORIAL_FILE, "w", encoding="utf-8") as file:
        json.dump(historial, file, indent=4, ensure_ascii=False)

# Función para iniciar sesión
def iniciar_sesion():
    nombre = entry_nombre.get().strip()
    if not nombre:
        messagebox.showwarning("Error", "Por favor, ingrese su nombre")
        return

    historial = cargar_historial()
    if nombre not in historial:
        historial[nombre] = []  # Crear historial vacío para nuevos usuarios
        guardar_historial(historial)

    ventana_login.destroy()  # Cerrar la ventana de login
    mostrar_chat(nombre, historial)

# Mostrar historial de usuario
def mostrar_historial(nombre, historial):
    ventana_historial = tk.Toplevel()
    ventana_historial.title(f"Historial de {nombre}")
    ventana_historial.geometry("400x400")
    ventana_historial.configure(bg="#2C3E50")

    historial_text = scrolledtext.ScrolledText(ventana_historial, wrap=tk.WORD, width=50, height=20, bg="#ECF0F1", fg="#2C3E50", font=("Arial", 10))
    historial_text.pack(padx=10, pady=10)
    historial_text.insert(tk.END, "\n".join(historial[nombre]) + "\n")
    historial_text.config(state=tk.DISABLED)

# Eliminar historial de usuario
def borrar_historial(nombre, historial, chat_text):
    if messagebox.askyesno("Borrar Historial", "¿Estás seguro de que quieres borrar tu historial?"):
        historial[nombre] = []
        guardar_historial(historial)
        chat_text.config(state=tk.NORMAL)
        chat_text.delete(1.0, tk.END)
        chat_text.config(state=tk.DISABLED)
        messagebox.showinfo("Historial Borrado", "Tu historial ha sido eliminado correctamente.")

# Función para mostrar la interfaz del chat
def mostrar_chat(nombre, historial):
    ventana_chat = tk.Tk()
    ventana_chat.title(f"Chat de {nombre}")
    ventana_chat.geometry("400x500")
    ventana_chat.configure(bg="#2C3E50")

    chat_text = scrolledtext.ScrolledText(ventana_chat, wrap=tk.WORD, width=50, height=15, bg="#ECF0F1", fg="#2C3E50", font=("Arial", 10))
    chat_text.pack(padx=10, pady=10)
    chat_text.insert(tk.END, "\n".join(historial[nombre]) + "\n")
    chat_text.config(state=tk.DISABLED)

    entrada_texto = tk.Entry(ventana_chat, width=40, font=("Arial", 10), bg="#ECF0F1", fg="#2C3E50")
    entrada_texto.pack(pady=5)

    def enviar_mensaje():
        mensaje = entrada_texto.get().strip()
        user_input_normalizado = normalizar_texto(mensaje)
        if user_input_normalizado:
            if user_input_normalizado in ["exit", "quit"]:
                ventana_chat.destroy()
                return

            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            chat_text.config(state=tk.NORMAL)
            chat_text.insert(tk.END, f"\n{timestamp} You: {user_input_normalizado}\n")
            chat_text.config(state=tk.DISABLED)

            # Obtener la respuesta del chatbot usando el modelo de IA
            response = chatbot_response(user_input_normalizado)  # Respuesta del bot usando el modelo de IA

            chat_text.config(state=tk.NORMAL)
            chat_text.insert(tk.END, f"{timestamp} SerraBot: {response}\n")
            chat_text.config(state=tk.DISABLED)

            historial[nombre].append(f"{timestamp} You: {user_input_normalizado}")
            historial[nombre].append(f"{timestamp} SerraBot: {response}")
            guardar_historial(historial)

            entrada_texto.delete(0, tk.END)

    boton_enviar = tk.Button(ventana_chat, text="Enviar", command=enviar_mensaje, bg="#3498DB", fg="white", font=("Arial", 10, "bold"), height=2, width=6)
    boton_enviar.pack(pady=15)

    boton_historial = tk.Button(ventana_chat, text="Ver Historial Completo", command=lambda: mostrar_historial(nombre, historial), bg="#E74C3C", fg="white", font=("Arial", 10, "bold"))
    boton_historial.pack(pady=5)

    boton_borrar = tk.Button(ventana_chat, text="Borrar Historial", command=lambda: borrar_historial(nombre, historial, chat_text), bg="#C0392B", fg="white", font=("Arial", 10, "bold"))
    boton_borrar.pack(pady=5)

    ventana_chat.mainloop()

# Ventana de inicio de sesión
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
