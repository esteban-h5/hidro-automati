import sys,os

file_name           =   os.path.basename(__file__)
CM_wd               =   os.path.dirname(os.path.realpath(__file__))
internal_lib        =   os.path.normpath(os.path.join(CM_wd,"..","internal_lib"))

sys.path.insert(0, internal_lib)

from __myLIMS_modulos__ import (
  datetime, get, version_actual, GetConfig, paisDICT, DeltaTimer,
  MensajeInicial, filedialog, pd, notify, sleep, FormatoExcepcion
)

from __myLIMS_API__ import (
  log_status, api_post,json, get_pricetable, 
  SampleAnalysisInsert, FormatoDF
)

from __ficheros_modulos__ import (
  FilaAgregarXLSX, ListaMuestraXLSX, 
  obtener_llave_por_valor
)

fecha = datetime.now().strftime('%Y_%m_%d-%H_%M')
token = get('mylims_app', 'secret7')

file_name = os.path.basename(__file__)
file_path = os.path.join(CM_wd,"") #Excel entrada
nombreLOG = os.path.join(CM_wd,"log", f"reporte_{fecha}" )

eprint = print

try:

    if not os.path.isdir( os.path.join(CM_wd,"log") ): os.mkdir(os.path.join(CM_wd,"log"))

    def eprint(string="", end="\n"):
        utf = str(string).replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
        print(f"\n{datetime.now().strftime(f'[%H:%M:%S] [{version_actual}]')}\n"+utf, end=end, file=sys.stderr)
        print(string, end=end)

    def logprint(string="", end="\n"):
        utf = str(string).replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
        print(f"\n{datetime.now().strftime(f'[%H:%M:%S] [{version_actual}] [log]')}\n"+utf, end=end, file=sys.stderr)

    log_file = open(nombreLOG+".txt", "a")
    sys.stderr = log_file

    def slog():
        print(f"\n{datetime.now().strftime(f'[%H:%M:%S] [LOG RECARGADO] [log]')}", file=sys.stderr)
        global log_file
        log_file.flush()
        log_file.close()
        log_file = open(nombreLOG+".txt", "a")
        sys.stderr = log_file

    config          = GetConfig( dirConfig=os.path.join(CM_wd,"config.txt"))
    global_config   = GetConfig( dirConfig=os.path.join(internal_lib,"global_config.txt") )
    
    keys_usadas = [
        "MostrarJSON", "ExcelEntrada", "ExcelObjetivo", "COL-std_id_muestra", "Partition", "ListaPrecio",
        "SCL-HojaIM", "SCL-COL-indice_m", "SCL-COL-id_muestras", "SCL-COL-identificacion", "SCL-COL-matriz", "SCL-COL-empresa", "SCL-COL-cuenta_relacionada", "SCL-COL-motivo", "SCL-COL-cliente_solicitante", "SCL-COL-lugar_muestreo", "SCL-COL-punto_muestreo", "SCL-COL-direccion_muestreo", "SCL-COL-estado", "SCL-COL-municipio", "SCL-COL-siralab", "SCL-COL-instrumento_ambiental", "SCL-COL-tipo_muestreo", "SCL-COL-consultora", "SCL-COL-coordenadas", "SCL-COL-resp_muestreo", "SCL-COL-frecuencia", "SCL-COL-proyecto", "SCL-COL-region", "SCL-COL-departamento", "SCL-COL-comuna", "SCL-COL-etfa", "SCL-COL-tabla_comp", "SCL-HojaA", "SCL-COL-indice_a", "SCL-COL-metodo_id", "SCL-COL-grupo_id", "SCL-COL-analisis_id", "SCL-COL-u_medida_id", "SCL-HojaIM", "SCL-COL-indice_m", "SCL-COL-id_muestras", "SCL-COL-identificacion", "SCL-COL-matriz", "SCL-COL-empresa", "SCL-COL-cuenta_relacionada", "SCL-COL-motivo", "SCL-COL-cliente_solicitante", "SCL-COL-lugar_muestreo", "SCL-COL-punto_muestreo", "SCL-COL-direccion_muestreo", "SCL-COL-estado", "SCL-COL-municipio", "SCL-COL-siralab", "SCL-COL-instrumento_ambiental", "SCL-COL-tipo_muestreo", "SCL-COL-consultora", "SCL-COL-coordenadas", "SCL-COL-resp_muestreo", "SCL-COL-frecuencia", "SCL-COL-proyecto", "SCL-COL-region", "SCL-COL-departamento", "SCL-COL-comuna", "SCL-COL-etfa", "SCL-COL-tabla_comp", "SCL-HojaA", "SCL-COL-indice_a", "SCL-COL-metodo_id", "SCL-COL-grupo_id", "SCL-COL-analisis_id", "SCL-COL-u_medida_id", 
        "MTY-HojaIM", "MTY-COL-indice_m", "MTY-COL-id_muestras", "MTY-COL-identificacion", "MTY-COL-matriz", "MTY-COL-empresa", "MTY-COL-cuenta_relacionada", "MTY-COL-motivo", "MTY-COL-cliente_solicitante", "MTY-COL-lugar_muestreo", "MTY-COL-punto_muestreo", "MTY-COL-direccion_muestreo", "MTY-COL-estado", "MTY-COL-municipio", "MTY-COL-siralab", "MTY-COL-instrumento_ambiental", "MTY-COL-tipo_muestreo", "MTY-COL-consultora", "MTY-COL-coordenadas", "MTY-COL-resp_muestreo", "MTY-COL-frecuencia", "MTY-COL-proyecto", "MTY-COL-region", "MTY-COL-departamento", "MTY-COL-comuna", "MTY-COL-etfa", "MTY-COL-tabla_comp", "MTY-HojaA", "MTY-COL-indice_a", "MTY-COL-metodo_id", "MTY-COL-grupo_id", "MTY-COL-analisis_id", "MTY-COL-u_medida_id", "MTY-HojaIM", "MTY-COL-indice_m", "MTY-COL-id_muestras", "MTY-COL-identificacion", "MTY-COL-matriz", "MTY-COL-empresa", "MTY-COL-cuenta_relacionada", "MTY-COL-motivo", "MTY-COL-cliente_solicitante", "MTY-COL-lugar_muestreo", "MTY-COL-punto_muestreo", "MTY-COL-direccion_muestreo", "MTY-COL-estado", "MTY-COL-municipio", "MTY-COL-siralab", "MTY-COL-instrumento_ambiental", "MTY-COL-tipo_muestreo", "MTY-COL-consultora", "MTY-COL-coordenadas", "MTY-COL-resp_muestreo", "MTY-COL-frecuencia", "MTY-COL-proyecto", "MTY-COL-region", "MTY-COL-departamento", "MTY-COL-comuna", "MTY-COL-etfa", "MTY-COL-tabla_comp", "MTY-HojaA", "MTY-COL-indice_a", "MTY-COL-metodo_id", "MTY-COL-grupo_id", "MTY-COL-analisis_id", "MTY-COL-u_medida_id", 
        "LIM-HojaIM", "LIM-COL-indice_m", "LIM-COL-id_muestras", "LIM-COL-identificacion", "LIM-COL-matriz", "LIM-COL-empresa", "LIM-COL-cuenta_relacionada", "LIM-COL-motivo", "LIM-COL-cliente_solicitante", "LIM-COL-lugar_muestreo", "LIM-COL-punto_muestreo", "LIM-COL-direccion_muestreo", "LIM-COL-estado", "LIM-COL-municipio", "LIM-COL-siralab", "LIM-COL-instrumento_ambiental", "LIM-COL-tipo_muestreo", "LIM-COL-consultora", "LIM-COL-coordenadas", "LIM-COL-resp_muestreo", "LIM-COL-frecuencia", "LIM-COL-proyecto", "LIM-COL-region", "LIM-COL-departamento", "LIM-COL-comuna", "LIM-COL-etfa", "LIM-COL-tabla_comp", "LIM-HojaA", "LIM-COL-indice_a", "LIM-COL-metodo_id", "LIM-COL-grupo_id", "LIM-COL-analisis_id", "LIM-COL-u_medida_id", "LIM-HojaIM", "LIM-COL-indice_m", "LIM-COL-id_muestras", "LIM-COL-identificacion", "LIM-COL-matriz", "LIM-COL-empresa", "LIM-COL-cuenta_relacionada", "LIM-COL-motivo", "LIM-COL-cliente_solicitante", "LIM-COL-lugar_muestreo", "LIM-COL-punto_muestreo", "LIM-COL-direccion_muestreo", "LIM-COL-estado", "LIM-COL-municipio", "LIM-COL-siralab", "LIM-COL-instrumento_ambiental", "LIM-COL-tipo_muestreo", "LIM-COL-consultora", "LIM-COL-coordenadas", "LIM-COL-resp_muestreo", "LIM-COL-frecuencia", "LIM-COL-proyecto", "LIM-COL-region", "LIM-COL-departamento", "LIM-COL-comuna", "LIM-COL-etfa", "LIM-COL-tabla_comp", "LIM-HojaA", "LIM-COL-indice_a", "LIM-COL-metodo_id", "LIM-COL-grupo_id", "LIM-COL-analisis_id", "LIM-COL-u_medida_id", 
        "BOG-HojaIM", "BOG-COL-indice_m", "BOG-COL-id_muestras", "BOG-COL-identificacion", "BOG-COL-matriz", "BOG-COL-empresa", "BOG-COL-cuenta_relacionada", "BOG-COL-motivo", "BOG-COL-cliente_solicitante", "BOG-COL-lugar_muestreo", "BOG-COL-punto_muestreo", "BOG-COL-direccion_muestreo", "BOG-COL-estado", "BOG-COL-municipio", "BOG-COL-siralab", "BOG-COL-instrumento_ambiental", "BOG-COL-tipo_muestreo", "BOG-COL-consultora", "BOG-COL-coordenadas", "BOG-COL-resp_muestreo", "BOG-COL-frecuencia", "BOG-COL-proyecto", "BOG-COL-region", "BOG-COL-departamento", "BOG-COL-comuna", "BOG-COL-etfa", "BOG-COL-tabla_comp", "BOG-HojaA", "BOG-COL-indice_a", "BOG-COL-metodo_id", "BOG-COL-grupo_id", "BOG-COL-analisis_id", "BOG-COL-u_medida_id", "BOG-HojaIM", "BOG-COL-indice_m", "BOG-COL-id_muestras", "BOG-COL-identificacion", "BOG-COL-matriz", "BOG-COL-empresa", "BOG-COL-cuenta_relacionada", "BOG-COL-motivo", "BOG-COL-cliente_solicitante", "BOG-COL-lugar_muestreo", "BOG-COL-punto_muestreo", "BOG-COL-direccion_muestreo", "BOG-COL-estado", "BOG-COL-municipio", "BOG-COL-siralab", "BOG-COL-instrumento_ambiental", "BOG-COL-tipo_muestreo", "BOG-COL-consultora", "BOG-COL-coordenadas", "BOG-COL-resp_muestreo", "BOG-COL-frecuencia", "BOG-COL-proyecto", "BOG-COL-region", "BOG-COL-departamento", "BOG-COL-comuna", "BOG-COL-etfa", "BOG-COL-tabla_comp", "BOG-HojaA", "BOG-COL-indice_a", "BOG-COL-metodo_id", "BOG-COL-grupo_id", "BOG-COL-analisis_id", "BOG-COL-u_medida_id"
        ]
    
    keys_used_g = ["paisActual", "ActivarLOG", "api-url"]

    for key in keys_used_g:
        if key not in global_config.keys():
            input(f"Valor de config \'{key}\' no encontrado en archivo global_config, enter para continuar igualmente...")

    for key in keys_usadas:
       if key not in config.keys():
            input(f"Valor de config \'{key}\' no encontrado en archivo config, enter para continuar igualmente...")

    paisActual      = global_config.get("paisActual", "").replace("é","e").replace("ú","u").lower()
    pais_prefijo    = paisDICT[paisActual]

    log             = global_config.get("ActivarLOG", True)
    APIdomain       = global_config.get("api-url", "")

    MostrarJSON     = config.get("MostrarJSON", False)
    ListaPrecio     = config.get("ListaPrecio", 0)
    
    Partition       = config.get("Partition", 50)

    ExcelEntrada    = config.get("ExcelEntrada", "")
    ExcelObjetivo   = config.get("ExcelObjetivo", "")

    HojaIM          = config.get(f"{pais_prefijo}-HojaIM", "")
    HojaA           = config.get(f"{pais_prefijo}-HojaA", "")

    col_fmt = {
        #Muestras
        "col-indice_m"              : config.get(f"{pais_prefijo}-COL-indice_m", "").lower(),
        "col-id_muestras"           : config.get(f"{pais_prefijo}-COL-id_muestras", "").lower(),
        "col-identificacion"        : config.get(f"{pais_prefijo}-COL-identificacion", "").lower(),
        "col-matriz"                : config.get(f"{pais_prefijo}-COL-matriz", "").lower(),
        "col-empresa"               : config.get(f"{pais_prefijo}-COL-empresa", "").lower(),
        "col-cuenta_relacionada"    : config.get(f"{pais_prefijo}-COL-cuenta_relacionada", "").lower(),
        "col-motivo"                : config.get(f"{pais_prefijo}-COL-motivo", "").lower(),
        "col-cliente_solicitante"   : config.get(f"{pais_prefijo}-COL-cliente_solicitante", "").lower(),
        "col-lugar_muestreo"        : config.get(f"{pais_prefijo}-COL-lugar_muestreo", "").lower(),
        "col-punto_muestreo"        : config.get(f"{pais_prefijo}-COL-punto_muestreo", "").lower(),
        "col-direccion_muestreo"    : config.get(f"{pais_prefijo}-COL-direccion_muestreo", "").lower(),
        "col-estado"                : config.get(f"{pais_prefijo}-COL-estado", "").lower(),
        "col-municipio"             : config.get(f"{pais_prefijo}-COL-municipio", "").lower(),
        "col-siralab"               : config.get(f"{pais_prefijo}-COL-siralab", "").lower(),
        "col-instrumento_ambiental" : config.get(f"{pais_prefijo}-COL-instrumento_ambiental", "").lower(),
        "col-tipo_muestreo"         : config.get(f"{pais_prefijo}-COL-tipo_muestreo", "").lower(),
        "col-consultora"            : config.get(f"{pais_prefijo}-COL-consultora", "").lower(),
        "col-coordenadas"           : config.get(f"{pais_prefijo}-COL-coordenadas", "").lower(),
        "col-resp_muestreo"         : config.get(f"{pais_prefijo}-COL-resp_muestreo", "").lower(),
        "col-frecuencia"            : config.get(f"{pais_prefijo}-COL-frecuencia", "").lower(),
        "col-proyecto"              : config.get(f"{pais_prefijo}-COL-proyecto", "").lower(),
        "col-region"                : config.get(f"{pais_prefijo}-COL-region", "").lower(),
        "col-departamento"          : config.get(f"{pais_prefijo}-COL-departamento", "").lower(),
        "col-comuna"                : config.get(f"{pais_prefijo}-COL-comuna", "").lower(),
        "col-etfa"                  : config.get(f"{pais_prefijo}-COL-etfa", "").lower(),
        "col-tabla_comp"            : config.get(f"{pais_prefijo}-COL-tabla_comp", "").lower(),

        #Analisis
        "col-indice_a"              : config.get(f"{pais_prefijo}-COL-indice_a", "").lower(),
        "col-metodo_id"             : config.get(f"{pais_prefijo}-COL-metodo_id", "").lower(),
        "col-grupo_id"              : config.get(f"{pais_prefijo}-COL-grupo_id", "").lower(),
        "col-analisis_id"           : config.get(f"{pais_prefijo}-COL-analisis_id", "").lower(),
        "col-u_medida_id"           : config.get(f"{pais_prefijo}-COL-u_medida_id", "").lower(),

        "col-std_id_muestra"        : config.get("COL-std_id_muestra", ""),
    }

    MensajeInicial(file_name, funcion_print=eprint, config=config, funcion_log=logprint)
    eprint(f"[País Actual: {paisActual}]")

    ExcelEntrada = os.path.join(CM_wd,ExcelEntrada)
    
    if not os.path.exists(ExcelEntrada) or os.path.isdir(ExcelEntrada):
        eprint("Archivo Excel no encontrado, seleccionar...")
        ExcelEntrada = filedialog.askopenfilename(
            title="Selecciona el archivo excel 'Base de datos'",
            initialdir=ExcelEntrada if os.path.isdir(ExcelEntrada) else CM_wd,
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if not ExcelEntrada:  # si el usuario cierra sin seleccionar
            input("No se seleccionó ningún archivo. Enter para salir...")
            exit(1)

        eprint(f"[Leyendo archivo {os.path.basename(ExcelEntrada)}]")

    #Comprobar excel de salida, volver a abrir al terminar
    if ExcelObjetivo:
        if not os.path.exists(ExcelObjetivo):
            eprint(f"Excel para guardar muestras no encontrado!\n\tDirectorio: {ExcelObjetivo}")
            ExcelObjetivo = ""
        else:
            eprint(f"[Guardando muestras en {os.path.basename(ExcelObjetivo)}]")
        
            listaExcel = ListaMuestraXLSX(dirExcel=ExcelObjetivo, colnames=[col_fmt["col-std_id_muestra"]], colname=col_fmt["col-std_id_muestra"], except_kill=False, except_create=True)
            
            if listaExcel:
                eprint(f"[Excel con {len(listaExcel)} muestras guardadas, concatenando muestras a lista (ultimo elemento {listaExcel[-1]})]")    

    if not token:
        input("No se encontro token de API. Enter para cerrar...")
        exit(1)

    eprint(f"[Leyendo Excel Hoja \'{HojaIM}\' y \'{HojaA}\']")

    try:
        #Leer dataframes con columnas en minusculas y filas con PK no vacía
        informacion_muestras_df = pd.read_excel(ExcelEntrada, sheet_name=HojaIM)
        analisis_df = pd.read_excel(ExcelEntrada, sheet_name=HojaA)
        
        org_col_inf = informacion_muestras_df.columns
        an_col_inf  = analisis_df.columns

    except ValueError as e:
        input(e)
        exit(1)

    eprint("[Formateando Datos de Analisis]")
    
    informacion_muestras_df.columns = informacion_muestras_df.columns.str.lower().str.strip()
    analisis_df.columns = analisis_df.columns.str.lower().str.strip()
    
    cols_muestras = set(col_fmt[_] for _ in ["col-indice_m" ,"col-id_muestras" ,"col-identificacion" ,"col-matriz" ,"col-empresa" ,"col-cuenta_relacionada" ,"col-motivo" ,"col-cliente_solicitante" ,"col-lugar_muestreo" ,"col-punto_muestreo" ,"col-direccion_muestreo" ,"col-estado" ,"col-municipio" ,"col-siralab" ,"col-instrumento_ambiental" ,"col-tipo_muestreo" ,"col-consultora" ,"col-coordenadas" ,"col-resp_muestreo" ,"col-frecuencia" ,"col-proyecto" ,"col-region" ,"col-departamento" ,"col-comuna" ,"col-etfa" ,"col-tabla_comp"] if col_fmt[_] != "")
    cols_analisis = set(col_fmt[_] for _ in ["col-indice_a","col-metodo_id","col-grupo_id","col-analisis_id","col-u_medida_id"] if col_fmt[_] != "")
    
    cols_df_muestras = set(informacion_muestras_df.columns.str.lower())
    cols_df_analisis = set(analisis_df.columns.str.lower())

    faltantes_muestras = cols_muestras - cols_df_muestras
    faltantes_analisis = cols_analisis - cols_df_analisis

    if faltantes_muestras:
        eprint(f"ALERTA No se encuentran columnas en Hoja {HojaIM} de excel, se esperaba:\n{faltantes_muestras}")

    if faltantes_analisis:
        eprint(f"ALERTA No se encuentran columnas en Hoja {HojaA} de excel, se esperaba:\n{faltantes_analisis}")
        
    if faltantes_analisis or faltantes_muestras:
        input("Puede que se encuentren errores. Enter para continuar...")

    try:
        if col_fmt["col-id_muestras"] not in informacion_muestras_df.columns:
            raise ValueError(f"columna id_muestras ('{col_fmt["col-id_muestras"]}') no encontrada en {list(informacion_muestras_df.columns)}")

        informacion_muestras_df = informacion_muestras_df.dropna(subset=[col_fmt["col-indice_m"]])
        analisis_df = analisis_df.dropna(subset=[col_fmt["col-indice_a"]])
        
        informacion_muestras_df.columns

        analisis_group = {}
        for group_value, group_df in analisis_df.groupby(col_fmt["col-indice_a"], sort=False):
            #NO REPETIR VALORES INFO ID
            info_id_buffer = []
            analisis_group[group_value] = []
            for _,fila in group_df.iterrows():
                f_infoid = fila[col_fmt["col-analisis_id"]]

                if f_infoid in info_id_buffer:
                    logprint(f"INFORMACION DUPLICADA {f_infoid} para muestra id {group_value}")
                    continue
                
                if pd.isna(f_infoid):
                    logprint(f"INFORMACION VACIA para muestra id {group_value}")
                    continue

                info_id_buffer.append(f_infoid)
                analisis_group[group_value].append(
                    SampleAnalysisInsert(
                        InfoId=             f_infoid,
                        MethodId=           fila[col_fmt["col-metodo_id"]],
                        AnalysisGroupId=    fila[col_fmt["col-grupo_id"]],
                        MeasurementUnitId=  fila[col_fmt["col-u_medida_id"]],
                    )
                )

        informacion_muestras_df["col-infos"] = informacion_muestras_df[col_fmt["col-indice_m"]].map(analisis_group)
    except KeyError as e:
        valor = e.args[0]
        llave = obtener_llave_por_valor(col_fmt, valor)
        if llave:
            input(f"Error columna de config '{llave}' ('{valor}') no encontrada, enter para cerrar...")
        else:
            input(f"Error columna {valor} no encontrada, enter para cerrar...")
        exit(1)
    except ValueError as e:
        input(e)
        exit(1)

    total_muestras = len(informacion_muestras_df)
    total_part = int((total_muestras)/Partition)+1

    lista_partitions = [informacion_muestras_df[i:i+Partition] for i in range(0, total_muestras, Partition)]
    len_lista_partitions = len(lista_partitions)
    
    if ListaPrecio != 0 and not str(ListaPrecio).isdigit():
        ListaPrecio = get_pricetable(ListaPrecio, APIdomain=APIdomain, token=token, funcion_print=eprint).Id
        
        if ListaPrecio == None:
            eprint("Lista de precios establecida al país")
            ListaPrecio = 0

    eprint(f"[Construyendo y subiendo cada {Partition} muestras en {total_part} partes ({total_muestras} muestras)]")
    timer = DeltaTimer(buffer_size=25)
    timer.start(len_lista_partitions)

    lista_errores = []
    ruta = os.path.join(CM_wd, f"salida_{fecha}.xlsx")

    df_salida = informacion_muestras_df.copy()
    del df_salida["col-infos"]

    with open(os.path.join(CM_wd, f"errores_{fecha}.txt"), "w", encoding="utf-8") as errores_salida:

        for idx, inf_muestra_df in enumerate(lista_partitions):
            timer.save(idx)
            eprint(f"\n[{idx*(Partition)}/{total_muestras}] [{idx+1}/{total_part}] [termino {timer.h_estimada} en {timer.t_restante}]")

            try:
                sample_records = FormatoDF(inf_muestra_df, col_fmt, paisActual, getdomain=APIdomain, gettoken=token, ListaPrecio=ListaPrecio, funcion_log=logprint, funcion_print=eprint)
            except KeyError as e:
                valor = e.args[0]
                llave = obtener_llave_por_valor(col_fmt, valor)
                if llave:
                    input(f"{e}\nError columna de config '{llave}' ('{valor}') no encontrada, enter para cerrar...")
                else:
                    input(f"{e}\nError columna {valor} no encontrada, enter para cerrar...")
                
                if total_part > 3:
                    continue
                else:
                    exit(1)
            
            total_solicitudes = len(sample_records)
            eprint(f"[Subiendo {total_solicitudes} Solicitudes]")
            
            temp_dict = {}
            for idx2, (id_muestra, record) in enumerate(sample_records, start=1):
                eprint(f"{idx2}/{total_solicitudes} [idx {id_muestra}]")
                
                if MostrarJSON:
                    eprint(json.dumps(json.loads(record), indent=4, ensure_ascii=False))
                else:
                    logprint(json.dumps(json.loads(record), indent=4, ensure_ascii=False))
                    
                #Subida API
                if "ERROR" in record:
                    eprint("Saltando Error")
                    continue

                data_api = api_post("samples", body=record, token=token, APIdomain=APIdomain, funcion_print=None)
                status = int(data_api.status_code)
                
                log_status(status, funcion_print=logprint)

                if status < 200 or status >= 300:
                    eprint(f"Error muestra {idx2} - estado API: {status}")
                    errores_salida.write(f"Error {data_api.status_code} para muestra de indice {id_muestra}.\nCabecera:\n{data_api.headers}\nContenido:\n{data_api.text}\n")
                    n_muestra = "ERROR"
                else:
                    n_muestra = int(data_api.json())
                    eprint(f"[Muestra {n_muestra} creada ({status})]")

                temp_dict = temp_dict|{id_muestra:n_muestra}

            for key,value in temp_dict.items():

                if ExcelObjetivo:
                    FilaAgregarXLSX(ExcelObjetivo, value, colnames=[col_fmt["col-std_id_muestra"]], except_kill=False, except_create=True)
                df_salida.loc[df_salida[col_fmt["col-indice_m"]] == int(key), col_fmt["col-id_muestras"]] = value

            df_salida.columns = org_col_inf
            analisis_df.columns = an_col_inf
        
            with pd.ExcelWriter(ruta, engine="xlsxwriter") as writer:
                df_salida.to_excel(writer, sheet_name=HojaIM, index=False)
                analisis_df.to_excel(writer, sheet_name=HojaA, index=False)
                    
            df_salida.columns = df_salida.columns.str.lower().str.strip()
            analisis_df.columns = analisis_df.columns.str.lower().str.strip()
        
    timer.finish()
    eprint("[Archivo excel creado]")

    input("Enter para cerrar...")

except Exception as e:

    notify(title="Problemas en programa", body=type(e).__name__)
    eprint(f"Problemas en programa: {FormatoExcepcion(e)}\n")
    eprint("Log exportado")
    sleep(3)
    exit(1)