#!/usr/bin/env python3
from distutils.command.build import build
from distutils.command.clean import clean
from genericpath import exists
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import glob
from PyPDF2 import PdfFileMerger

DW_DIR= "/Users/ramirogarcia/lecop/correo_imprimir"
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_experimental_option('prefs', {
"download.default_directory": f"{DW_DIR}", #Change default directory for downloads
"download.prompt_for_download": False, #To auto download the file
"download.directory_upgrade": True,
"plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome 
})

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

# variables a utilizar
all_descargar_buttons_list = []
etiquetas_a_descargar = []
page_number = 1
total_descargado = 0
file_list = []

# declarar funciones

def clean_directory():
    files = glob.glob(f"{DW_DIR}/*")
    for f in files:
        os.remove(f)
    print("Directorio destino ahora está vacío\n")


def comenzar():
    print("*** Programa iniciado ***")
    clean_directory()
    #driver.implicitly_wait(30)
    # driver.maximize_window()
    driver.get("https://www.correoargentino.com.ar/MiCorreo/public/login")
    username_field = driver.find_element(By.ID, "email" )
    username_field.send_keys("lecopcentral@gmail.com")
    password_field = driver.find_element(By.ID, "password" )
    password_field.send_keys("qmb2pfx_GQE9eub3xqv")
    login_button = driver.find_element(By.XPATH, "/html/body/div[4]/div/div/div/div[2]/form/div[3]/div[2]/button" )
    try:
        login_button.click()
        print("Entrando al sitio... ")
    except:
        print("Error al tratar de ingresar al sitio (seguramente haya una sesión abierta.")
        driver.quit()
    #ir a gestion de envios
    driver.get("https://www.correoargentino.com.ar/MiCorreo/public/listadooperaciones")


#esta hay que quitarla en cuanto deje de aparecer el modal
"""
def aceptar_modal():
    button_aceptar = wait.until(EC.invisibility_of_element(driver.find_element(By.ID, "modalLoading"))).find_element(By.XPATH, '//*[@id="mensajeModalFooterGen"]/button')
    try:
        button_aceptar.click()
        #wait.until(EC.element_to_be_clickable(driver.find_element(By.XPATH, '//*[@id="mensajeModalFooterGen"]/button'))).click()
        print("Pop-up (Modal) aceptado\n")
    except:
        print("PROBLEMAS CON EL MODAL DE MIERDA")
        salir()
"""
def next():
    go_to_next_page = driver.find_element(By.CLASS_NAME, "fa-forward")
    go_to_next_page.click() #ir a la siguiente "pagina" (es la misma url)
    print(f"Yendo a la página siguiente ({page_number}).Espera un momento...\n")
    wait.until(EC.invisibility_of_element(driver.find_element(By.ID, "modalLoading")))

"""
# ver el ultimo ticket para controlar en caso de ser necesario. 
# El maximo de tickets por pagina es 100
#TODO NO SIEMPRE HAY 100, claro
def get_last_ticket():
    global page_number
    #last_ticket = driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[4]/div[1]/div[1]/div[2]/div/table/tbody/tr[100]/td[8]/div").text
    #ticket_100 = wait.until(EC.element_to_be_clickable(driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[4]/div[1]/div[1]/div[2]/div/table/tbody/tr[100]/td[8]/div")
    #info = ticket_100.text
    #print(f"# # # # #\nDatos del útlimo ticket de la página {page_number}:\n{last_ticket}\n# # # # #")  
"""
#lista de los botones Descargar (seran 100, arranca en 0)
def make_descargar_buttons_list():
    # contenedor
    tbody = driver.find_element(By.TAG_NAME,"tbody")
    #lista de todos los botones (400, 4 por ticket)
    all_buttons_list = tbody.find_elements(By.TAG_NAME, "button")
    for cada_boton in all_buttons_list:
        if (cada_boton.get_attribute("title") == 'Descargar'):
            all_descargar_buttons_list.append(cada_boton)

# lista de lo que efectivamente necesito
def make_etiquetas_a_descargar_list():
    for cada_boton in all_descargar_buttons_list:
            #TODO: diferenciar Proceso de preimposicion(no se imprimieron/descargaron) y PREIMPOSICION (las que ya fueron impresas/descargadas)
            if (cada_boton.get_attribute("onclick") != "mensajeEstado()"):
                etiquetas_a_descargar.append(cada_boton)
    x = len(etiquetas_a_descargar)
    print(f"Total de tickets para imprimir en esta página: {x}")
    return etiquetas_a_descargar


def check_download(filename):
    file_exists = exists(filename)
    time.sleep(0.25)
    if file_exists == True:
        return None
    else: check_download(filename)


def descargar():
    print("\nDescargando...")
    global page_number
    global total_descargado
    descargado_por_pagina = 0
    default_name = f"{DW_DIR}/getrotulo.pdf"
    for cada_boton in etiquetas_a_descargar:
        #descargar etiqueta
        cada_boton.click()
        #count
        total_descargado += 1
        descargado_por_pagina += 1
        #get name
        nearer_ancestor = cada_boton.find_element(By.XPATH, "*//ancestor::tr/td[8]/div").text.strip()
        div_content_list = nearer_ancestor.split()
        nombre = f"{total_descargado}" + "_" + div_content_list[-2] + "_" + div_content_list[-1] + ".pdf"
        file_list.append(nombre)
        new_name = f"{DW_DIR}/{nombre}"
        #confirmar que esta en directorio destino
        check_download(default_name)
        #rename
        os.rename(default_name,new_name)
    os.system("osascript -e beep; osascript -e beep; osascript -e beep")
    print(f"Se descargaron {descargado_por_pagina} de esta página ({page_number}).")


def salir():
    print("Saliendo del driver...")
    driver.get("https://www.correoargentino.com.ar/MiCorreo/public/logout")
    time.sleep(2)
    driver.quit()


def func():
    global page_number
    print(f"Buscando tickets en página {page_number}...")
    #get_last_ticket() # Una vez que devuelve el ultimo ticket es seguro avanzar
    time.sleep(20)
    make_descargar_buttons_list() 
    make_etiquetas_a_descargar_list() 
    os.system("osascript -e beep; osascript -e beep; osascript -e beep")
    msg = input(f"\n(Para iniciar desarga ingresar \"ok + Enter\")\n(Para cancelar presiona solamente \"Enter\")\nINGRESAR COMANDO: ").upper()
    confirmar_hay_mas = len(etiquetas_a_descargar) >= 100 # en la lista es de 0 a 99
    if msg == "OK":
        descargar()
        if confirmar_hay_mas == True:
            print("\nParece que hay más etiquetas en la siguiente página")
            all_descargar_buttons_list.clear() # limpiar lista
            etiquetas_a_descargar.clear() # limpiar lista
            page_number += 1
            next()
            func()
        else:
            print(f"Se descargaron {total_descargado} etiquetas.")
            print("No quedan más etiquetas por descargar.")
            salir()
    else:
        print("Descarga cancelada.")
        salir()


def imprimir():
    pdfs = file_list
    #pdfs = filter(lambda f: f.endswith('.pdf'), pdfs)
    merger = PdfFileMerger()

    
    for pdf in pdfs:
        full_path = f"{DW_DIR}/{pdf}"
        merger.append(full_path)

    merger.write(f"{DW_DIR}/TICKETS_PARA_IMPRIMIR.pdf")
    merger.close()
    print("PDF merge realizado.")

#Workflow
comenzar()
#aceptar_modal()
func()
time.sleep(10)
imprimir()
exit()