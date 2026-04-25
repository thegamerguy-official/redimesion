import tkinter as tk
from tkinter import ttk
# Esta lógica se basa en usar funciones lambda y al llamar una funcion podemos
# Usar los parentesis para usar argumentos en funciones que loo requieran
# Este caso es una funcion que tiene como arg texto a printear.
window = tk.Tk()

def boton_func(text):
    print(text)
entry = ttk.Entry(window)
entry.pack()
boton1 = ttk.Button(window, text = 'Un simple boton.', command = lambda: boton_func(entry.get()))
boton1.pack()
window.mainloop()