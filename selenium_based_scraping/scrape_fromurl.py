from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
import os
import time
import pickle


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
cow_image_path = os.path.join(BASE_DIR, "cow_images")

def save_additional_image(driver, url, all_cattle_data):

    global cow_image_path

    wait = WebDriverWait(driver, 120)

    temp_dict = dict()
    temp_image_path_dict = dict()
    i = 1

    driver.get(url)
    wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')

    wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="specification"]')))
    cattle_div_specifications = driver.find_elements_by_xpath('//div[@class="specification"]')
    for specification in cattle_div_specifications:
        
        datas = specification.find_elements_by_xpath('./h4')
        for data in datas:
            temp_text = str(data.text)
            text_data = temp_text.split(":")
            text_data[0] = text_data[0].strip()
            text_data[1] = text_data[1].strip()
            temp_dict[text_data[0]] = text_data[1]

    xpath_cattle_description = '//div[@class="swiper-wrapper"]'
    cattle_image_div_outer = driver.find_element_by_xpath(xpath_cattle_description)
    cattle_image_div_inner = cattle_image_div_outer.find_elements_by_xpath('//div')

    for div_image in cattle_image_div_inner:
        image_path = str(div_image.value_of_css_property("background-image"))
        if image_path != "none":
            image_path = image_path.split('"')
            try:
                image_path = image_path[1]
                image_path_to_write = image_path.split("/")[-1]

                if image_path_to_write != "classification2.jpg":
                    #print(image_path)
                    image = requests.get(image_path)
                    image_path_to_write = os.path.join(cow_image_path, image_path_to_write)
                    with open(image_path_to_write, "wb") as f:
                        f.write(image.content)
                    
                    temp_image_path_dict["image " + str(i)] = image_path_to_write
                    i = i + 1
            except:
                print(image_path)
    
    temp_dict["images"] = temp_image_path_dict
    all_cattle_data.append(temp_dict)
        

    return all_cattle_data


def main():
    global cow_image_path
    if not os.path.exists(cow_image_path):
        os.mkdir(cow_image_path)

    driver = webdriver.Chrome("./chromedriver")
    driver.maximize_window()
    all_cattle_data = list()

    with open("url_set.pkl", "rb") as f:
        url_set = pickle.load(f)

    print(url_set[0])

    for url in url_set:
        save_additional_image(driver, url, all_cattle_data)
        print(all_cattle_data)
    
    with open("all_cow_data.pickle", "wb") as f:
        pickle.dump(all_cattle_data, f)

if __name__ == '__main__':
    main()
