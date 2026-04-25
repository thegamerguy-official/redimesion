import tkinter as tk
from tkinter import ttk

window = tk.Tk()

def boton_func(text):
    print(text)
entry = ttk.Entry(window)
entry.pack()
boton1 = ttk.Button(window, text = 'Un simple boton.', command = lambda: boton_func(entry.get()))
boton1.pack()
window.mainloop()