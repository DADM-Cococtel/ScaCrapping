from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

def scrape_product_data():
    """Realiza el scraping de la página y devuelve los datos del producto."""
    options = Options()
    options.add_argument("--headless")  # Modo sin interfaz gráfica
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Iniciar el driver
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # URL de la página
        url = "https://www.gs1.org/services/verified-by-gs1/iframe?gtin=7702049101337#productInformation"
        driver.get(url)

        # Aceptar cookies
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        ).click()

        # Aceptar términos de uso
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "btn-accept"))
        ).click()

        # Esperar a que cargue la información del producto
        product_info = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "productInformation"))
        )

        # Extraer la información del producto
        product_text = product_info.text.split("\n")
        product_data = {
            "name": product_text[0],
            "gtin": product_text[1].split(" ")[1],
            "brand_name": product_text[2].split('Brand name ' )[1],
            "product_description": product_text[3].split('Product description ')[1],
            "product_image_url": product_text[4].split(" ")[-1],
            "global_product_category": product_text[5].split("Global product category ")[1],
            "net_content": product_text[6].split("Net content ")[1],
            "country_of_sale": product_text[7].split("Country of sale ")[1],
        }

        return product_data
    finally:
        driver.quit()

@app.route('/product-info', methods=['GET'])
def get_product_info():
    """Endpoint que realiza scraping y retorna información del producto."""
    try:
        product_data = scrape_product_data()
        return jsonify(product_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
