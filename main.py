from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import json

# Configurar el driver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.maximize_window()

try:
    # Ir al sitio de Liverpool y buscar
    driver.get("https://www.liverpool.com.mx")
    time.sleep(5)

    search_box = driver.find_element(By.ID, "mainSearchbar")
    search_box.send_keys("Cargador Iphone")
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)

    # Abrir el primer producto
    product_link = driver.find_element(By.CSS_SELECTOR, "li[data-prodid] a")
    href = product_link.get_attribute("href")
    driver.get(href)
    time.sleep(5)

    # Función para abrir el modal de disponibilidad
    def abrir_modal_disponibilidad():
        disponibilidad_btn = driver.find_element(By.CSS_SELECTOR, "div.btnGeoStore")
        disponibilidad_btn.click()
        time.sleep(3)

    # Función para cerrar el modal de disponibilidad
    def cerrar_modal_disponibilidad():
        close_btn = driver.find_element(By.CSS_SELECTOR, "button.close")
        close_btn.click()
        time.sleep(3)

    # Abrir modal la primera vez para obtener los estados
    abrir_modal_disponibilidad()

    # Obtener la lista de estados (solo textos)
    states_div = driver.find_element(By.CSS_SELECTOR, ".m-product__itrSelectStates")
    states_names = [state.text.strip() for state in states_div.find_elements(By.CLASS_NAME, "a-product__anchorSelectState")]

    resultados = {}

    for state_name in states_names:
        try:
            cerrar_modal_disponibilidad()
            time.sleep(2)

            abrir_modal_disponibilidad()
            time.sleep(2)

            # Obtener de nuevo los estados del DOM actualizado
            states_div = driver.find_element(By.CSS_SELECTOR, ".m-product__itrSelectStates")
            states = states_div.find_elements(By.CLASS_NAME, "a-product__anchorSelectState")

            # Buscar el estado actual
            state_clicked = False
            for state in states:
                if state.text.strip() == state_name:
                    state.click()
                    state_clicked = True
                    break

            if not state_clicked:
                print(f"No se encontró el estado {state_name} en la lista")
                continue

            time.sleep(3)  # Esperar a que carguen las tiendas

            stores = driver.find_elements(By.CSS_SELECTOR, ".a-product__store")
            tiendas_estado = []

            if stores:
                print(f"\nTiendas disponibles en {state_name}:")
                for store in stores:
                    info = store.find_elements(By.TAG_NAME, "p")
                    texto_info = [p.text.strip() for p in info if p.text.strip()]
                    if texto_info:
                        print(" - " + ", ".join(texto_info))
                        tiendas_estado.append(texto_info)
            else:
                print(f"\nNo hay tiendas disponibles en {state_name}.")

            resultados[state_name] = tiendas_estado

        except Exception as e:
            print(f"Error al procesar el estado {state_name}: {e}")

    cerrar_modal_disponibilidad()
    print("\nProceso completado.")

    # Guardar en archivo JSON
    with open("disponibilidad_liverpool.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)

finally:
    driver.quit()
