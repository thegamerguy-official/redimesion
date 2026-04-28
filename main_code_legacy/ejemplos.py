import tkinter as tk
from tkinter import ttk
import time
mn_win = tk.Tk()
mn_win.title('REDIMENSON PRE-ALPHA')
mn_win.geometry('800x500')
txt_btt = ttk.Label(master = mn_win ,text = 'Este texto ha aparecido porque el boton ha sido clickeado.')
def btt_pres():
    print('El boton fue clikeado.')
    txt_btt.pack()
    mn_win.after(2000, txt_btt.pack_forget)
txt_ver = ttk.Label(master = mn_win, text = 'Esto es una versión PRE-ALPHA del programa REDIMENSION.')
txt_ver.pack()
usr_inpt = ttk.Entry(master = mn_win)
usr_inpt.pack()
button = ttk.Button(master = mn_win,text = 'TEST', command = btt_pres)
button.pack()
mn_win.mainloop()