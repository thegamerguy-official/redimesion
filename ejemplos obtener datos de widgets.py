import tkinter as tk
from tkinter import ttk

def button_func():
    #obtener contenido de entrada
    print(entry.get())

window = tk.Tk()
window.title('Consiguiendo y seteando widgets')

label = ttk.Label(master = window, text = 'Pon algo y dale click al boton!')
label.pack()
entry = ttk.Entry(master = window)
entry.pack()
button = ttk.Button(master = window, text = 'Haz click para enviar el texto', command = button_func)
button.pack()

window.mainloop()