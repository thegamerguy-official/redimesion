import tkinter as tk
from tkinter import ttk

window = tk.Tk()
window.title('Botones')
window.geometry('600x400')
#podemos poner el nombre de la variable que es la ventana en un objeto como un boton porque lo interpretará como master.
def button_func():
    print('un boton basico.')
#podemos usar lambda tambien si no queremos una funcion.
button_stringvar = tk.StringVar(value = 'Un boton con una stringvar.')
button = ttk.Button(window, text = 'Un simple boton', command = button_func, textvariable = button_stringvar)
button.pack()

#checkbutton
#Side note, si pongo el on value dentro del parentesis de Intvar la casilla estará marcada por defecto, útil para opciones "por defecto"
#Algo util para checkboxes, podemos incluir un off value en algunas para hacerlas "mutuamente exclusivas" en el caso de selección de configuración esto se logra si en una ponemos su off value como por ejemplo 5 y la que queremos mutuamente exclusiva hacemos una funcion lambda talque asi: lambda: NOMBREDEVARIABLEAQUI.set(valordeoffdelaquequeramosexcluir) no se nos olvide tmb asignar variable comun a las 2.
check_var = tk.IntVar(value = 10)
def check_func():
    check_var.set(10)
#MUY IMPORTANTE! Podemos usar on y offvalue para en el caso de que usemos un Intvar dar un valor a un estado, esto nos puede ser útil en múltiples operaciones.
check1 = ttk.Checkbutton(window, text = 'Checkbox 1', command = check_func, variable = check_var, onvalue = 10 , offvalue = 0)
check1.pack()
check2 = ttk.Checkbutton(window, text = 'Checkbox 2',command = lambda: check_var.set(0), offvalue = 10, onvalue = 0, variable = check_var)
check2.pack()
#radio buttons
#IMPORTANTISIMO! Si no asignamos valor a esto al chequear 1 se chequean los 2 a la vez, poner valores separados en cada uno, valores identicos (en un caso sin valor siendo nada) se chequearan juntos.
#Ah tambien, en este caso especifico si usamos en los 2 esto y oh mira 1 de ellos es un numero es mejor una strinvar, ya que se maneja automaticamente la conversion de str a int.
#La idea de los radio buttons es solo 1 a la vez, especialemnte util si elegimos opciones como "Maximum Space Saving", y etc ese tipo de casos es MUY util.
radio_var = tk.StringVar()
radio1 = ttk.Radiobutton(window, text = 'radiobutton1', value = 1, command = lambda: print(radio_var.get()), variable = radio_var)
radio2 = ttk.Radiobutton(window, text = 'radiobutton2', value = 'radio', variable = radio_var)
radio1.pack()
radio2.pack()
window.mainloop()