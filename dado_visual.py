import os
import random
import tkinter as tk
from PIL import Image, ImageTk

class DadoVisual:
    def __init__(self, root):
        self.root = root
        self.root.title("Dado Visual")
        self.root.geometry("320x350")

        self.imagenes_dado = []
        self.cargar_imagenes()

        self.lbl_dado = tk.Label(root, image=self.imagenes_dado[1])
        self.lbl_dado.pack(pady=20)

        self.btn_lanzar = tk.Button(
            root, 
            text="Lanzar Dado",
            font=("Helvetica", 14, "bold"), 
            command=self.iniciar_giro
        )
        self.btn_lanzar.pack(pady=20)

    def cargar_imagenes(self):
        for i in range(1, 7):
            nombre_archivo = f"dado_{i}.jpg"

            if not os.path.exists(nombre_archivo):
                img=Image.new("RGB", (100, 100), color=(255, 255, 255))
            else:
                img = Image.open(nombre_archivo)

            img = img.resize((150, 150), Image.Resampling.LANCZOS)
            self.imagenes_dado[i] = ImageTk.PhotoImage(img)

    def iniciar_giro(self):
        self.btn_lanzar.config(state=tk.DISABLED)
        valor_final = random.randint(1, 6)

        self.animar_paso(paso = 0, pasos_totales = 10, retardo= 40, valor_final= valor_final)

    def animar_paso(self, paso, pasos_totales, retardo, valor_final):
        if paso < pasos_totales:
            cara_temporal = random.randint(1, 6)
            self.lbl_dado.config(image=self.imagenes_dado[cara_temporal])
            nuevo_retardo = int (retardo * 1.2)

            self.root.after(
                nuevo_retardo,
                self.animar_paso,
                paso + 1,
                pasos_totales,
                nuevo_retardo,
                valor_final
            )
        else:
            self.lbl_dado.config(image=self.imagenes_dado[valor_final])
            self.btn_lanzar.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = DadoVisual(root)
    root.mainloop()