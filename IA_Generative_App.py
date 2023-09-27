import numpy as np
import tkinter as tk
import datetime
import os
import shutil
import replicate
import requests
import base64
import json
import threading


from PIL import Image, ImageTk, ImageGrab
from keras.models import load_model
from io import BytesIO
from tkinter import font, ttk, messagebox
from image_viewer import ImageViewer

from button_style import get_custom_button_style

base_image_directory = "images\save_data"
save = ""


# Cargar el modelo entrenado
model = load_model("models/Animals4.h5")

# Configuración de la ventana
WIDTH, HEIGHT = 400, 400
BACKGROUND_COLOR = "white"
DRAW_COLOR = "black"
LINE_WIDTH_THIN = 2  # Grosor de línea del canvas superior
LINE_WIDTH_THICK = 10  # Grosor de línea del canvas inferior

background_color = "#CD95EB"



# Categorías
categorical = ['bear', 'bird', 'butterfly', 'cat', 'crab', 'elephant',
               'fish', 'lion', 'octopus', 'owl', 'rhinoceros', 'sea turtle',
               'sheep', 'snail', 'snake']

# Inicializar la ventana de tkinter
root = tk.Tk()
root.title("Dibuja Identifica Genera")
root.configure(bg=background_color)



# Crear un marco principal
main_frame = tk.Frame(root, bg=background_color)
main_frame.pack()

# fuente personalizada
titulo_font = font.Font(family="Helvetica", size=18, weight="bold")

# Crear un marco para las imágenes (izquierda)
images_frame_left = tk.Frame(main_frame, bg=background_color)
images_frame_left.pack(side=tk.LEFT, padx=20)

# Título para el canvas de la izquierda
label_left = tk.Label(images_frame_left, text="Dibujo mejorado", font=titulo_font, bg=background_color)
label_left.pack(pady=15)  # pady



# Cargar la imagen improved_drawing.png
imagen_improved_drawing = Image.open("improved_drawing.png")
imagen_improved_drawing.thumbnail((WIDTH, HEIGHT))  # Ajusta el tamaño si es necesario

# Convierte la imagen PIL a PhotoImage
imagen_tk = ImageTk.PhotoImage(imagen_improved_drawing)

# Agregar un Label en el marco para mostrar la imagen
imagen_label = tk.Label(images_frame_left, image=imagen_tk)
imagen_label.pack()

# Crear un marco para los lienzos y botones
canvas_frame = tk.Frame(main_frame, bg=background_color)
canvas_frame.pack(side=tk.LEFT, pady=(0,20))

# Título
label_draw = tk.Label(canvas_frame, text="Lienzo", font=titulo_font, bg=background_color)
label_draw.pack(pady=(30,15))  # pady


# Inicializar el lienzo de dibujo
canvas = tk.Canvas(canvas_frame, width=WIDTH, height=HEIGHT, bg=BACKGROUND_COLOR)
canvas.pack()

# Inicializar imagen de dibujo
canvas_image = np.zeros((WIDTH, HEIGHT), dtype=np.uint8)

# Variables para rastrear el estado del dibujo
drawing = False

# Función para manejar el dibujo en el lienzo superior
def start_drawing(event):
    global drawing
    drawing = True

def draw(event):
    if drawing:
        x, y = event.x, event.y
        canvas.create_oval(x - LINE_WIDTH_THIN, y - LINE_WIDTH_THIN, x + LINE_WIDTH_THIN, y + LINE_WIDTH_THIN,
                           fill=DRAW_COLOR)
        canvas_image[y - LINE_WIDTH_THIN:y + LINE_WIDTH_THIN, x - LINE_WIDTH_THIN:x + LINE_WIDTH_THIN] = 255

        # Dibuja en el canvas inferior con grosor mayor
        x_scaled = int(x * (WIDTH / canvas.winfo_width()))  # Escalar coordenadas
        y_scaled = int(y * (HEIGHT / canvas.winfo_height()))
        canvas_hidden.create_oval(x_scaled - LINE_WIDTH_THICK, y_scaled - LINE_WIDTH_THICK,
                                  x_scaled + LINE_WIDTH_THICK, y_scaled + LINE_WIDTH_THICK, fill=DRAW_COLOR)
        canvas_image_hidden[y_scaled - LINE_WIDTH_THICK:y_scaled + LINE_WIDTH_THICK,
        x_scaled - LINE_WIDTH_THICK:x_scaled + LINE_WIDTH_THICK] = 255


def stop_drawing(event):
    global drawing
    drawing = False

canvas.bind("<Button-1>", start_drawing)
canvas.bind("<B1-Motion>", draw)
canvas.bind("<ButtonRelease-1>", stop_drawing)




# Función para limpiar el lienzo de dibujo

def clear_canvas():
    global canvas_image, canvas_image_hidden
    canvas.delete("all")
    canvas_image = np.zeros((WIDTH, HEIGHT), dtype=np.uint8)
    canvas_hidden.delete("all")
    canvas_image_hidden = np.zeros((WIDTH, HEIGHT), dtype=np.uint8)
    prediction_label.config(text="Clase Identificada: ")

    global save
    save = ""




# Función para predecir el dibujo
def predict_drawing():
    image = Image.fromarray(canvas_image_hidden)
    image = image.convert("L").resize((28, 28))
    image_array = np.array(image)
    image_array = image_array.reshape(1, 28, 28, 1)
    image_array = image_array.astype('float32') / 255.0

    prediction = model.predict(image_array)
    predicted_class = np.argmax(prediction)

    global save
    save = categorical[predicted_class]
    prediction_label.config(text="Clase Identificada: " + str(predicted_class) + " - " + categorical[predicted_class])
    capture_and_save_image()


def save_images():
    if save != "":
        current_date = datetime.datetime.now()
        current_date_formatted = current_date.strftime("%Y-%m-%d-%H-%M-%S")  # Eliminar ':' de la hora

        # Nombres de archivo originales y nuevos
        original_filenames = ["temp_image.png", "improved_drawing.png", "real_drawing.png"]
        new_filenames = [
            "1temp_image_" + current_date_formatted + ".png",
            "2improved_drawing_" + current_date_formatted + ".png",
            "3real_drawing_" + current_date_formatted + ".png"
        ]

        folder = os.path.join(base_image_directory, save)

        try:
            # Crear el directorio si no existe
            os.makedirs(folder, exist_ok=True)

            # Lista para rastrear si se guardaron todas las imágenes con éxito
            all_images_saved = True

            # Copiar y renombrar los archivos
            for original, new in zip(original_filenames, new_filenames):
                source_path = os.path.join(".", original)  # Ruta de origen en el directorio actual
                destination_path = os.path.join(folder, new)  # Ruta de destino

                try:
                    shutil.copy(source_path, destination_path)
                except Exception as e:
                    # Si ocurre un error al copiar una imagen, establecer all_images_saved en False
                    all_images_saved = False
                    messagebox.showerror("Error", f"Ocurrió un error al copiar {original}:\n{str(e)}")

            # Mostrar un mensaje de éxito si todas las imágenes se guardaron con éxito
            if all_images_saved:
                messagebox.showinfo("Éxito", "Todas las imágenes se han guardado correctamente.")

        except Exception as e:
            messagebox.showerror("Error", "Ocurrió un error al crear el directorio:\n" + str(e))

    else:
        messagebox.showwarning("Alerta", "El dibujo no se ha identificado. No se puede guardar.")


# Función para alternar la visibilidad del lienzo inferior
def toggle_canvas_visibility():
    if canvas_hidden_frame.winfo_ismapped():
        canvas_hidden_frame.pack_forget()
    else:
        canvas_hidden_frame.pack()



# Etiqueta para la predicción
label_font = font.Font(family="Helvetica", size=10, weight="bold")

prediction_label = tk.Label(canvas_frame, text="Clase Identificada: ",font=label_font,bg=background_color)
prediction_label.pack(pady=3)


# Crear un marco para los tres primeros botones
button_frame = tk.Frame(canvas_frame, bg=background_color)
button_frame.pack(side=tk.TOP, padx=10, pady=10)

# Botón Identificar
predict_button = ttk.Button(button_frame, text="Identificar", command=predict_drawing, style=get_custom_button_style())
predict_button.pack(side=tk.LEFT, padx=5)

# Botón Limpiar
clear_button = ttk.Button(button_frame, text="Limpiar", command=clear_canvas, style=get_custom_button_style())
clear_button.pack(side=tk.LEFT, padx=5)

# Botón Guardar
save_button = ttk.Button(button_frame, text="Guardar", command=save_images,  style=get_custom_button_style())
save_button.pack(side=tk.LEFT, padx=5)

# Botón para alternar la visibilidad del lienzo inferior
toggle_button = ttk.Button(canvas_frame, text="Mostrar/Ocultar Lienzo Inferior", command=toggle_canvas_visibility, style=get_custom_button_style())
toggle_button.pack(pady=3)


# Crear un marco para las imágenes cargadas (derecha)
images_frame_right = tk.Frame(main_frame, bg=background_color)
images_frame_right.pack(side=tk.LEFT, padx=20)

# Título para el canvas de la derecha
label_right = tk.Label(images_frame_right, text="Imagen realista", font=titulo_font, bg=background_color)
label_right.pack(pady=15)  # pady
label_right.pack()

# Cargar la imagen real_drawing.png
imagen_final_drawing = Image.open("real_drawing.png")
imagen_final_drawing.thumbnail((WIDTH, HEIGHT))

# Convierte la imagen PIL a PhotoImage
imagen_tk2 = ImageTk.PhotoImage(imagen_final_drawing)

# Agregar un Label en el marco para mostrar la imagen
imagen_label2 = tk.Label(images_frame_right, image=imagen_tk2, bg=BACKGROUND_COLOR)
imagen_label2.pack()

# Crear un marco para el lienzo inferior
canvas_hidden_frame = tk.Frame(canvas_frame)
canvas_hidden_frame.pack()

# Inicializar el lienzo de dibujo oculto
canvas_hidden = tk.Canvas(canvas_hidden_frame, width=WIDTH, height=HEIGHT, bg=BACKGROUND_COLOR)
canvas_hidden.pack()

# Inicializar imagen de dibujo oculto
canvas_image_hidden = np.zeros((WIDTH, HEIGHT), dtype=np.uint8)



# Ruta donde se almacenará la imagen temporalmente
TEMP_IMAGE_PATH = "temp_image.png"


# Función para capturar y guardar la imagen del canvas de arriba
def capture_and_save_image():
    # Obtener las coordenadas del canvas superior
    x = canvas.winfo_rootx()
    y = canvas.winfo_rooty()
    x1 = x + canvas.winfo_width()
    y1 = y + canvas.winfo_height()

    # Tomar una captura de pantalla del canvas superior
    screenshot = ImageGrab.grab(bbox=(x, y, x1, y1))

    # Guardar la captura de pantalla en la ruta temporal
    screenshot.save(TEMP_IMAGE_PATH)

    #print("Imagen capturada y guardada en:", TEMP_IMAGE_PATH)

# Función para predecir el dibujo y generar una imagen
def predict_and_generate():
    if save != "":

        REPLICATE_API_TOKEN = "r8_dJ2HOGUB9msu7vh0QRDYEQhh49Q60uv1UlHYu"
        # REPLICATE_API_TOKEN = "r8_FGqUKoAiN9Jj4YjxJnoHt5TgdeF670A4WZb0a"

        # Autenticación a través de la variable de entorno
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

        # Función para ejecutar replicate.run en un hilo separado
        def run_replicate():
            # Ejecutar el modelo de generación con la imagen dibujada como entrada
            output = replicate.run(
                "rossjillian/controlnet:795433b19458d0f4fa172a7ccf93178d2adb1cb8ab2ad6c8fdc33fdbcd49f477",
                input={"image": open(TEMP_IMAGE_PATH, "rb"),
                       "prompt": f" finished drawing with White background of a {save} to black and white",
                       "negative_prompt": "no notebook",
                       "structure": "scribble",
                       "num_outputs": 1,
                       "image_resolution": 512,
                       "scheduler": "DDIM",
                       "steps": 20,
                       "scale": 9,
                       "seed": 0,
                       "eta": 0,
                       "return_reference_image": False,
                       "low_threshold": 100,
                       "high_threshold": 200
                       },
            )

            # Obtener la URL de la imagen generada
            generated_image_url = output[0]

            # Descargar la imagen desde la URL y guardarla localmente
            if generated_image_url:
                response = requests.get(generated_image_url)
                if response.status_code == 200:
                    generated_image_path = "improved_drawing.png"
                    with open(generated_image_path, "wb") as f:
                        f.write(response.content)

                    # Cargar y mostrar la imagen mejorada
                    load_and_show_improved_image()

        # hilo para ejecutar run_replicate
        replicate_thread = threading.Thread(target=run_replicate)

        # Iniciar el hilo
        replicate_thread.start()

    else:
        messagebox.showwarning("Alerta", "El dibujo no se ha identificado. No se puede Generar.")


# Botón para predecir, generar imagen y ejecutar modelo
generate_button = ttk.Button(images_frame_left, text="Generar imagen", command=predict_and_generate, style= get_custom_button_style())
generate_button.pack(pady=(20,80))



def load_and_show_improved_image():
    improved_image = Image.open("improved_drawing.png")
    improved_image.thumbnail((WIDTH, HEIGHT))  # Ajusta el tamaño si es necesario
    improved_tk = ImageTk.PhotoImage(improved_image)
    imagen_label.config(image=improved_tk)
    imagen_label.image = improved_tk  # Mantén una referencia para evitar que se elimine la imagen


def load_image_from_api_and_save():
    if save != "":

        try:
            
            # Realiza una solicitud a la API para obtener la imagen
            # Prompt Positivo
            positive_prompt = f"Draw a realistic {save} in its natural habitat. Pay close attention to the details of its anatomy, fur or skin, texture, and distinctive features. Ensure that the environment it is in is consistent with its real habitat. I want the {save} to appear lifelike and in motion, and its representation to be true to nature."

            # Prompt Negativo
            negative_prompt = f"Do not depict a caricature or an exaggerated interpretation of the {save}. Avoid unnatural colors or unusual situations for the {save}. I do not want the {save} to appear out of context or in an awkward position. The representation should be realistic and consistent with the biology and behavior of the {save}."

            motor = "stable-diffusion-xl-beta-v2-2-2"
            url = "https://api.stability.ai/v1/generation/" + motor + "/text-to-image"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": "Bearer sk-QWRRAef9VuvcJkTGX48gYsZ8PbCJJqR7abVXkRAcgx05vQK8",
            }
            text_prompts = [
                {
                    "text": positive_prompt,
                    "weight": 1
                }
            ]

            if negative_prompt.strip():
                text_prompts.append(
                    {
                        "text": negative_prompt,
                        "weight": -1
                    }
                )

            body = {
                "steps": 15,
                "width": 512,
                "height": 512,
                "seed": 0,
                "cfg_scale": 7,
                "samples": 1,
                "style_preset": "enhance",
                "text_prompts": text_prompts,
            }

            response = requests.post(url, headers=headers, json=body)

            if response.status_code == 200:
                data = response.json()
                image_base64 = data["artifacts"][0]["base64"]

                # Decodifica la imagen desde base64
                image_bytes = base64.b64decode(image_base64)
                image = Image.open(BytesIO(image_bytes))

                # Guarda la imagen con el nombre deseado en la raíz
                image.save("real_drawing.png")

                # Muestra la imagen en el Label
                image.thumbnail((WIDTH, HEIGHT))
                image_tk = ImageTk.PhotoImage(image)
                imagen_label2.config(image=image_tk)
                imagen_label2.image = image_tk
            else:

                try:
                    response_data = json.loads(response.text)
                    error_name = response_data.get('name', 'No Name Provided')
                    error_message = response_data.get('message', 'No Message Provided')
                except json.JSONDecodeError:
                    error_name = 'Unknown'
                    error_message = 'Failed to decode JSON response'

                name_error = f"Error: {error_name}"
                message = f"Message: {error_message}"
                messagebox.showerror(name_error, message)
                print("Error al obtener la imagen de la API")
                print("Mensaje de respuesta del servidor:", response.text)
        except Exception as e:
            messagebox.showerror("Error", "Ocurrió un error:" + str(e))
            print("Ocurrió un error:", str(e))

    else:
        messagebox.showwarning("Alerta", "El dibujo no se ha identificado. No se puede guardar.")


# Boton generar imagen realista (derecha)
load_and_save_image_button = ttk.Button(
    images_frame_right,
    text="Generar imagen",
    command=load_image_from_api_and_save,
    style= get_custom_button_style()
)
load_and_save_image_button.pack(pady=(20,80))

def load_images(image_paths):
    images = []
    for path in image_paths:
        image = Image.open(path)
        image.thumbnail((90, 90))
        images.append(ImageTk.PhotoImage(image))
    return images

image_paths = ["images/gato.png",
               "images/caracol.png",
               "images/pez.png",
               "images/tortuga.png",
               "images/oso.png",
               "images/rinoceronte.png",
               "images/pajaro.png",
               "images/leon.png",
               "images/pulpo.png",
               "images/serpiente.png",
               "images/oveja.png",
               "images/buho.png",
               "images/elefante.png",
               "images/cangrejo.png",
               "images/mariposa.png"
               ]
loaded_images = load_images(image_paths)

def enlarge_image(event):
    event.widget.config(bg="#7ea7bf")  # Cambiar el color de fondo al pasar el mouse

def restore_image(event):
    event.widget.config(bg=background_color)  # Cambiar el color de fondo al pasar el mouse

# Crear un nuevo marco para contener las imágenes
images_frame = tk.Frame(root, bg=background_color)
images_frame.pack()


image_folders = [
    "cat",
    "snail",
    "fish",
    "sea turtle",
    "bear",
    "rhinoceros",
    "bird",
    "lion",
    "octopus",
    "snake",
    "sheep",
    "owl",
    "elephant",
    "crab",
    "butterfly",

]

# Usar grid para organizar las imágenes en una fila horizontal con espacios personalizados
for i, image in enumerate(loaded_images):
    # Crear un Frame para cada imagen y establecer pady en ese Frame
    image_frame = tk.Frame(images_frame, bg=background_color)
    image_frame.grid(row=0, column=i, sticky="nsew")  # Organizar los Frames en una fila horizontal en images_frame

    # Colocar la imagen en el Frame y establecer el fondo personalizado
    label = tk.Label(image_frame, image=image, bg=background_color)
    label.pack()

    # Obtener la ruta de la carpeta de imágenes correspondiente
    folder_path = os.path.join(base_image_directory, image_folders[i])
    animal= image_folders[i]

    def open_image_viewer(event, folder):

        # Abrir la ventana del carrusel de imágenes con la carpeta específica
        viewer = ImageViewer(folder)
        viewer.root.mainloop()

    label.bind("<Enter>", enlarge_image)  # Hacer más grande la imagen cuando el mouse entra
    label.bind("<Leave>", restore_image)  # Restaurar tamaño original de la imagen cuando el mouse sale
    label.bind("<Button-1>", lambda event, folder=folder_path: open_image_viewer(event, folder))


canvas_hidden_frame.pack_forget()


# Iniciar bucle de la ventana
root.mainloop()

