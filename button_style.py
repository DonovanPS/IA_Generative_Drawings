
from tkinter import ttk

def get_custom_button_style():
    style = ttk.Style()
    style.configure("Custom.TButton",
        background="#E0E0E0",  # Color de fondo gris claro (más suave)
        foreground="#333333",  # Color del texto (gris oscuro)
        font=("Arial", 11),  # Fuente similar a la de los títulos
        borderwidth=1,  # Ancho del borde (1 para un borde más delgado)
        relief="raised",  # Estilo del borde (raised para un efecto 3D)
        padding=(10, 5),  # Relleno interno (10 píxeles horizontal, 5 píxeles vertical)
        focuscolor="#CCCCCC"  # Color de enfoque (cuando se presiona el botón)
    )
    return "Custom.TButton"  # Devuelve el nombre del estilo

