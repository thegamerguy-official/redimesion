import tkinter as tk
from tkinter import ttk

window = tk.Tk()
window.title('Menu Dropdown y Commo Box')

items = ('Helado', 'Pizza', 'Pollo')
food_string = tk.StringVar(value = items[0])
spin_int = tk.IntVar(value = 12)
comobox = ttk.Combobox(window, textvariable = food_string)
#Las 2 lineas de abajo hacen lo mismo.
#comobox['values'] = items
comobox.configure(values = items)
comobox.pack()
spinbox = ttk.Spinbox(window, from_ = 3, to = 20, increment = 3, command = lambda: print(spin_int.get()), textvariable = spin_int)
spinbox.pack()
comobox.bind('<<ComboboxSelected>>', lambda event: combo_label.config(text = f'Valor seleccionado: {food_string.get()}'))
spinbox.bind('<<Increment>>', lambda event: print('arriba'))
spinbox.bind('<<Decrement>>', lambda event: print('abajo'))

combo_label = ttk.Label(window, text = '')
combo_label.pack()
window.mainloop()