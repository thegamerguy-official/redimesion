import tkinter as tk
from tkinter import ttk
#para 2 entries que hagan "mirror" simplemente les ponemos el mismo stringvar y ya esta.
def button_func():
    print(stringvar.get())
    stringvar.set('boton presionado')
window = tk.Tk()
window.title('Variables de Tkinter')

stringvar = tk.StringVar(value = 'valor inicial')

label = ttk.Label(master = window, text = 'texto', textvariable = stringvar)
label.pack()

entry = ttk.Entry(master = window, textvariable = stringvar)
entry.pack()

button = ttk.Button(master = window, text = 'boton', command = button_func)
button.pack()
window.mainloop()