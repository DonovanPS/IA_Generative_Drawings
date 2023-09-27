import numpy as np
import matplotlib.pyplot as plt

# Cargar el archivo cat.npy
data = np.load("data/owl.npy", allow_pickle=True)

# Aumentar la calidad de visualización
plt.figure(dpi=300)

# Mostrar las primeras 5 imágenes
for i in range(1):
    plt.subplot(1, 1, i+1)  # Crear un espacio en la cuadrícula para cada imagen
    inverted_image = 255 - data[i].reshape(28, 28)  # Invertir colores
    plt.imshow(inverted_image, cmap='gray', vmin=0, vmax=255)
    plt.axis('off')  # No mostrar ejes en la imagen

plt.tight_layout()  # Ajustar el diseño de la figura
plt.show()  # Mostrar todas las imágenes juntas
