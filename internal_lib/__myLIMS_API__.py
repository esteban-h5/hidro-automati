import requests, json, sys, os, pandas as pd, traceback, re
from keyring import get_password as get
from typing import Type, TypeVar
from __myLIMS_class__ import (
    T, PageResult, List, SampleAnalysisInsert,
    SampleBasic, PriceListBasic, SampleInfoInsert,
    MethodPrerequisiteAnalysisBasic,
    AnalysisGroupAnalysisBasic,
    SampleReasonBasic, AccountDetail,
    SampleTypeBasic, SpecificationBasic,
    MethodAnalysisBasic, SampleInsert,
    SampleSpecificationInsert,
    ValidationError,
)

from requests.exceptions import HTTPError
from openpyxl import load_workbook
from zipfile import BadZipFile
from urllib.parse import quote
from win11toast import notify
from datetime import datetime
from time import sleep
from time import time

def api_get(endpoint, APIdomain, token, model: Type[T], espera=30) -> T:
    response = requests.get(APIdomain+endpoint, 
                headers = {
                    "Content-Type": "application/json",
                    "x-access-key": token
                },
                timeout=(5, espera)
    )
    
    response.raise_for_status()
    data = response.json()
    
    return model.model_validate(data)

def api_post(endpoint, body, APIdomain, token, funcion_print=print):
    out = requests.post(
        APIdomain + endpoint,
        headers={
            "Content-Type": "application/json",
            "x-access-key": token
        },
        #params = {
            #"inlinecount":"allpages",
            #"top":"100"
        #}
        data=body
    )
    if funcion_print != None:
        funcion_print(body)
        
    return out

def get_samples_ID(filter, APIdomain, funcion_print=print, funcion_logprint=print):
    samples_list = []
    token = get('mylims_app', 'secret7')
    url_text = f"Samples?$filter={filter}&$inlinecount=allpages&$top=100"
    retries = 5
    while True:
        try:
            respuesta = api_get(url_text, APIdomain, token, PageResult[SampleBasic])
        except HTTPError as e:
            if retries != 0:
                retries -= 1
                respuesta
                funcion_print(f"ERROR DE API {e} AL OBTENER MUESTRAS\nReintentando [{retries}]")
                funcion_logprint("Body:", e.response.text)
                
                continue

            else:
                funcion_print(f"Continuando con lista actual")
                return samples_list

        break

    samples_list = samples_list + [str(sample.Id) for sample in respuesta.Result]

    total_page = int(respuesta.TotalCount/100)
    funcion_print(f"Consultando {respuesta.TotalCount} muestras en {total_page} páginas")
    
    page = 1
    retries = 5
    while respuesta.Count >= 100:
        funcion_print(f"{page}/{total_page}")
        try:
            respuesta = api_get(url_text+f"&$skip={100*page}", APIdomain, token, PageResult[SampleBasic])
        except HTTPError as e:
            if retries != 0:
                retries -= 1
                funcion_print(f"ERROR DE API {e} AL OBTENER MUESTRAS\nReintentando [{retries}]")
                respuesta.Count = 100
                continue

            else:
                break
        samples_list = samples_list + [str(sample.Id) for sample in respuesta.Result]
        page+=1

    return samples_list

def get_grupoanalisis(id: int, APIdomain, token, funcion_print=print) ->  List[AnalysisGroupAnalysisBasic]:
    
    empty_obj = AnalysisGroupAnalysisBasic(**{f: None for f in AnalysisGroupAnalysisBasic.model_fields})

    try:
        # respuesta = api_get(f"AnalysisGroups/{id}/Analyses?$filter=Active eq true", APIdomain, token, PageResult[AnalysisGroupAnalysisBasic])
        respuesta = api_get(f"AnalysisGroups/{id}/Analyses", APIdomain, token, PageResult[AnalysisGroupAnalysisBasic])
    except HTTPError as e:
        funcion_print(f"ERROR DE API {e} PARA GRUPO DE ANALISIS {id}")
        return empty_obj

    if respuesta.Count < 1:
        funcion_print(f"NO SE ENCONTRARON RESULTADOS PARA GRUPO DE ANALISIS {id}")
        return empty_obj

    return respuesta.Result


def get_pricetable(identification: str, APIdomain, token, funcion_print=print) -> PageResult[PriceListBasic]:
    
    empty_obj = PriceListBasic(**{f: None for f in PriceListBasic.model_fields})

    try:
        respuesta = api_get(f"pricelists?$filter=Identification eq '{quote(identification)}' and Active eq true", APIdomain, token, PageResult[PriceListBasic])
    except HTTPError as e:
        funcion_print(f"ERROR DE API {e} PARA TABLA DE PRECIOS {identification}")
        return empty_obj

    if respuesta.Count < 1:
        funcion_print(f"NO SE ENCONTRARON RESULTADOS PARA TABLA DE PRECIOS {identification}")
        return empty_obj

    if respuesta.Count > 1:
        funcion_print(f"SE ENCONTRO MAS DE 1 RESULTADO\nSe encontro tambien: {' - '.join(_.Identification for _ in respuesta.Result[1:])}")

    return respuesta.Result[0]

def get_samplereason(identification: str, APIdomain, token, funcion_print=print) -> PageResult[SampleReasonBasic]:
    
    empty_obj = SampleReasonBasic(**{f: None for f in SampleReasonBasic.model_fields})

    try:
        respuesta = api_get(f"samplereasons?$filter=Identification eq '{quote(identification)}' and Active eq true", APIdomain, token, PageResult[SampleReasonBasic])
    except HTTPError as e:
        funcion_print(f"ERROR DE API {e} PARA MOTIVO {identification}")
        return empty_obj

    if respuesta.Count < 1:
        funcion_print(f"NO SE ENCONTRARON RESULTADOS PARA MOTIVO {identification}")
        return empty_obj

    if respuesta.Count > 1:
        funcion_print(f"SE ENCONTRO MAS DE 1 RESULTADO\nSe encontro tambien: {' - '.join(_.Identification for _ in respuesta.Result[1:])}")

    return respuesta.Result[0]

def get_account(identification: str, APIdomain, token, funcion_print=print) -> PageResult[AccountDetail]:
    empty_obj = AccountDetail(**{f: None for f in AccountDetail.model_fields})
    
    try:
        respuesta = api_get(f"Accounts?$filter=Identification eq '{quote(identification)}'", APIdomain, token, PageResult[AccountDetail])
    except HTTPError as e:
        funcion_print(f"ERROR DE API {e} PARA CUENTA {identification}")
        return empty_obj

    if respuesta.Count < 1:
        funcion_print(f"NO SE ENCONTRARON RESULTADOS PARA CUENTA {identification}")
        return empty_obj

    if respuesta.Count > 1:
        funcion_print(f"SE ENCONTRO MAS DE 1 RESULTADO\nSe encontro tambien: {' - '.join(_.Identification for _ in respuesta.Result[1:])}")

    return respuesta.Result[0]

def get_sampletype(identification: str, APIdomain, token, funcion_print=print) -> PageResult[SampleTypeBasic]:

    empty_obj = SampleTypeBasic(**{f: None for f in SampleTypeBasic.model_fields})
    
    try:
        respuesta = api_get(f"SampleTypes?$filter=Identification eq '{quote(identification)}'", APIdomain, token, PageResult[SampleTypeBasic])
    except HTTPError as e:
        funcion_print(f"ERROR DE API {e} PARA TIPO DE MUESTRA {identification}")
        return empty_obj

    if respuesta.Count < 1:
        funcion_print(f"NO SE ENCONTRARON RESULTADOS PARA TIPO DE MUESTRA {identification}")
        return empty_obj

    if respuesta.Count > 1:
        funcion_print(f"SE ENCONTRO MAS DE 1 RESULTADO\nSe encontro tambien: {' - '.join(_.Identification for _ in respuesta.Result[1:])}")

    return respuesta.Result[0]

def get_specification(identification: str, APIdomain, token, funcion_print=print) -> PageResult[SpecificationBasic]:

    empty_obj = SpecificationBasic(**{f: None for f in SpecificationBasic.model_fields})
    
    try:
        respuesta = api_get(f"Specifications?$filter=Identification eq '{quote(identification)}' and Active eq true", APIdomain, token, PageResult[SampleTypeBasic])
    except HTTPError as e:
        funcion_print(f"ERROR DE API {e} PARA LA ESPECIFICACION {identification}")
        return empty_obj

    if respuesta.Count < 1:
        funcion_print(f"NO SE ENCONTRARON RESULTADOS PARA LA ESPECIFICACION {identification}")
        return empty_obj

    if respuesta.Count > 1:
        funcion_print(f"SE ENCONTRO MAS DE 1 RESULTADO\nSe encontro tambien: {' - '.join(_.Identification for _ in respuesta.Result[1:])}")

    return respuesta.Result[0]


def get_methodprerequisite(id: str, APIdomain, token, funcion_print=print) -> List[T]:
    
    empty_obj = MethodPrerequisiteAnalysisBasic(**{f: None for f in MethodPrerequisiteAnalysisBasic.model_fields})

    try:
        respuesta = api_get(f"Methods/{id}/MethodPrerequisiteAnalysisBasic?$filter=Active eq true", APIdomain, token, PageResult[MethodPrerequisiteAnalysisBasic])
    except HTTPError as e:
        funcion_print(f"ERROR DE API {e} PARA METODO {id}")
        return empty_obj

    if respuesta.Count < 1:
        funcion_print(f"NO SE ENCONTRARON RESULTADOS PARA METODO DE ID {id}")
        return [empty_obj]

    return respuesta.Result

def get_methods(page: int, APIdomain, token, funcion_print=print) -> List[T]:
    
    empty_obj = MethodAnalysisBasic(**{f: None for f in MethodAnalysisBasic.model_fields})

    try:
        respuesta = api_get(
            f"Methods/Analyses?$skip={(page-1)*50}&$inlinecount=allpages&$filter=Method/Active eq true and (Method/MethodType/Identification eq 'General' or Method/MethodType/Identification eq 'General - QC')",
            APIdomain, token, PageResult[MethodAnalysisBasic]
        )
    except HTTPError as e:
        funcion_print(f"ERROR DE API {e} PARA BUSCAR METODOS")
        return [empty_obj]

    if respuesta.Count < 1:
        funcion_print(f"NO SE ENCONTRARON RESULTADOS EN LOS METODOS")
        return [empty_obj]

    return respuesta

def FormatoDF(muestras, col_fmt, paisActual, getdomain, gettoken, ListaPrecio, funcion_print=print, funcion_log=print):
    sample_records = []

    ############################
    # Definir variables de paises
    ############################

    if paisActual == "colombia":
        centro_servicio = 24
        
        # HB BOG 2026
        lista_precio = 138 if ListaPrecio == 0 else ListaPrecio
        
        info_lista= lambda df: [

            SampleInfoInsert(DisplayValue=df[col_fmt["col-cliente_solicitante"]],
                InfoId=13139,Attribute=None,InfoGroupId=102),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-lugar_muestreo"]],
                InfoId=11268,Attribute=None,InfoGroupId=2),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-punto_muestreo"]],
                InfoId=11269,Attribute=None,InfoGroupId=2),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-direccion_muestreo"]],
                InfoId=11270,Attribute=None,InfoGroupId=2),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-departamento"]],
                InfoId=11262,Attribute=None,InfoGroupId=2),
                
            SampleInfoInsert(DisplayValue=df[col_fmt["col-tipo_muestreo"]],
                InfoId=13145,Attribute=None,InfoGroupId=2),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-consultora"]],
                InfoId=13609,Attribute=2,InfoGroupId=102),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-coordenadas"]],
                InfoId=11044,Attribute=0,InfoGroupId=2),
                
            # SampleInfoInsert(DisplayValue=df[col_fmt["col-resp_muestreo"]],
            #     InfoId=474,Attribute=0,InfoGroupId=102),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-frecuencia"]],
                InfoId=10924,Attribute=None,InfoGroupId=102),

        ]

    elif paisActual == "mexico":
        centro_servicio = 25
        
        #HB MTY 2026
        lista_precio = 135 if ListaPrecio == 0 else ListaPrecio

        info_lista= lambda df: [

            SampleInfoInsert(DisplayValue=df[col_fmt["col-cliente_solicitante"]],
                InfoId=14596,Attribute=0,InfoGroupId=102),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-lugar_muestreo"]],
                InfoId=11268,Attribute=None,InfoGroupId=2),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-punto_muestreo"]],
                InfoId=11269,Attribute=None,InfoGroupId=2),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-direccion_muestreo"]],
                InfoId=11270,Attribute=None,InfoGroupId=2),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-estado"]],
                InfoId=14569,Attribute=None,InfoGroupId=2),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-municipio"]],
                InfoId=14570,Attribute=None,InfoGroupId=2),
                
            SampleInfoInsert(DisplayValue=df[col_fmt["col-siralab"]],
                InfoId=14566,Attribute=None,InfoGroupId=102),

            # SampleInfoInsert(DisplayValue=df[col_fmt["col-instrumento_ambiental"]],
                # InfoId=13097,Attribute=None,InfoGroupId=2),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-tipo_muestreo"]],
                InfoId=13145,Attribute=None,InfoGroupId=2),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-consultora"]],
                InfoId=13609,Attribute=2,InfoGroupId=102),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-coordenadas"]],
                InfoId=11044,Attribute=0,InfoGroupId=2),
                
            SampleInfoInsert(DisplayValue=df[col_fmt["col-resp_muestreo"]],
                InfoId=474,Attribute=0,InfoGroupId=102),
        ]
    elif paisActual == "chile": # Asumir Chile
        centro_servicio = 20
        lista_precio = 122 if ListaPrecio == 0 else ListaPrecio
        info_lista= lambda df: [
            
            SampleInfoInsert(DisplayValue=df[col_fmt["col-cliente_solicitante"]],
                InfoId=13139,Attribute=None,InfoGroupId=102),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-lugar_muestreo"]],
                InfoId=11268,Attribute=None,InfoGroupId=2),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-punto_muestreo"]],
                InfoId=11269,Attribute=None,InfoGroupId=2),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-direccion_muestreo"]],
                InfoId=11270,Attribute=None,InfoGroupId=2),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-proyecto"]],
                InfoId=13098,Attribute=None,InfoGroupId=2),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-region"]],
                InfoId=11262,Attribute=None,InfoGroupId=2),
                
            SampleInfoInsert(DisplayValue=df[col_fmt["col-comuna"]],
                InfoId=11209,Attribute=None,InfoGroupId=2),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-etfa"]],
                InfoId=11263,Attribute=2,InfoGroupId=102),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-instrumento_ambiental"]],
                InfoId=13097,Attribute=None,InfoGroupId=2),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-tipo_muestreo"]],
                InfoId=13145,Attribute=None,InfoGroupId=2),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-consultora"]],
                InfoId=13609,Attribute=2,InfoGroupId=102),

            SampleInfoInsert(DisplayValue=df[col_fmt["col-coordenadas"]],
                InfoId=11044,Attribute=0,InfoGroupId=2),
                
            SampleInfoInsert(DisplayValue=df[col_fmt["col-resp_muestreo"]],
                InfoId=474,Attribute=None,InfoGroupId=102),
        ]

    else:
        raise Exception(f"País {paisActual} no se reconoce")

    #########################################
    # Recorrer filas para construir solicitud
    #########################################

    total_muestras = len(muestras)

    def get_id(muestra, val, def_get):
        comp = str(muestra[col_fmt[val]])
        if comp in ("nan","N/A","N-A"): return  None
        else:
            if comp.isdigit(): 
                return int(comp)
            else:
                get_info = def_get(comp, APIdomain=getdomain, token=gettoken, funcion_print=funcion_print)
                return get_info.Id
    
    for idx, (_, muestra) in enumerate(muestras.iterrows(), start=1):
        
        try:
            id_muestra = muestra[col_fmt["col-indice_m"]]
            
            samplereason_id     = get_id(muestra, "col-motivo", get_samplereason)
            account_id          = get_id(muestra, "col-empresa", get_account)
            related_account_id  = get_id(muestra, "col-cuenta_relacionada", get_account)
            sample_t_id         = get_id(muestra, "col-matriz", get_sampletype)
            spec_id             = get_id(muestra, "col-tabla_comp", get_specification)
            
            if spec_id:
                specification_record  = [SampleSpecificationInsert(SpecificationId=spec_id)]
            else:
                specification_record = []
                  
            solicitud = SampleInsert(
                Identification=         muestra[col_fmt["col-identificacion"]],
                ControlIdentification=  None,
                TakenDateTime=          None,
                SampleTypeId=           sample_t_id,
                ServiceCenterId=        centro_servicio,
                CollectionPointId=      None,
                PriceListId=            lista_precio,
                ConclusionTime=         None,
                ConclusionTimeFixed=    False,
                AccountId=              account_id,
                RelatedAccountId=       related_account_id,
                SampleReasonId=         samplereason_id,
                ReferenceKey=           None,
                SyncPortal=             True,
                Latitude=               None,
                Altitude=               None,
                Longitude=              None,
                groupId=                None,
                UpdateTermAndPrice=     True,
                Infos=                  info_lista(muestra),
                Analyses=               muestra["col-infos"],
                Specifications=         specification_record
            )

            sample_records.append([id_muestra , solicitud.model_dump_json()])

        except ValidationError as e:
            funcion_print(f"Error para muestra {idx} de {total_muestras} [id en excel: {id_muestra}] {e.errors()}")
            funcion_log(f"-----------\n{e.json()}\n-----------\n")
            sample_records.append([id_muestra, {'ERROR'}])

    return sample_records


def log_status(status_code, funcion_print):
    match status_code:

        case 200:
            funcion_print("200 OK - No error, successful operation")
        case 201:
            funcion_print("201 Created - Successfully creating a resource")
        case 202:
            funcion_print("202 Accepted - The request was received")
        case 204:
            funcion_print("204 No Content - Request processed successfully, no response body required")
        case 301:
            funcion_print("301 Moved Permanently - Feature has moved")
        case 304:
            funcion_print("304 Not Modified - Resource has not been modified")
        case 400:
            funcion_print("400 Bad Request - Malformed syntax or a bad query")
        case 401:
            funcion_print("401 Unauthorized - Action requires user authentication")
        case 403:
            funcion_print("403 Forbidden - Authentication failed or invalid application ID")
        case 404:
            funcion_print("404 Not Found - Resource not found")
        case 405:
            funcion_print("405 Not Allowed - Method not allowed on this resource")
        case 406:
            funcion_print("406 Not Acceptable - Requested representation is not available for the resource")
        case 408:
            funcion_print("408 Request Timeout - The request expired")
        case 410:
            funcion_print("410 Gone - The URI used refers to a resource no longer available")
        case 415:
            funcion_print("415 Unsupported Media Type - Representation is not supported for the resource")
        case 500:
            funcion_print("500 Internal Server Error - Server encountered an unexpected condition")
        case 501:
            funcion_print("501 Not Implemented - The requested HTTP operation is not supported")
        case _:
            funcion_print(f"{status_code} - Código de estado no esperado")
