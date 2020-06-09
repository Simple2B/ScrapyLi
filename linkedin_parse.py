import os
import time
from dotenv import load_dotenv

import scrapy
from selenium import webdriver
load_dotenv()

SITE_URL = os.getenv('SITE_URL')
PATH_TO_CHROME_DRIVER = os.getenv("PATH_TO_CHROME_DRIVER")
HTTP_LOGIN = os.getenv("HTTP_LOGIN")
HTTP_PASS = os.getenv("HTTP_PASS")
LOGIN_URL = os.getenv("LOGIN_URL",
                        'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')


class LinkedinSpider(scrapy.Spider):
    name = "link_parse"
    start_urls = [SITE_URL]

    def __init__(self):
        self.driver = webdriver.Chrome(PATH_TO_CHROME_DRIVER)
        if HTTP_LOGIN:
            self.site_login()

    def site_login(self):
        self.driver.get(LOGIN_URL)
        self.driver.implicitly_wait(30)
        self.driver.find_element_by_xpath(
            r'//*[@id="app__container"]/main[1]/div[2]/form[1]/div[1]/input[1]'
            ).send_keys(HTTP_LOGIN)

        self.driver.find_element_by_xpath(
            r'//*[@id="app__container"]/main[1]/div[2]/form[1]/div[2]/input[1]'
            ).send_keys(HTTP_PASS)

        self.driver.find_element_by_xpath(
            '//*[@id="app__container"]/main[1]/div[2]/form[1]/div[3]/button[1]'
            ).click()
        self.driver.implicitly_wait(30)
        time.sleep(5)

    def parse(self, response):
        self.driver.get(SITE_URL)
        self.driver.implicitly_wait(30)
        time.sleep(5)
        print('#'*100)
        data = self.driver.find_elements_by_xpath('/html/body/div[7]/div[3]/div/div/div/div/div/div/div/div/section/ul/li')
        for contact in data:
            profile = contact.find_element_by_xpath('div/a').get_attribute('href')
            print(profile)

        self.driver.close()
