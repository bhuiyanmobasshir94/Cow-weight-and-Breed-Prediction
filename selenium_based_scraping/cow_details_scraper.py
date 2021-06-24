from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
import os
import time
import pickle

def save_base_image(element, cow_image_path, temp_image_path_dict, i):

    if not os.path.exists(cow_image_path):
        os.mkdir(cow_image_path)

    base_img_element = element.find_element_by_xpath('./img')
    base_img_url = str(base_img_element.get_attribute("src"))
    print(base_img_url)
    
    base_img = requests.get(base_img_url)
    save_base_img_path = str(base_img_url.split('/')[-1])

    save_base_img_path = os.path.join(cow_image_path, save_base_img_path)
    #print(element.text)

    with open(save_base_img_path, "wb") as f:
        f.write(base_img.content)
    temp_image_path_dict["image"+str(i)] = save_base_img_path
    

def save_additional_image(all_cattle_data, elements, cow_image_path, driver):

    for cattle in elements:

        temp_dict = dict()
        temp_image_path_dict = dict()
        i = 1
        save_base_image(cattle, cow_image_path, temp_image_path_dict, i)
        i = i + 1

        div_card_button = cattle.find_element_by_xpath('//div[@class="cattle__featured__card__button"]/span')
        div_card_button.click()
        cattle_description_url = driver.current_url

        driver_cattle_page = webdriver.Chrome("./chromedriver")
        driver_cattle_page.maximize_window()
        driver_cattle_page.get(cattle_description_url)


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

def urlchanged(old, new):

    if old != new:
        return new

def main():

    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    cow_image_path = os.path.join(BASE_DIR, "cow_images")

    if not os.path.exists(cow_image_path):
        os.mkdir(cow_image_path)

    #driver = webdriver.Chrome("./chromedriver")
    driver = webdriver.Chrome("./chromedriver")
    driver.maximize_window()
    driver.implicitly_wait(120)
    all_cattle_data = list()

    base_url = "https://loyalty.bengalmeat.com/cattle/all"
    driver.get(base_url)
    #source = driver.page_source

    prev_page_url = ""
    cur_page_url = str(driver.current_url)
    #print(cur_page_url)
    wait = WebDriverWait(driver, 120)

    old_url = ""
    new_url = str(driver.current_url)

    while(old_url != new_url):

        old_url = new_url
    
        xpath_all_cattles_button = '//div[@class="cattle__featured__card"]'
        xpath_content = '//div[@class="content"]'
        bmp_cattle_list = '//bmq-cattle-list[@class="ng-star-inserted"]'
        cattle__details_list = driver.find_elements_by_xpath(xpath_all_cattles_button)

        all_cattle_data = save_additional_image(all_cattle_data, cattle__details_list, cow_image_path, driver)

        print(all_cattle_data)
        driver.get(new_url)
        time.sleep(30)

        wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="cattle-list__pagination"]')))
        buttons = driver.find_elements_by_xpath('//button[@class="btn btn--primary"]')

        #Press Next
        for button in buttons:
            print(str(button.text))
            if str(button.text) == "NEXT":
                button.click()

        wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
        wait.until(lambda driver: new_url != driver.current_url)
        new_url = str(driver.current_url)
        driver.get(new_url)


    
    
    with open("all_cow_data.pickle", "wb") as f:
        pickle.dump(all_cattle_data, f)
    

    driver.quit()

if __name__ == '__main__':

    main()




