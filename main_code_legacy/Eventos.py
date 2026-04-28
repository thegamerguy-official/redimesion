import tkinter as tk
from tkinter import ttk
# pagina web con lista de eventos
#pythontutorial.net/tkinter/tkinter-event-binding
window = tk.Tk()
#Eventos pueden ser muchas cosas, desde lo mas comun (inputs de teclado para shortcuts) hasta cosas como Mouse Clicks, Widgets siendo seleccionados y deseleccionados y widgets siendo alterados y etc...
# Estos pueden ser observados Y USADOS!
#Bindear eventos a widgets, ejemplo: Widget.bind(evento,funcionausar)
# Formato de eventos: modificador-tipo-detalle
# Si queremos chequear alt y tecla a presionada seria algo como:
# Alt-Keypress-a
# Hagamos ejemplos aquí abajo
def get_pos(event):
    print(f'x: {event.x} y: {event.y}')
window.geometry('600x500')
window.title('Bindeo de Eventos')

texto = tk.Text(window)
texto.pack()

entrada = ttk.Entry(window)
entrada.pack()

btn = ttk.Button(window, text = 'Un boton.')
btn.pack()
#eventos aqui
#Analizemos este codigo
#Estamos bindeando al widget window (la ventana) un evento, este debe estar
# Como string entre '' en el formato anteriormente especificado,
# Especial atencion a como se escribe, tkinter es sensitivo a mayusculas y minusculas en codigo.
# Se cierra y abre con <> (es asi, y ya)
# Y usamos un lambda, pero debe ser un lambda EVENT o si no dará error.
window.bind('<Alt-KeyPress-a>', lambda event: print('evento'))
#window.bind('<Alt-KeyPress-a>', lambda event: print(event))
# podemos quitar de comentario loo de encima pero basicamente printea
# detalles mas tecnicos del evento.
# Ejemplo para nuestro evento: 
# <KeyPress event state=Mod1 keysym=a keycode=38 char='a' x=440 y=302>
#OJO! Al bindear con la ventana este evento se trigerea en cualquier lugar de la ventana
# Si lo bindease al boton solo si lo hemos seleccionado mediante un click se trigerea.
#Trackeamos x e y del raton, LA TITLEBAR NO CUENTA PARA ESTO POR EJEMPLO!
window.bind('<Motion>', get_pos)
#texto.bind('<Motion>', get_pos)
#Por si queremos probar con el tema de ver de dentro de los widgets
#Solo se trigerea dentro del widget "text"
#A veces solo queremos ver CUALQUIER keypress, en ese caso quitamos la parte inicial y final.
window.bind('<KeyPress>', lambda event: print(f'una tecla fue presionada: ({event.char})'))

entrada.bind('<FocusIn>', lambda event: print('El campo de entrada fue seleccionado.'))
entrada.bind('<FocusOut>', lambda event: print('El campo de entrada fue deseleccionado.'))
#ejercicio del tutorial.
#texto.bind('<Shift-MouseWheel>', lambda event: print('mousewheel'))
window.mainloop()