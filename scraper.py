import os
import time
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from PIL import Image
import requests
from selenium.webdriver.chrome.options import Options
from io import BytesIO
from constants import class_map

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_image(img_url, save_dir, count):
    try:
        if img_url.startswith("data:image"):
            img_data = base64.b64decode(img_url.split(",")[1])
            file_path = os.path.join(save_dir, f"image_{count}.jpg")
            with open(file_path, "wb") as f:
                f.write(img_data)
        else:
            response = requests.get(img_url, timeout=5)
            img = Image.open(BytesIO(response.content))
            file_path = os.path.join(save_dir, f"image_{count}.jpg")
            img.convert("RGB").save(file_path, "JPEG")
    except Exception as e:
        print(f"Could not save image {count}: {e}")

MAX_SCROLLS = 2
def scrape_images_with_alt(query, save_dir, start_count):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.google.com/imghp")
    time.sleep(1)
    
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(1)
    for _ in range(MAX_SCROLLS):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

    images_with_alt = driver.execute_script(
        "return Array.from(document.querySelectorAll('img[alt]:not([alt=\"\"])')).map(img => img.src);"
    )

    img_count = start_count
    for img_url in images_with_alt:
        save_image(img_url, save_dir, img_count)
        img_count += 1
        print(f"Saved image {img_count} from query '{query}'")

    driver.quit()
    return img_count

def remove_small_images(directory, min_size=120):
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        try:
            with Image.open(file_path) as img:
                if img.size[0] < min_size or img.size[1] < min_size:
                    os.remove(file_path)
                    print(f"Removed small image: {file_name} (Size: {img.size})")
        except Exception as e:
            print(f"Could not process file {file_name}: {e}")

if __name__ == "__main__":
    '''
    class_map contains the description of all classes, numerated.
    check out constants.py
    leave only the classes you are assigned for.
    And add more descriptors for each class.
    Each descriptor of a class is stored in its index folder.
    for example:
        0: ['backpack', 'blue backpack'] will combine the results
        and save the results to the folder /data/0
    
    MAX_SCROLLS is the number which determines the number of page scrolls Selenium makes
    before starting saving the images.
    '''
    for key, queries in class_map.items():
        save_dir = os.path.join("data", str(key))
        create_directory(save_dir)
        count = 0
        for query in queries:
            print(f"Scraping images for query: '{query}'")
            count = scrape_images_with_alt(query, save_dir, count)
        print("Removing small images...")
        remove_small_images(save_dir, min_size=120)