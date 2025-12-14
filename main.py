from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import tkinter as tk
import keyring
import json
import threading


def limpiar_ventana():
    """Elimina todos los widgets actuales"""
    for widget in frame.winfo_children():
        widget.destroy()

def mostrar_mensaje(texto,con_tiempo,next_func=None):
    """Muestra un mensaje en la ventana"""
    limpiar_ventana()
    label = tk.Label(
        frame,
        text=texto,
        font=("Arial", 16),
        fg="white",
        bg="#2E2E2E"
        )
    label.grid(row=2, column=0, pady=(100, 20),columnspan=40)

    if con_tiempo:
        label.after(2000, lambda: (label.destroy(), next_func()))

def pedir_datos_usuario():
    """Pantalla para introducir datos de usuario"""
    limpiar_ventana()

    tk.Label(
        frame,
        text="Usuario",
        font=("Arial", 16),
        fg="white",
        bg="#2E2E2E"
    ).grid(row=0, column=0, pady=20)

    entrada_usuario = tk.Entry(
        frame,
        show="*",
        font=("Arial", 16)
    )
    entrada_usuario.grid(row=1, column=0)

    tk.Label(
        frame,
        text="Contraseña",
        font=("Arial", 16),
        fg="white",
        bg="#2E2E2E"
    ).grid(row=2, column=0, pady=20)

    entrada_contrasena = tk.Entry(
        frame,
        show="*",
        font=("Arial", 16)
    )
    entrada_contrasena.grid(row=3, column=0)

    tk.Button(
        frame,
        text="Verificar",
        command=lambda:verificar_datos(entrada_usuario.get(),entrada_contrasena.get()),
        font=("Arial", 16),
        bg="#2196F3",
        fg="white",
        activebackground="#1976D2",
        activeforeground="white"
    ).grid(row=4, column=0, pady=60)

def verificar_datos(usuario,contrasena):
    """actualiza la app"""
    limpiar_ventana()
    mostrar_mensaje("Procesando...esto puede llevar un rato",False)

    threading.Thread(
        target=verificar_datos_selenium,
        args=(usuario, contrasena),
        daemon=True
    ).start()

def verificar_datos_selenium(usuario, contrasena):
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    driver.set_window_position(-1000, 0)
    driver.set_window_size(800, 600)

    options = Options()
    options.add_argument("--headless=new")  # Chrome oculto
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://aules.edu.gva.es/fp/login/index.php?loginredirect=1")

    driver.find_element(By.ID, "username").send_keys(usuario)
    driver.find_element(By.ID, "password").send_keys(contrasena + Keys.ENTER)

    wait = WebDriverWait(driver, 5)

    try:
        wait.until(EC.presence_of_element_located((By.ID, "username")))
        wait.until(EC.presence_of_element_located((By.ID, "password")))

        ventana.after(
            0,
            lambda: mostrar_mensaje("Cuenta inválida", True, pedir_datos_usuario)
        )

    except TimeoutException:
        guardar_datos(usuario, contrasena)

        ventana.after(
            0,
            lambda: mostrar_mensaje("Cuenta verificada", True, menu_principal)
        )

    finally:
        driver.quit()

def guardar_datos(usuario,contrasena):
    confirmar_registro()
    password = []
    password.append(usuario)
    password.append(contrasena)
    password_str = json.dumps(password)

    keyring.set_password(SERVICE, ACCOUNT, password_str)

def comprobar_registro():
    with open("usuario_registrado.txt", "r") as archivo:
        linea = archivo.readline()

    if linea =="true":
        return True
    else:
        return False

def confirmar_registro():
    with open("usuario_registrado.txt", "w") as archivo:
        archivo.write("true")

def menu_principal():
    limpiar_ventana()

    tk.Button(
        frame,
        text="Organizar",
        font=("Arial", 16),
        bg="#2196F3",
        fg="white",
        activebackground="#1976D2",
        activeforeground="white",
        command=lambda:crear_carpeta()
    ).grid(row=0, column=0, padx=10, pady=40)

    tk.Button(
        frame,
        text="Desahacer",
        font=("Arial", 16),
        bg="#FFC107",
        fg="white",
        activebackground="#FFA000",
        activeforeground="white"
    ).grid(row=1, column=0, padx=10, pady=40)

    tk.Button(
        frame,
        text="Eliminar",
        font=("Arial", 16),
        bg="#F44336",
        fg="white",
        activebackground="#D32F2F",
        activeforeground="white"
    ).grid(row=2, column=0, padx=10, pady=40)

def crear_carpeta():
    """actualiza la app"""
    limpiar_ventana()
    mostrar_mensaje("Procesando...esto puede llevar un rato", False)

    threading.Thread(
        target=crear_carpeta_selenium,
        daemon=True
    ).start()

def crear_carpeta_selenium():

    """cargar los datos"""
    password_str = keyring.get_password(SERVICE, ACCOUNT)
    password = json.loads(password_str)

    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    driver.set_window_position(-1000, 0)
    driver.set_window_size(800, 600)

    options = Options()
    options.add_argument("--headless=new")  # Chrome oculto
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://aules.edu.gva.es/fp/login/index.php?loginredirect=1")

    driver.find_element(By.ID, "username").send_keys(password[0])
    driver.find_element(By.ID, "password").send_keys(password[1] + Keys.ENTER)

    wait = WebDriverWait(driver, 5)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.aalink.coursename")))

    courses = driver.find_elements(By.CSS_SELECTOR, "a.aalink.coursename")

    """Identifica todos los cursos"""
    course_list = []
    for c in courses:
        span_title = c.find_element(By.CSS_SELECTOR, "span.multiline")
        name = span_title.get_attribute("title")
        link = c.get_attribute("href")

        #print(name)
        course_list.append((name, link))

    archivos = []
    """Recorre cada curso"""
    for name, link in course_list:
        print("\nEntrando en:", name)
        driver.get(link)
        #para encontrar todas las secciones
        secciones = driver.find_elements(By.CSS_SELECTOR, "h3.sectionname")
        for seccion in secciones:
            texto = seccion.text
            print(texto)
        driver.get("https://aules.edu.gva.es/fp/my/")

SERVICE = "app"
ACCOUNT = "usuario"

ventana = tk.Tk()

ancho = 600
alto = 400

# Tamaño de la pantalla
ancho_pantalla = ventana.winfo_screenwidth()
alto_pantalla = ventana.winfo_screenheight()

# Cálculo para centrar
x = (ancho_pantalla // 2) - (ancho // 2)
y = (alto_pantalla // 2) - (alto // 2)

ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

ventana.title("Organizador_AULES")
ventana.resizable(False, False)
ventana.configure(bg="#2E2E2E")

frame = tk.Frame(ventana, bg="#2E2E2E")
frame.grid(row=0, column=0, sticky="nsew")

ventana.grid_rowconfigure(0, weight=1)
ventana.grid_columnconfigure(0, weight=1)

frame.grid_columnconfigure(0, weight=1)

if not comprobar_registro():
    pedir_datos_usuario()

else:
    menu_principal()

ventana.mainloop()
