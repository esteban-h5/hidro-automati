try:
    from tkinter import ttk, Tk, messagebox, Label
    from tkcalendar import DateEntry
    from _tkinter import TclError
    import tkinter as tk
    import random

except ModuleNotFoundError as e:
    input(f"Modulos no instalados: {e}\nEnter para cerrar")
    exit(1)  
    
from __myLIMS_wrappers__ import *

def mainStyle():
    main_style = ttk.Style()
    main_style.theme_use('clam')
    main_style.configure('off.TButton', foreground='gray')
    main_style.configure('on.TButton', foreground='black')

largo = lambda menu,n=1: int((len(menu)+n)*42)

separacion = 32
background = "#f0f0f0"

try:
    """
    1: Registros Pendientes
    2: Cambiar Lotes
    """
    tipo_menu = int(sys.argv[1])

except (ValueError, IndexError):
    messagebox.showerror(title="Error en programacion", message=f"No se especifica el menu del programa: \'{sys.argv}\'")
    exit(1)

match tipo_menu:

    ########################
    # REGISTROS PENDIENTES #
    ########################
    case 1:
        try:
            pais = str(sys.argv[2])
            cant_muestras = str(sys.argv[3])
            cant_muestras_aux = str(sys.argv[4])

        except (ValueError, IndexError):
            messagebox.showerror(message=f"Excepcion al ejecutar el programa:\n{' '.join(sys.argv[1:])}", title="Error en programacion", )
            state = False
            pais = "-1"

        state = bool(int(cant_muestras))

        #SUBMENU PARA REGISTRO AUXILIAR
        def sumbenu_registro_auxiliar():
            ventana.destroy()
            largo_botones = 60

            submenu = Tk()
            mainStyle()

            menu = {
                # "Mostrar Datos":6,
                "[GUARDAR] Navegador -> Excel":7,
                "[DESPLEGAR] Excel -> navegador":8,
                "Abrir Excel Auxiliar":9,
                "Limpiar Excel Auxiliar":10,
                "Atrás":11,
            }

            submenu.geometry(f"550x{largo(menu)}")
            submenu.config()
            submenu.title("Registros Pendientes - Excel Auxiliar")
            
            def cerrar():
                print("14")
                submenu.destroy()

            submenu.protocol("WM_DELETE_WINDOW", cerrar)

            def volver_atras():
                submenu.destroy()
                menu_principal_registro_pendientes()

            # texto = Label(submenu, text="País Actual: "+pais.upper()+"\nMuestras en Registro Auxiliar: "+cant_muestras_aux, font=("Arial", 10),anchor="e",justify="right")
            texto = Label(submenu, text="País Actual: "+pais.upper()+"\nMuestras enlistadas: "+cant_muestras+"\nMuestras en Registro Auxiliar: "+cant_muestras_aux, font=("Arial", 10),anchor="e",justify="right")
            texto.place(relx=1.0, rely=1.0, anchor='se')

            botones={}

            for idx,option in enumerate(menu):

                indice = menu[option]

                def click( numero=indice, submenu=submenu):
                    print(numero)
                    submenu.destroy()

                if (indice == 11):
                    botones[option] = ttk.Button(submenu, text=option, command=volver_atras, width=largo_botones, style='on.TButton')
                if (indice == 7 and cant_muestras == "0"):
                    botones[option] = ttk.Button(submenu, text=option, command=None, width=largo_botones, style='off.TButton')
                else:
                    botones[option] = ttk.Button(submenu, text=option, command=click, width=largo_botones, style='on.TButton')

                botones[option].place(x=90, y=separacion*(idx+1) )

            submenu.mainloop()

        def menu_principal_registro_pendientes():
            global ventana
            ventana = Tk()
            mainStyle()
            
            menu = {
                "Enlistar muestras":1,
                "Buscar y registrar controles":2,
                "Borrar muestras enlistadas":3,
                "Recargar Muestras en Registro Auxiliar":6,
                "Registro Auxiliar":5,
                # REGISTRO AUXILAR
                "Abrir Excel con Controles":12,
                "Limpiar Excel con Controles":13,
                "Salir y Cerrar Sesión":14
            }

            ventana.geometry(f"500x{largo(menu,.8)}")
            ventana.config()
            ventana.title("Registro Pendientes - Menú principal")

            def cerrar():
                print("14")
                ventana.destroy()
            
            ventana.protocol("WM_DELETE_WINDOW", cerrar)

            texto = Label(ventana, text="País Actual: "+pais.upper()+"\nMuestras enlistadas: "+cant_muestras+"\nMuestras en Registro Auxiliar: "+cant_muestras_aux, font=("Arial", 10),anchor="e",justify="right")
            texto.place(relx=1.0, rely=1.0, anchor='se')

            botones={}

            for idx,option in enumerate(menu):
                indice = menu[option]

                def click( numero=indice, ventana=ventana):
                    print(numero)
                    ventana.destroy()

                if not state and (indice == 2 or indice == 3):
                    botones[option] = ttk.Button(ventana, text=option, command=None, width=50, style='off.TButton')
                
                elif (indice == 5):
                    botones[option] = ttk.Button(ventana, text=option, command=sumbenu_registro_auxiliar, width=50, style='on.TButton')

                else:
                    botones[option] = ttk.Button(ventana, text=option, command=click, width=50, style='on.TButton')

                botones[option].place(x=90, y=separacion*(idx+1) )
            
            ventana.mainloop()

        menu_principal_registro_pendientes()

    #################
    # CAMBIAR LOTES #
    #################
    case 2:
        import pandas as pd

        if len(sys.argv) != 6:
            messagebox.showerror(message=f"Se requieren 7 argumentos y se obtienen {len(sys.argv)}:\n{sys.argv}", title="Error en programacion", )
            exit(1)

        try:
            sub_menu = int(sys.argv[2])
            path_lista = str(sys.argv[3])
            cantidad_muestras = str(sys.argv[4])
            pais = str(sys.argv[5])

        except (ValueError, IndexError) as e:
            messagebox.showerror(message=f"Excepcion al ejecutar el programa:\n{e}", title="Error en lista de muestras", )
            exit(1)

        try:
            df_muestras = pd.read_excel(path_lista, sheet_name="ListaMetodos")
            df_requerimientos = pd.read_excel(path_lista, sheet_name="Requerimientos")

        except Exception as e:
            messagebox.showerror(message=f"Excepcion al abrir el Excel lista de muestras:\n{e}", title="Error en lista de muestras", )
            exit(1)

        match sub_menu:
            #Menú excepción
            case -1:
                messagebox.showerror(message=f"Error en argumentos:\n{sys.argv}", title="Error de código")
                exit(1)

            #MENU PRINCIPAL
            case 0:
                botones_desactivados = []#4,7]
                
                #SUBMENU PARA MODIFICAR ANALISIS (CAMBIAR LOTES TRADICIONAL)
                def submenu_procesar_muestras():
                    try:
                        ventana.destroy()
                    except TclError:
                        pass

                    largo_botones = 75

                    submenu = Tk()
                    mainStyle()
                    
                    menu = {
                        "Reemplazar uno o más métodos por otro método de análisis":1,
                        "Reemplazar análisis por otro con el mismo método de análisis":2,
                        "Reemplazar un análisis por otro con otro método de análisis":3,
                        "Agregar análisis a muestras en lista":4,
                        "Eliminar método de muestras en lista":5,
                        "Cambiar Fecha Recibimiento":6,
                        "Reprocesar Precios y Envases":7,
                        "Volver":8
                    }

                    submenu.geometry(f"675x{largo( menu )}")
                    submenu.config()
                    submenu.title("Cambiar Lotes - Modificar Análisis")

                    #SUBMENU PARA MODIFICAR ANALISIS (CAMBIAR LOTES TRADICIONAL)
                    def sumbenu_recibimiento():
                        submenu.destroy()
                        largo_botones = 30

                        submenu_2 = Tk()
                        mainStyle()

                        submenu_2.geometry("400x300")
                        submenu_2.config()

                        submenu_2.title("Cambiar Lotes - Cambiar Fecha Recibimiento")
                        
                        def cerrar():
                            submenu_2.destroy()
                            print("-1")

                        submenu_2.protocol("WM_DELETE_WINDOW", cerrar)

                        def volver_atras():
                            submenu_2.destroy()
                            submenu_procesar_muestras()

                        texto = Label(submenu_2, text="País Actual: "+pais.upper()+"\nCantidad de muestras: "+cantidad_muestras, font=("Arial", 10))
                        texto.place(relx=1.0, rely=1.0, anchor='se')

                        date_label = tk.Label(submenu_2, text="Fecha:")
                        date_label.pack()

                        date_picker = DateEntry(submenu_2, width=12, date_pattern="dd-mm-y", background='darkblue', foreground='white', borderwidth=2)
                        date_picker.pack(padx=10, pady=10)

                        time_label = tk.Label(submenu_2, text="Hora:")
                        time_label.pack()

                        hour_var = tk.StringVar()
                        hour_var.set("12")

                        minute_var = tk.StringVar()
                        minute_var.set("30")

                        second_var = tk.StringVar()
                        second_var.set("30")

                        time_frame = tk.Frame(submenu_2)
                        time_frame.pack()

                        def spinbox_scroll(spinbox, event):
                            if event.delta > 0:
                                spinbox.invoke('buttonup')
                            else:
                                spinbox.invoke('buttondown')

                        hour_spinbox = tk.Spinbox(time_frame, from_=0, to=23, textvariable=hour_var, wrap=True, width=5)
                        hour_spinbox.pack(side=tk.LEFT)
                        hour_spinbox.bind("<MouseWheel>", lambda e: spinbox_scroll(hour_spinbox, e))

                        tk.Label(time_frame, text=":").pack(side=tk.LEFT)

                        minute_spinbox = tk.Spinbox(time_frame, from_=00, to=59, textvariable=minute_var, wrap=True, width=5)
                        minute_spinbox.pack(side=tk.LEFT)
                        minute_spinbox.bind("<MouseWheel>", lambda e: spinbox_scroll(minute_spinbox, e))

                        tk.Label(time_frame, text=":").pack(side=tk.LEFT)

                        second_spinbox = tk.Spinbox(time_frame, from_=00, to=59, textvariable=second_var, wrap=True, width=5)
                        second_spinbox.pack(side=tk.LEFT)
                        second_spinbox.bind("<MouseWheel>", lambda e: spinbox_scroll(second_spinbox, e))

                        def submit_clicked():
                            selected_date = date_picker.get_date().strftime("%d-%m-%Y")

                            selected_hour = hour_var.get()
                            selected_minute = minute_var.get()
                            selected_second = second_var.get()

                            hora = ":".join([f"{int(selected):02d}" for selected in (selected_hour, selected_minute, selected_second) if selected.isdigit()])
                            print(f"6|{selected_date} {hora}", end="")
                            submenu_2.destroy()

                        def random_date():

                            random_hour = random.randint(9, 18)
                            random_minute = random.randint(0, 59)
                            random_second = random.randint(0, 59)

                            hour_var.set(str(random_hour))
                            minute_var.set(str(random_minute))
                            second_var.set(str(random_second))

                        submit_button = ttk.Button(submenu_2, text="Generar hora laboral", command=random_date, width=largo_botones, style='on.TButton')
                        submit_button.pack(padx=10, pady=10)

                        submit_button = ttk.Button(submenu_2, text="Continuar", command=submit_clicked, width=largo_botones, style='on.TButton')
                        submit_button.pack(padx=10, pady=10)

                        volver = ttk.Button(submenu_2, text="Volver", command=volver_atras, width=largo_botones, style='on.TButton')
                        volver.pack()
                        
                        submenu_2.mainloop()

                    def cerrar():
                        print("-1")
                        submenu.destroy()

                    submenu.protocol("WM_DELETE_WINDOW", cerrar)

                    def volver_atras():
                        submenu.destroy()
                        menu_principal_procesar_muestras()

                    texto = Label(submenu, text="País Actual: "+pais.upper()+"\nCantidad de muestras: "+cantidad_muestras, font=("Arial", 10))
                    texto.place(relx=1.0, rely=1.0, anchor='se')

                    botones={}

                    for idx,option in enumerate(menu):

                        indice = menu[option]

                        def click( numero=indice, submenu=submenu):
                            print(numero)
                            submenu.destroy()
                        
                        if indice in botones_desactivados:
                            botones[option] = ttk.Button(submenu, text=option, command=None, width=largo_botones, style='off.TButton')
                        
                        else:
                            if (indice==8):
                                botones[option] = ttk.Button(submenu, text=option, command=volver_atras, width=largo_botones, style='on.TButton')
                            elif (indice==6):
                                botones[option] = ttk.Button(submenu, text=option, command=sumbenu_recibimiento, width=largo_botones, style='on.TButton')
                            else:
                                botones[option] = ttk.Button(submenu, text=option, command=click, width=largo_botones, style='on.TButton')

                        botones[option].place(x=90, y=separacion*(idx+1) )

                    submenu.mainloop()

                def submenu_excel():
                    try:
                        ventana.destroy()
                    except TclError:
                        pass

                    menu = {
                        "Abrir DIRECTORIO de descarga actual":17,
                        "Abrir EXCEL de lista [ACTUAL] [RUTINAS]":18,
                        "Limpiar EXCEL de lista actual":19,
                        "Abrir EXCEL de RegistrosPendientes [CONTROLES]":20,
                        "Abrir EXCEL de DescargaMuestras [ESTADOS]":21,
                        "Copiar Registro a Historico en DescargaMuestras":22,
                        "Volver":23,
                    }

                    largo_botones = 75

                    submenu = Tk()
                    mainStyle()

                    submenu.geometry(f"515x{largo(menu)}")
                    submenu.config()
                    submenu.title("Cambiar Lotes - Excel y Registros")

                    def cerrar():
                        print("-1")
                        submenu.destroy()
                        
                    submenu.protocol("WM_DELETE_WINDOW", cerrar)

                    texto = Label(submenu, text="País Actual: "+pais.upper()+"\nCantidad de muestras: "+cantidad_muestras, font=("Arial", 10))
                    texto.place(relx=1.0, rely=1.0, anchor='se')

                    botones={}
                    largo_botones = 50

                    def volver_atras():
                        submenu.destroy()
                        menu_principal_procesar_muestras()

                    for idx,option in enumerate(menu):
                        indice = menu[option]

                        def click( numero=indice, ventana=submenu):
                            print(numero)
                            ventana.destroy()

                        if (indice == 23): botones[option] = ttk.Button(submenu, text=option, command=volver_atras, width=largo_botones, style='on.TButton')
                        elif (indice in botones_desactivados):  botones[option] = ttk.Button(submenu, text=option, command=None, width=largo_botones, style='off.TButton')
                        else: botones[option] = ttk.Button(submenu, text=option, command=click, width=largo_botones, style='on.TButton')

                        botones[option].place(x=90, y=separacion*(idx+1) )

                    ventana.mainloop()

                def menu_principal_procesar_muestras():
                    global ventana
                    ventana = Tk()
                    mainStyle()

                    menu = {
                        "Modificar Análisis":1, #+8
                        "Descargar Muestras en lista":15,
                        "Excel y Registros":16, #+5
                        "Recargar Muestras en lista":30,
                        "Salir":31,
                        # "TEMP":-10
                    }
                
                    ventana.geometry(f"515x{largo(menu)}")
                    ventana.config()
                    ventana.title("Cambiar Lotes - Menú principal")

                    def cerrar():
                        print("-1")
                        ventana.destroy()
                        
                    ventana.protocol("WM_DELETE_WINDOW", cerrar)

                    texto = Label(ventana, text="País Actual: "+pais.upper()+"\nCantidad de muestras: "+cantidad_muestras, font=("Arial", 10))
                    texto.place(relx=1.0, rely=1.0, anchor='se')

                    botones={}
                    largo_botones = 50

                    for idx,option in enumerate(menu):
                        indice = menu[option]

                        def click( numero=indice, ventana=ventana):
                            print(numero)
                            ventana.destroy()

                        if (indice == -10):
                            botones[option] = ttk.Button(ventana, text=option, command=click, width=5, style='on.TButton').place(x=0, y=0)
                        
                        elif (indice in botones_desactivados) or (cantidad_muestras=="0" and indice in [1,15]):
                            botones[option] = ttk.Button(ventana, text=option, command=None, width=largo_botones, style='off.TButton')

                        elif (indice == 1):
                            botones[option] = ttk.Button(ventana, text=option, command=submenu_procesar_muestras, width=largo_botones, style='on.TButton')

                        elif (indice == 16):
                            botones[option] = ttk.Button(ventana, text=option, command=submenu_excel, width=largo_botones, style='on.TButton')

                        else:
                            botones[option] = ttk.Button(ventana, text=option, command=click, width=largo_botones, style='on.TButton')

                        botones[option].place(x=90, y=separacion*(idx+1) )

                    ventana.mainloop()
                
                menu_principal_procesar_muestras()

            #####################################################################
            #Reemplazar método de análisis para un parámetro con el mismo nombre
            #   metodo_nuevo&metodo_antiguo1,metodo_antiguo2,metodo_antiguo3&cambio_u_medidad
            case 1:
                selector_ventana = None
                metodos = df_muestras["Metodo"].drop_duplicates().to_list()
                analitos = df_muestras["Analito"].drop_duplicates().to_list()

                df_requerimientos = pd.read_excel(path_lista, sheet_name="Requerimientos")

                seleccion_metodo_analisis_entrada = ""
                seleccion_metodo_analisis_entrada_lista = ['']

                seleccion_metodo_analisis_salida = ""
                
                seleccion_analisis = ""
                
                def seleccionar_elemento_entrada(event, ventana, boton):
                    global boton_agregar
                    global seleccion_metodo_analisis_entrada
                    
                    seleccion = listbox.curselection()
                    if seleccion:
                        seleccion_metodo_analisis_entrada = listbox.get(seleccion)
                        boton.config(text=f"{seleccion_metodo_analisis_entrada}")
                        boton_agregar.config(style='on.TButton', command=lambda: agregar_selector_ventana(boton, fitro_var) )
                        ventana.destroy()

                def seleccionar_elemento_salida(event, ventana, boton):
                    global seleccion_metodo_analisis_salida

                    seleccion = listbox.curselection()
                    if seleccion:
                        seleccion_metodo_analisis_salida = listbox.get(seleccion)
                        boton.config(text=f"{seleccion_metodo_analisis_salida}")
                        ventana.destroy()

                def seleccionar_elemento_analisis(event, ventana, boton):
                    global seleccion_analisis
                    
                    seleccion = listbox.curselection()
                    if seleccion:
                        seleccion_analisis = listbox.get(seleccion)
                        boton.config(text=f"{seleccion_analisis}")
                        ventana.destroy()
                        
                def mostrar_frame(tipo, boton):

                    lista_seleccion_metodos = metodos
                    seleccion_filtro = ""

                    def buscar(event=None):
                        query = entry_busqueda.get().lower().replace(" ", "-")

                        listbox.delete(0, tk.END)

                        for metodo in lista_seleccion_metodos:
                            if query in metodo.lower():
                                listbox.insert(tk.END, metodo)

                    nueva_ventana = tk.Toplevel(root)
                    nueva_ventana.title("Métodos de análisis")

                    frame = tk.Frame(nueva_ventana)
                    frame.pack(pady=20, padx=20)

                    global entry_busqueda
                    entry_busqueda = tk.Entry(frame, width=40)
                    entry_busqueda.pack(pady=5)
                    entry_busqueda.focus()
                    entry_busqueda.bind("<KeyRelease>", buscar)

                    global listbox
                    listbox = tk.Listbox(frame, width=40, height=10)
                    listbox.pack(side=tk.LEFT, fill=tk.BOTH)

                    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                    listbox.config(yscrollcommand=scrollbar.set)
                    scrollbar.config(command=listbox.yview)

                    if tipo == "entrada":
                        seleccion_filtro = seleccion_metodo_analisis_salida
                        if seleccion_filtro != "" and fitro_var.get(): 
                            seleccion_analito = df_muestras.loc[df_muestras['Metodo'] == seleccion_filtro, "Analito"].drop_duplicates().to_list()[0]
                            lista_seleccion_metodos = df_muestras.loc[df_muestras['Analito'] == seleccion_analito, "Metodo"].drop_duplicates().to_list()

                        else:    
                            lista_seleccion_metodos = metodos
                            
                        for metodo in lista_seleccion_metodos:
                            listbox.insert(tk.END, metodo)

                        listbox.bind("<Double-1>", lambda event: seleccionar_elemento_entrada(event, nueva_ventana, boton))

                    if tipo == "salida":
                        seleccion_filtro = seleccion_metodo_analisis_entrada
                        if seleccion_filtro != "" and fitro_var.get(): 
                            seleccion_analito = df_muestras.loc[df_muestras['Metodo'] == seleccion_filtro, "Analito"].drop_duplicates().to_list()[0]
                            lista_seleccion_metodos = df_muestras.loc[df_muestras['Analito'] == seleccion_analito, "Metodo"].drop_duplicates().to_list()
                        
                        else:
                            lista_seleccion_metodos = metodos

                        for metodo in lista_seleccion_metodos:
                            listbox.insert(tk.END, metodo)
                            
                        listbox.bind("<Double-1>", lambda event: seleccionar_elemento_salida(event, nueva_ventana, boton))

                    if tipo == "analisis":
                        lista_seleccion_metodos = analitos
                        for analisis in lista_seleccion_metodos:
                            listbox.insert(tk.END, analisis)
                            
                        listbox.bind("<Double-1>", lambda event: seleccionar_elemento_analisis(event, nueva_ventana, boton))

                def continuar():
                    global seleccion_metodo_analisis_entrada_lista

                    if (seleccion_metodo_analisis_entrada != "" or len(seleccion_metodo_analisis_entrada_lista) != 0) and seleccion_metodo_analisis_salida != "":

                        if seleccion_metodo_analisis_entrada == seleccion_metodo_analisis_salida:
                            messagebox.showwarning(title="Alerta",message="Favor seleccionar metodos de analisis distintos")

                        else:             
                            if seleccion_metodo_analisis_entrada != "":
                                seleccion_metodo_analisis_entrada_lista.append(seleccion_metodo_analisis_entrada)
                                
                            if seleccion_metodo_analisis_entrada_lista[0] == '':
                                seleccion_metodo_analisis_entrada_lista = [seleccion_metodo_analisis_entrada]

                            seleccion_metodo_analisis_entrada_lista = unique(seleccion_metodo_analisis_entrada_lista)

                            for metodo in seleccion_metodo_analisis_entrada_lista:
                                req_entrada = df_requerimientos.loc[df_requerimientos['Metodo'] == metodo, "AnalisRequerido"].drop_duplicates().to_list()
                                req_salida = df_requerimientos.loc[df_requerimientos['Metodo'] == seleccion_metodo_analisis_salida, "AnalisRequerido"].drop_duplicates().to_list()
                                
                                lista_requerimientos = [req for req in req_salida if req not in req_entrada]
                                lista_req_sin_uso = [req for req in req_entrada if req not in req_salida]

                                if len(lista_req_sin_uso) != 0:
                                    _tmp_str = '\n - '.join(lista_req_sin_uso)
                                    messagebox.showwarning(title="Alerta",message=f"Metodo de entrada [{metodo}] tiene requerimientos que no son necesarios para nuevo metodo [{seleccion_metodo_analisis_salida}]:\n\n - {_tmp_str}")

                                if len(lista_requerimientos) != 0:
                                    _tmp_str = '\n - '.join(lista_requerimientos)
                                    messagebox.showwarning(title="Alerta",message=f"Método {seleccion_metodo_analisis_salida} tiene {len(lista_requerimientos)} requerimientos distintos a {metodo}:\n\n - {_tmp_str}")
                            
                            print(f"{';'.join(seleccion_metodo_analisis_entrada_lista)}&{seleccion_metodo_analisis_salida}&{check_var.get()}&{seleccion_analisis}", end="")
                            root.destroy() 

                    else:
                        messagebox.showwarning(title="Alerta",message="Favor seleccionar métodos de análisis")

                def agregar_selector_ventana(cuadro_entrada, fitro_var):
                    cuadro_texto = cuadro_entrada.cget("text")
                    global listbox_2, selector_ventana
                    if selector_ventana == None:

                        def selector_reiniciar():
                            global seleccion_metodo_analisis_entrada_lista, selector_ventana
                            seleccion_metodo_analisis_entrada_lista = ['']
                            cuadro_entrada.config(text="Seleccionar Método de Entrada")
                            selector_ventana.destroy()
                            selector_ventana = None

                        def borrar_elemento(event):
                            # Obtener el índice del elemento bajo el mouse
                            global seleccion_metodo_analisis_entrada_lista

                            index = listbox_2.nearest(event.y)
                            if index >= 0:
                                listbox_2.delete(index)
                                seleccion_metodo_analisis_entrada_lista.pop(index)

                        selector_ventana = tk.Toplevel(root)
                        selector_ventana.protocol("WM_DELETE_WINDOW", selector_reiniciar)
                        selector_ventana.title("Cola de Métodos")

                        frame = tk.Frame(selector_ventana)
                        frame.pack(pady=20, padx=20)
                    
                        listbox_2 = tk.Listbox(frame, width=40, height=10)
                        listbox_2.pack(side=tk.LEFT, fill=tk.BOTH)
                        listbox_2.bind("<Double-Button-1>", borrar_elemento)
                        listbox_2.insert(tk.END, cuadro_texto)
                        
                        seleccion_metodo_analisis_entrada_lista.pop(0)
                        seleccion_metodo_analisis_entrada_lista.append(cuadro_texto)

                        # print(seleccion_metodo_analisis_entrada_lista)
                        
                        cuadro_entrada.config(text="Seleccionar Método de Entrada")
                    else:
                        fitro_var.set(False)
                        if cuadro_texto != "Seleccionar Método de Entrada" and cuadro_texto not in seleccion_metodo_analisis_entrada_lista:
                            listbox_2.insert(tk.END, cuadro_texto)
                            seleccion_metodo_analisis_entrada_lista.append(cuadro_texto)
                            # print(seleccion_metodo_analisis_entrada_lista)
                            
                        cuadro_entrada.config(text="Seleccionar Método de Entrada")
                        
                root = tk.Tk()
                mainStyle()
                
                check_var = tk.BooleanVar()
                fitro_var = tk.BooleanVar(value=True)

                root.title("Alterar metodos de análisis")
                root.geometry("400x450")

                label_metodo_entrada = tk.Label(root, text="Encontrar a:", anchor='w')
                label_metodo_entrada.pack(pady=(20,0))

                boton_metodo_entrada = tk.Button(root, text="Seleccionar Método de Entrada", width=30, command=lambda: mostrar_frame("entrada", boton_metodo_entrada) )
                boton_metodo_entrada.pack()

                boton_agregar = ttk.Button(root, text="+", style='off.TButton', width=2, command=lambda: None)
                boton_agregar.pack()

                label_metodo_salida = tk.Label(root, text="Reemplazar por:")
                label_metodo_salida.pack(pady=(20,0))

                boton_metodo_salida = tk.Button(root, text="Seleccionar Método de Salida", width=30, command=lambda: mostrar_frame("salida", boton_metodo_salida) )
                boton_metodo_salida.pack()

                filtro_checkbutton = tk.Checkbutton(root, text="Filtrar siguiente seleccion", variable=fitro_var)
                filtro_checkbutton.pack(padx=10, pady=10)

                checkbutton = tk.Checkbutton(root, text="Revisar Unidad de Medida", variable=check_var)
                checkbutton.pack(padx=10, pady=10)
                
                boton_analisis = tk.Button(root, text="Analisis (OPCIONAL)", width=30, command=lambda: mostrar_frame("analisis", boton_analisis) )
                boton_analisis.pack()

                def reiniciar():

                    global seleccion_metodo_analisis_entrada, seleccion_metodo_analisis_salida, metodos, df_requerimientos
                    
                    seleccion_metodo_analisis_entrada = ""
                    seleccion_metodo_analisis_salida = ""
                    
                    metodos = df_muestras["Metodo"].drop_duplicates().to_list()
                    df_requerimientos = pd.read_excel(path_lista, sheet_name="Requerimientos")

                    print("-2", end="")
                    root.destroy()

                boton_resetear = tk.Button(root, text="Reiniciar Seleccion", width=30, command=reiniciar)
                boton_resetear.pack(pady=(20,5))

                boton_continuar = tk.Button(root, text="Continuar", width=30, command=continuar)
                boton_continuar.pack(pady=(5,5))

                def volver():
                    print("-1", end="")
                    root.destroy()

                boton_volver = tk.Button(root, text="Volver", width=30, command=volver)
                boton_volver.pack(pady=5)

                root.mainloop()

            #####################################################################
            #Reemplazar analíto por otro con el mismo método de análisis
            #   analito_nuevo&analito_antiguo&metodo&cambio_u_medidad
            case 2:
                analisis = df_muestras["Analito"].drop_duplicates().to_list()
                metodos  = df_muestras["Metodo"].drop_duplicates().to_list()

                df_requerimientos = pd.read_excel(path_lista, sheet_name="Requerimientos")

                seleccion_analisis_entrada = ""
                seleccion_analisis_salida = ""
                seleccion_metodo = ""

                def seleccionar_elemento_entrada(event, ventana, boton):
                    global seleccion_analisis_entrada
                    seleccion = listbox.curselection()
                    if seleccion:
                        seleccion_analisis_entrada = listbox.get(seleccion)
                        boton.config(text=f"{seleccion_analisis_entrada}")
                        ventana.destroy()

                def seleccionar_elemento_salida(event, ventana, boton):
                    global seleccion_analisis_salida
                    seleccion = listbox.curselection()
                    if seleccion:
                        seleccion_analisis_salida = listbox.get(seleccion)
                        boton.config(text=f"{seleccion_analisis_salida}")
                        ventana.destroy()

                def seleccionar_elemento_metodo(event, ventana, boton):
                    global seleccion_metodo
                    seleccion = listbox.curselection()
                    if seleccion:
                        seleccion_metodo = listbox.get(seleccion)
                        boton.config(text=f"{seleccion_metodo}")
                        ventana.destroy()

                def mostrar_frame(tipo, boton):

                    def buscar(event=None):
                        query = entry_busqueda.get().lower().replace(" ", "-")

                        listbox.delete(0, tk.END)

                        for elemento in lista_seleccion:
                            if query in elemento.lower():
                                listbox.insert(tk.END, elemento)

                    nueva_ventana = tk.Toplevel(root)
                    seleccion_filtro = ""

                    if tipo == "entrada" or tipo == "salida": 
                        lista_seleccion = analisis
                        nueva_ventana.title("Analitos")

                    if tipo == "metodo": 
                        lista_seleccion = metodos
                        nueva_ventana.title("Métodos de análisis")

                    frame = tk.Frame(nueva_ventana)
                    frame.pack(pady=20, padx=20)

                    global entry_busqueda
                    entry_busqueda = tk.Entry(frame, width=40)
                    entry_busqueda.pack(pady=5)
                    entry_busqueda.focus()
                    
                    global listbox
                    listbox = tk.Listbox(frame, width=40, height=10)
                    listbox.pack(side=tk.LEFT, fill=tk.BOTH)
                    entry_busqueda.bind("<KeyRelease>", buscar)

                    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                    listbox.config(yscrollcommand=scrollbar.set)
                    scrollbar.config(command=listbox.yview)

                    if tipo == "entrada":
                        for elemento in lista_seleccion:
                            listbox.insert(tk.END, elemento)

                        listbox.bind("<Double-1>", lambda event: seleccionar_elemento_entrada(event, nueva_ventana, boton))

                    if tipo == "salida":
                        seleccion_filtro = seleccion_analisis_entrada
                        if seleccion_filtro != "" and fitro_var.get(): 
                            seleccion_filtrada = df_muestras.loc[df_muestras['Analito'] == seleccion_filtro, "Metodo"].drop_duplicates().to_list()[0]
                            lista_seleccion    = df_muestras.loc[df_muestras['Metodo'] == seleccion_filtrada, "Analito"].drop_duplicates().to_list()
                        else:
                            lista_seleccion = analisis

                        for elemento in lista_seleccion:
                            listbox.insert(tk.END, elemento)
                            
                        listbox.bind("<Double-1>", lambda event: seleccionar_elemento_salida(event, nueva_ventana, boton))

                    if tipo == "metodo":
                        seleccion_filtro = seleccion_analisis_entrada
                        if seleccion_filtro != "" and fitro_var.get(): 
                            seleccion_filtrada = df_muestras.loc[df_muestras['Analito'] == seleccion_filtro, "Analito"].drop_duplicates().to_list()[0]
                            lista_seleccion    = df_muestras.loc[df_muestras['Analito'] == seleccion_filtrada, "Metodo"].drop_duplicates().to_list()
                        else:
                            lista_seleccion = metodos

                        for elemento in lista_seleccion:
                            listbox.insert(tk.END, elemento)
                            
                        listbox.bind("<Double-1>", lambda event: seleccionar_elemento_metodo(event, nueva_ventana, boton))

                def continuar():
                
                    if seleccion_analisis_entrada == "" or seleccion_analisis_salida == "" or seleccion_metodo == "":
                        messagebox.showwarning(title="Alerta",message="Favor seleccionar ambos analitos y metodo")
                    elif seleccion_analisis_entrada == seleccion_analisis_salida:
                        messagebox.showwarning(title="Alerta",message="Favor seleccionar analitos distintos")

                    else:
                        print(f"{seleccion_analisis_entrada}&{seleccion_analisis_salida}&{seleccion_metodo}&{check_var.get()}", end="")
                        root.destroy() 

                root = tk.Tk()
                check_var = tk.BooleanVar()
                fitro_var = tk.BooleanVar(value=True)

                root.title("Reemplazar analitos")
                root.geometry("400x450")

                label_analito_entrada = tk.Label(root, text="Encontrar a:", anchor='w')
                label_analito_entrada.pack(pady=(20,0))

                boton_analito_entrada = tk.Button(root, text="Seleccionar analito de Entrada", width=30, command=lambda: mostrar_frame("entrada", boton_analito_entrada) )
                boton_analito_entrada.pack()

                label_analito_salida = tk.Label(root, text="Reemplazar por:")
                label_analito_salida.pack(pady=(20,0))

                boton_analito_salida = tk.Button(root, text="Seleccionar analito de Salida", width=30, command=lambda: mostrar_frame("salida", boton_analito_salida) )
                boton_analito_salida.pack()

                label_analito_salida = tk.Label(root, text="Con el método:")
                label_analito_salida.pack(pady=(20,0))

                boton_metodo = tk.Button(root, text="Seleccionar Método", width=30, command=lambda: mostrar_frame("metodo", boton_metodo) )
                boton_metodo.pack()

                filtro_checkbutton = tk.Checkbutton(root, text="Filtrar siguiente seleccion", variable=fitro_var)
                filtro_checkbutton.pack(padx=10, pady=10)

                checkbutton = tk.Checkbutton(root, text="Revisar Unidad de Medida", variable=check_var)
                checkbutton.pack(padx=10, pady=0)
                
                def reiniciar():
                    global seleccion_analisis_salida, seleccion_analisis_entrada, seleccion_metodo, metodos, analisis
                    
                    seleccion_analisis_salida = ""
                    seleccion_analisis_entrada = ""
                    seleccion_metodo = ""

                    metodos = df_muestras["Metodo"].drop_duplicates().to_list()
                    analisis = df_muestras["Analito"].drop_duplicates().to_list()

                    print("-2", end="")
                    root.destroy()

                boton_resetear = tk.Button(root, text="Reiniciar Seleccion", width=30, command=reiniciar)
                boton_resetear.pack(pady=(20,5))

                boton_continuar = tk.Button(root, text="Continuar", width=30, command=continuar)
                boton_continuar.pack(pady=(5,5))

                def volver():
                    print("-1", end="")
                    root.destroy()

                boton_volver = tk.Button(root, text="Volver", width=30, command=volver)
                boton_volver.pack(pady=5)

                root.mainloop()

            #####################################################################
            #Reemplazar un análisis por otro con otro método de análisis
            case 3:

                analisis = df_muestras["Analito"].drop_duplicates().to_list()
                metodos  = df_muestras["Metodo"].drop_duplicates().to_list()

                df_requerimientos = pd.read_excel(path_lista, sheet_name="Requerimientos")

                seleccion_analisis_entrada = ""
                seleccion_analisis_salida = ""

                seleccion_metodo_entrada = ""
                seleccion_metodo_salida = ""

                def seleccionar_elemento_analisis_entrada(event, ventana, boton):
                    global seleccion_analisis_entrada
                    seleccion = listbox.curselection()
                    if seleccion:
                        seleccion_analisis_entrada = listbox.get(seleccion)
                        boton.config(text=f"{seleccion_analisis_entrada}")
                        ventana.destroy()

                def seleccionar_elemento_analisis_salida(event, ventana, boton):
                    global seleccion_analisis_salida
                    seleccion = listbox.curselection()
                    if seleccion:
                        seleccion_analisis_salida = listbox.get(seleccion)
                        boton.config(text=f"{seleccion_analisis_salida}")
                        ventana.destroy()

                def seleccionar_elemento_metodo_entrada(event, ventana, boton):
                    global seleccion_metodo_entrada
                    seleccion = listbox.curselection()
                    if seleccion:
                        seleccion_metodo_entrada = listbox.get(seleccion)
                        boton.config(text=f"{seleccion_metodo_entrada}")
                        ventana.destroy()
                
                def seleccionar_elemento_metodo_salida(event, ventana, boton):
                    global seleccion_metodo_salida
                    seleccion = listbox.curselection()
                    if seleccion:
                        seleccion_metodo_salida = listbox.get(seleccion)
                        boton.config(text=f"{seleccion_metodo_salida}")
                        ventana.destroy()

                def mostrar_frame(tipo, boton):

                    def buscar(event=None):
                        query = entry_busqueda.get().lower().replace(" ", "-")

                        listbox.delete(0, tk.END)

                        for elemento in lista_seleccion:
                            if query in elemento.lower():
                                listbox.insert(tk.END, elemento)

                    nueva_ventana = tk.Toplevel(root)
                    seleccion_filtro = ""

                    if tipo == "a_entrada" or tipo == "a_salida": 
                        lista_seleccion = analisis
                        nueva_ventana.title("Analitos")

                    if tipo == "m_entrada" or tipo == "m_salida": 
                        lista_seleccion = metodos
                        nueva_ventana.title("Métodos de análisis")

                    frame = tk.Frame(nueva_ventana)
                    frame.pack(pady=20, padx=20)

                    global entry_busqueda
                    entry_busqueda = tk.Entry(frame, width=40)
                    entry_busqueda.pack(pady=5)
                    entry_busqueda.focus()
                    entry_busqueda.bind("<KeyRelease>", buscar)
                    
                    global listbox
                    listbox = tk.Listbox(frame, width=40, height=10)
                    listbox.pack(side=tk.LEFT, fill=tk.BOTH)

                    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                    listbox.config(yscrollcommand=scrollbar.set)
                    scrollbar.config(command=listbox.yview)

                    if tipo == "a_entrada":

                        seleccion_filtro = seleccion_metodo_entrada
                        if seleccion_filtro != "" and fitro_var.get(): 
                            seleccion_filtrada = df_muestras.loc[df_muestras['Metodo'] == seleccion_filtro, "Metodo"].drop_duplicates().to_list()[0]
                            lista_seleccion    = df_muestras.loc[df_muestras['Metodo'] == seleccion_filtrada, "Analito"].drop_duplicates().to_list()
                        else:
                            lista_seleccion = analisis
                    
                        for elemento in lista_seleccion:
                            listbox.insert(tk.END, elemento)
                        listbox.bind("<Double-1>", lambda event: seleccionar_elemento_analisis_entrada(event, nueva_ventana, boton))

                    if tipo == "a_salida":

                        seleccion_filtro = seleccion_metodo_salida
                        if seleccion_filtro != "" and fitro_var.get(): 
                            seleccion_filtrada = df_muestras.loc[df_muestras['Metodo'] == seleccion_filtro, "Metodo"].drop_duplicates().to_list()[0]
                            lista_seleccion    = df_muestras.loc[df_muestras['Metodo'] == seleccion_filtrada, "Analito"].drop_duplicates().to_list()
                        else:
                            lista_seleccion = analisis

                        for elemento in lista_seleccion:
                            listbox.insert(tk.END, elemento)
                        listbox.bind("<Double-1>", lambda event: seleccionar_elemento_analisis_salida(event, nueva_ventana, boton))

                    if tipo == "m_entrada":
                        
                        seleccion_filtro = seleccion_analisis_entrada
                        if seleccion_filtro != "" and fitro_var.get(): 
                            seleccion_filtrada = df_muestras.loc[df_muestras['Analito'] == seleccion_filtro, "Analito"].drop_duplicates().to_list()[0]
                            lista_seleccion    = df_muestras.loc[df_muestras['Analito'] == seleccion_filtrada, "Metodo"].drop_duplicates().to_list()
                        else:    
                            lista_seleccion = metodos

                        for elemento in lista_seleccion:
                            listbox.insert(tk.END, elemento)
                        listbox.bind("<Double-1>", lambda event: seleccionar_elemento_metodo_entrada(event, nueva_ventana, boton))

                    if tipo == "m_salida":

                        seleccion_filtro = seleccion_analisis_salida
                        if seleccion_filtro != "" and fitro_var.get(): 
                            seleccion_filtrada = df_muestras.loc[df_muestras['Analito'] == seleccion_filtro, "Analito"].drop_duplicates().to_list()[0]
                            lista_seleccion    = df_muestras.loc[df_muestras['Analito'] == seleccion_filtrada, "Metodo"].drop_duplicates().to_list()
                        else:    
                            lista_seleccion = metodos

                        for elemento in lista_seleccion:
                            listbox.insert(tk.END, elemento) 
                        listbox.bind("<Double-1>", lambda event: seleccionar_elemento_metodo_salida(event, nueva_ventana, boton))

                def continuar(): 
                    if seleccion_analisis_entrada == "" or seleccion_analisis_salida == "" or seleccion_metodo_entrada == "" or seleccion_metodo_salida == "":
                        messagebox.showwarning(title="Alerta",message="Favor seleccionar todos los analitos y metodos")
                    elif seleccion_analisis_entrada == seleccion_analisis_salida:
                        messagebox.showwarning(title="Alerta",message="Favor seleccionar analitos distintos")
                    elif seleccion_metodo_entrada == seleccion_metodo_salida:
                        messagebox.showwarning(title="Alerta",message="Favor seleccionar metodos distintos")

                    else:
                        print(f"{seleccion_analisis_entrada}&{seleccion_analisis_salida}&{seleccion_metodo_entrada}&{seleccion_metodo_salida}&{check_var.get()}", end="")
                        root.destroy() 

                root = tk.Tk()
                check_var = tk.BooleanVar()
                fitro_var = tk.BooleanVar(value=True)

                root.title("Reemplazar analitos")
                root.geometry("400x500")

                label_analito_entrada = tk.Label(root, text="Encontrar a:", anchor='w')
                label_analito_entrada.pack(pady=(15,0))

                boton_analito_entrada = tk.Button(root, text="Seleccionar analito de Entrada", width=30, command=lambda: mostrar_frame("a_entrada", boton_analito_entrada) )
                boton_analito_entrada.pack()

                label_analito_salida = tk.Label(root, text="Con metodo:")
                label_analito_salida.pack(pady=(10,0))

                boton_metodo_entrada = tk.Button(root, text="Seleccionar metodo de Entrada", width=30, command=lambda: mostrar_frame("m_entrada", boton_metodo_entrada) )
                boton_metodo_entrada.pack()

                label_analito_entrada = tk.Label(root, text="Reemplazar por:", anchor='w')
                label_analito_entrada.pack(pady=(35,0))
                
                boton_analito_salida = tk.Button(root, text="Seleccionar analito de Salida", width=30, command=lambda: mostrar_frame("a_salida", boton_analito_salida) )
                boton_analito_salida.pack()

                label_analito_salida = tk.Label(root, text="Con metodo:")
                label_analito_salida.pack(pady=(10,0))

                boton_metodo_salida = tk.Button(root, text="Seleccionar metodo de Salida", width=30, command=lambda: mostrar_frame("m_salida", boton_metodo_salida) )
                boton_metodo_salida.pack()

                filtro_checkbutton = tk.Checkbutton(root, text="Filtrar siguiente seleccion", variable=fitro_var)
                filtro_checkbutton.pack(padx=10, pady=10)

                checkbutton = tk.Checkbutton(root, text="Revisar Unidad de Medida", variable=check_var)
                checkbutton.pack(padx=10, pady=0)
                
                def reiniciar():
                    global seleccion_analisis_entrada, seleccion_analisis_salida, seleccion_metodo_entrada, seleccion_metodo_salida, metodos, analisis
                    
                    seleccion_analisis_entrada = ""
                    seleccion_analisis_salida = ""
                    seleccion_metodo_entrada = ""
                    seleccion_metodo_salida = ""

                    analisis = df_muestras["Analito"].drop_duplicates().to_list()
                    metodos  = df_muestras["Metodo"].drop_duplicates().to_list()

                    print("-2", end="")
                    root.destroy()

                boton_resetear = tk.Button(root, text="Reiniciar Seleccion", width=30, command=reiniciar)
                boton_resetear.pack(pady=(20,5))

                boton_continuar = tk.Button(root, text="Continuar", width=30, command=continuar)
                boton_continuar.pack(pady=(5,5))

                def volver():
                    print("-1", end="")
                    root.destroy()

                boton_volver = tk.Button(root, text="Volver", width=30, command=volver)
                boton_volver.pack(pady=5)

                root.mainloop()

            #####################################################################
            #Agregar análisis a muestras en lista
            case 4:
                metodos = df_muestras["Metodo"].drop_duplicates().to_list()
                analisis = df_muestras["Analito"].drop_duplicates().to_list()

                seleccion_metodo_entrada = ""
                seleccion_analisis_entrada = ""

                def seleccionar_metodo(event, ventana, boton):
                    global seleccion_metodo_entrada, analisis
                    seleccion = listbox.curselection()
                    if seleccion:
                        seleccion_metodo_entrada = listbox.get(seleccion)
                        analisis = df_muestras.loc[df_muestras['Metodo'] == seleccion_metodo_entrada, 'Analito'].drop_duplicates().to_list()

                        boton.config(text=f"{seleccion_metodo_entrada}")
                        ventana.destroy()

                def seleccionar_analisis(event, ventana, boton):
                    global seleccion_analisis_entrada, metodos
                    seleccion = listbox.curselection()
                    if seleccion:
                        seleccion_analisis_entrada = listbox.get(seleccion)
                        metodos = df_muestras.loc[df_muestras['Analito'] == seleccion_analisis_entrada, 'Metodo'].drop_duplicates().to_list()

                        boton.config(text=f"{seleccion_analisis_entrada}")
                        ventana.destroy()

                def buscar(event, tipo):
                    query = entry_busqueda.get().lower().replace(" ", "-")
                    listbox.delete(0, tk.END)
                    
                    if tipo == "metodo":
                        elementos = metodos
                    if tipo == "analisis":
                        elementos = analisis

                    for elemento in elementos:
                        if query in elemento.lower():
                            listbox.insert(tk.END, elemento)

                def mostrar_frame(tipo, boton):

                    nueva_ventana = tk.Toplevel(root)
                    seleccion_filtro = ""

                    if tipo == "metodo": 
                        lista_seleccion = metodos
                        nueva_ventana.title("Métodos de análisis")

                    if tipo == "analisis": 
                        lista_seleccion = analisis
                        nueva_ventana.title("Analitos")

                    frame = tk.Frame(nueva_ventana)
                    frame.pack(pady=20, padx=20)

                    global entry_busqueda
                    entry_busqueda = tk.Entry(frame, width=40)
                    entry_busqueda.pack(pady=5)
                    entry_busqueda.focus()
                    entry_busqueda.bind("<KeyRelease>", lambda event: buscar(event, tipo))
                    
                    global listbox
                    listbox = tk.Listbox(frame, width=40, height=10)
                    listbox.pack(side=tk.LEFT, fill=tk.BOTH)

                    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                    listbox.config(yscrollcommand=scrollbar.set)
                    scrollbar.config(command=listbox.yview)

                    if tipo == "metodo":
                        seleccion_filtro = seleccion_analisis_entrada
                        if seleccion_filtro != "" and fitro_var.get(): 
                            seleccion_filtrada = df_muestras.loc[df_muestras['Analito'] == seleccion_filtro, "Analito"].drop_duplicates().to_list()[0]
                            lista_seleccion    = df_muestras.loc[df_muestras['Analito'] == seleccion_filtrada, "Metodo"].drop_duplicates().to_list()
                        else:
                            lista_seleccion = metodos
                        
                        for metodo in lista_seleccion:
                            listbox.insert(tk.END, metodo)
                        
                        listbox.bind("<Double-1>", lambda event: seleccionar_metodo(event, nueva_ventana, boton))

                    if tipo == "analisis":
                        seleccion_filtro = seleccion_metodo_entrada
                        if seleccion_filtro != "" and fitro_var.get(): 
                            seleccion_filtrada = df_muestras.loc[df_muestras['Metodo'] == seleccion_filtro, "Metodo"].drop_duplicates().to_list()[0]
                            lista_seleccion    = df_muestras.loc[df_muestras['Metodo'] == seleccion_filtrada, "Analito"].drop_duplicates().to_list()
                        else:
                            lista_seleccion = analisis
                            
                        for analito in lista_seleccion:
                            listbox.insert(tk.END, analito)

                        listbox.bind("<Double-1>", lambda event: seleccionar_analisis(event, nueva_ventana, boton))

                #Revisar requerimientos y preguntar para cada uno
                def continuar():
                    
                    if seleccion_metodo_entrada != "" and seleccion_analisis_entrada != "":
                        
                        lista_requerimientos = df_requerimientos.loc[df_requerimientos['Metodo'] == seleccion_metodo_entrada, "AnalisRequerido"].drop_duplicates().to_list()
                        null_reqs = df_requerimientos[ (df_requerimientos['MetodoRequerido'].isnull()) ]
                        
                        if len(lista_requerimientos) == 0:
                            print(f"{seleccion_metodo_entrada}&{seleccion_analisis_entrada}", end="")
                            root.destroy()
                            
                        else:
                            _tmp_str = '\n - '.join(lista_requerimientos)
                            messagebox.showinfo(title="Alerta",message=f"Se necesita asociar método a {len(lista_requerimientos)} requerimientos:\n\n - {_tmp_str}")
                            
                            dict_seleccion = {}
                            for req in lista_requerimientos:

                                es_null = len(null_reqs[ (null_reqs["Metodo"] == seleccion_metodo_entrada) & (null_reqs["AnalisRequerido"] == req)])
                                
                                opciones = df_muestras.loc[df_muestras['Analito'] == req]["Metodo"].to_list()

                                nueva_ventana = tk.Toplevel(root)
                                nueva_ventana.title("Requerimientos")

                                frame = tk.Frame(nueva_ventana)
                                frame.pack(pady=20, padx=20)
                                
                                label_metodo_asociar = tk.Label(frame, text=f"Asociar a {req}", anchor='w')
                                label_metodo_asociar.pack(fill=tk.Y, expand=True)

                                tkLista = tk.Listbox(frame, width=40, height=10)
                                tkLista.pack(side=tk.TOP, fill=tk.NONE)

                                if not es_null:
                                    metodo_de_requerimiento = df_requerimientos[
                                                                                (df_requerimientos["AnalisRequerido"] == req ) & 
                                                                                (df_requerimientos["MetodoRequerido"].notnull()) & 
                                                                                (df_requerimientos["Metodo"] == seleccion_metodo_entrada) 
                                                            ]["MetodoRequerido"].to_string(index=False)
                                    
                                    label_metodo_req = tk.Label(frame, text=f"Analisis {req} preestablecido a {metodo_de_requerimiento}", anchor='w')
                                    label_metodo_req.pack(side=tk.TOP, fill=tk.X)

                                for metodo in opciones:
                                    tkLista.insert(tk.END, metodo)
                                
                                def seleccionar(event, ventana, diccionario):
                                    seleccion = tkLista.curselection()

                                    if seleccion:
                                        indice = seleccion[0]
                                        diccionario[req] = tkLista.get(indice)
                                        ventana.destroy()
                                
                                tkLista.bind("<Double-1>", lambda event: seleccionar(event, nueva_ventana, dict_seleccion))
                                root.wait_window(nueva_ventana)
                            
                            p_salida = f"{seleccion_metodo_entrada}&{seleccion_analisis_entrada}"
                            p_alerta = "Se cambiarán las siguientes asociaciones:\n\n"
                            
                            for llave, valor in dict_seleccion.items():
                                p_salida=f"{p_salida}|{llave}&{valor}"
                                p_alerta=f"{p_alerta}- {llave}: {valor}\n"

                            messagebox.showinfo(title="Alerta",message=p_alerta)
                            print(p_salida, end="")
                            root.destroy()
                    else:
                        messagebox.showwarning(title="Alerta",message="Favor marcar opción para continuar")

                root = tk.Tk()
                fitro_var = tk.BooleanVar(value=True)

                root.title("Alterar metodos de análisis")
                root.geometry("400x350")

                label_metodo_entrada = tk.Label(root, text="Agregar Método:", anchor='w')
                label_metodo_entrada.pack(pady=(20,0))

                boton_metodo_entrada = tk.Button(root, text="Seleccionar Método de Entrada", width=30, command=lambda: mostrar_frame("metodo", boton_metodo_entrada) )
                boton_metodo_entrada.pack()

                label_metodo_salida = tk.Label(root, text="Agregar Análisis:")
                label_metodo_salida.pack(pady=(20,0))

                boton_metodo_salida = tk.Button(root, text="Seleccionar Análisis de Entrada", width=30, command=lambda: mostrar_frame("analisis", boton_metodo_salida) )
                boton_metodo_salida.pack()
                
                filtro_checkbutton = tk.Checkbutton(root, text="Filtrar siguiente seleccion", variable=fitro_var)
                filtro_checkbutton.pack(padx=10, pady=10)

                def reiniciar():
                    global seleccion_metodo_entrada, seleccion_analisis_entrada, metodos, analisis
                    seleccion_metodo_entrada = ""
                    seleccion_analisis_entrada = ""

                    metodos = df_muestras["Metodo"].drop_duplicates().to_list()
                    analisis = df_muestras["Analito"].drop_duplicates().to_list()

                    print("-2", end="")
                    root.destroy()

                boton_resetear = tk.Button(root, text="Reiniciar Seleccion", width=30, command=reiniciar)
                boton_resetear.pack(pady=(25,5))

                boton_continuar = tk.Button(root, text="Continuar", width=30, command=continuar)
                boton_continuar.pack(pady=5)

                def volver():
                    print("-1", end="")
                    root.destroy()

                boton_volver = tk.Button(root, text="Volver", width=30, command=volver)
                boton_volver.pack(pady=5)
                
                root.mainloop()

            #####################################################################
            #Eliminar método de muestras en lista
            case 5:
                metodos = df_muestras["Metodo"].drop_duplicates().to_list()

                seleccion_metodo_entrada = ""

                def seleccionar_metodo(event, ventana, boton):
                    global seleccion_metodo_entrada, analisis
                    seleccion = listbox.curselection()
                    if seleccion:
                        seleccion_metodo_entrada = listbox.get(seleccion)
                        analisis = df_muestras.loc[df_muestras['Metodo'] == seleccion_metodo_entrada, 'Analito'].drop_duplicates().to_list()

                        boton.config(text=f"{seleccion_metodo_entrada}")
                        ventana.destroy()


                def buscar(event, tipo):
                    query = entry_busqueda.get().lower().replace(" ", "-")
                    listbox.delete(0, tk.END)

                    elementos = metodos

                    for elemento in elementos:
                        if query in elemento.lower():
                            listbox.insert(tk.END, elemento)

                def mostrar_frame(tipo, boton):

                    nueva_ventana = tk.Toplevel(root)
                    seleccion_filtro = ""

                    lista_seleccion = metodos
                    nueva_ventana.title("Métodos de análisis")

                    frame = tk.Frame(nueva_ventana)
                    frame.pack(pady=20, padx=20)

                    global entry_busqueda
                    entry_busqueda = tk.Entry(frame, width=40)
                    entry_busqueda.pack(pady=5)
                    entry_busqueda.focus()
                    entry_busqueda.bind("<KeyRelease>", lambda event: buscar(event, tipo))
                    
                    global listbox
                    listbox = tk.Listbox(frame, width=40, height=10)
                    listbox.pack(side=tk.LEFT, fill=tk.BOTH)

                    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
                    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                    listbox.config(yscrollcommand=scrollbar.set)
                    scrollbar.config(command=listbox.yview)

                    if tipo == "metodo":
                        lista_seleccion = metodos
                        for metodo in lista_seleccion:
                            listbox.insert(tk.END, metodo)
                        
                        listbox.bind("<Double-1>", lambda event: seleccionar_metodo(event, nueva_ventana, boton))


                #Revisar requerimientos y preguntar para cada uno
                def continuar():
                    
                    if seleccion_metodo_entrada != "":
                        
                        lista_requerimientos = df_requerimientos.loc[df_requerimientos['Metodo'] == seleccion_metodo_entrada, "AnalisRequerido"].drop_duplicates().to_list()
                        
                        if len(lista_requerimientos) == 0:
                            print(f"{seleccion_metodo_entrada}", end="")
                            root.destroy()
                            
                        else:
                            messagebox.showinfo(title="Alerta",message=f"Alerta de método con {len(lista_requerimientos)} requerimientos")
                            print(f"{seleccion_metodo_entrada}", end="")
                            root.destroy()
                    else:
                        messagebox.showwarning(title="Alerta",message="Favor marcar opción para continuar")

                root = tk.Tk()
                fitro_var = tk.BooleanVar(value=True)

                root.title("Eliminar metodos de análisis")
                root.geometry("400x270")

                label_metodo_entrada = tk.Label(root, text="Método a eliminar:", anchor='w')
                label_metodo_entrada.pack(pady=(20,0))

                boton_metodo_entrada = tk.Button(root, text="Seleccionar Método de Entrada", width=30, command=lambda: mostrar_frame("metodo", boton_metodo_entrada) )
                boton_metodo_entrada.pack()

                def reiniciar():
                    global seleccion_metodo_entrada, metodos
                    seleccion_metodo_entrada = ""

                    metodos = df_muestras["Metodo"].drop_duplicates().to_list()

                    print("-2", end="")
                    root.destroy()

                boton_resetear = tk.Button(root, text="Reiniciar Seleccion", width=30, command=reiniciar)
                boton_resetear.pack(pady=(25,5))

                boton_continuar = tk.Button(root, text="Continuar", width=30, command=continuar)
                boton_continuar.pack(pady=5)

                def volver():
                    print("-1", end="")
                    root.destroy()

                boton_volver = tk.Button(root, text="Volver", width=30, command=volver)
                boton_volver.pack(pady=5)
                
                root.mainloop()