#!/usr/bin/env python3
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

DW_DIR= "/path/to/download/directory"
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_experimental_option('prefs', {
"download.default_directory": f"{DW_DIR}", #Change default directory for downloads
"download.prompt_for_download": False, #To auto download the file
"download.directory_upgrade": True,
"plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome 
})
driver = webdriver.Chrome(options=options)

# declarar variables a utilizar
all_descargar_buttons_list = []
etiquetas_a_descargar = []
page_number = 1

# declarar funciones
def comenzar():
    driver.implicitly_wait(30)
    driver.get("https://www.correoargentino.com.ar/MiCorreo/public/login")
    username_field = driver.find_element(By.ID, "email" )
    username_field.send_keys("ejemplo@mail.com")
    password_field = driver.find_element(By.ID, "password" )
    password_field.send_keys("contraseña1234")
    login_button = driver.find_element(By.XPATH, "/html/body/div[4]/div/div/div/div[2]/form/div[3]/div[2]/button" )
    login_button.click()
    #ir a gestion de envios
    driver.get("https://www.correoargentino.com.ar/MiCorreo/public/listadooperaciones")
    print("Entrando al sitio... ")
    time.sleep(5)


def next():
    go_to_next_page = driver.find_element(By.CLASS_NAME, "fa-forward")
    go_to_next_page.click() #ir a la siguiente "pagina" (es la misma url)


# WAIT WORKAROUND: llamar al ticket 100 para asegurarse de que esta cargado hasta ahi
def get_ticket_100():
    ticket_100 = driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[4]/div[1]/div[1]/div[2]/div/table/tbody/tr[100]/td[8]/div").text
    print(f"# # # # #\nDatos del ticket nº 100 de la página {page_number}:\n{ticket_100}\n# # # # #")
    page_number.__add__(1)  # por si cambia de pagina, ya tiene el numero preparado


#lista de los botones Descargar (100 por pagina)
def make_descargar_buttons_list():
    # contenedor
    tbody = driver.find_element(By.TAG_NAME,"tbody")
    #lista de todos los botones (400)
    all_buttons_list = tbody.find_elements(By.TAG_NAME, "button")
    for cada_boton in all_buttons_list:
        if (cada_boton.get_attribute("title") == 'Descargar'):
            all_descargar_buttons_list.append(cada_boton)

# lista de los tickets que necesitamos descargar
def make_etiquetas_a_descargar_list():
    for cada_boton in all_descargar_buttons_list:
            if (cada_boton.get_attribute("onclick") != "mensajeEstado()"):
                etiquetas_a_descargar.append(cada_boton)
    x = len(etiquetas_a_descargar)
    print(f"Total de tickets para imprimir en esta página: {x}")
    return etiquetas_a_descargar

def descargar():
    total_descargado = 0
    for cada_boton in etiquetas_a_descargar:
        #get name
        nearer_ancestor = cada_boton.find_element(By.XPATH, "*//ancestor::tr/td[8]/div").text.strip()
        div_content_list = nearer_ancestor.split()
        nombre = (div_content_list[-2] + "_" + div_content_list[-1] + ".pdf")
        #click en descargar
        cada_boton.click()
        #rename
        original_file_name = os.popen(f"ls -rt {DW_DIR} | tail -n 1").read().strip()
        os.rename(f"{DW_DIR}/{original_file_name}",f"{DW_DIR}/{nombre}")
        #count
        total_descargado += 1
    os.system("osascript -e beep; osascript -e beep; osascript -e beep")
    print(f"Se descargaron {total_descargado} etiquetas de esta página.")
    
def salir():
    print("Programa finalizado.")
    driver.get("https://www.correoargentino.com.ar/MiCorreo/public/logout")
    driver.quit()

def func1():
    get_ticket_100() # Una vez que devuelve el ultimo ticket (ticket_100), es seguro avanzar
    time.sleep(10)
    print("Espera mientras se carga la pagina...")
    make_descargar_buttons_list()
    #En este punto tengo la lista con TODOS los botones Descargar
    #print(len(all_descargar_buttons_list)) #CUENTA 100, perfecto!
    make_etiquetas_a_descargar_list()
    #Confirmar
    confirmar_hay_mas = etiquetas_a_descargar == 100
    os.system("osascript -e beep")
    msg = input(f"Ingresar \"ok + Enter\" para descargar etiquetas. Para cancelar presiona solamente \"Enter\": ")
    if msg == "ok":
        print("Descargando...")
        descargar()
        if confirmar_hay_mas == True:
            print("Parece que hay más etiquetas en la siguiente página. Buscando para descargar...")
            all_descargar_buttons_list.clear() # limpiar lista
            etiquetas_a_descargar.clear() # limpiar lista
            next()
            func1()
        else:
            print("No quedan más etiquetas por descargar.")
            salir()
    else:
        print("Descarga cancelada.")
        salir()


comenzar()
func1()
exit()
