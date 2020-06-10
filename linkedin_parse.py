import os
import time
import csv
from dotenv import load_dotenv

import scrapy
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
load_dotenv()

PAGE_SCROLING_TIME = 1
SITE_URL = os.getenv('SITE_URL')
PATH_TO_CHROME_DRIVER = os.getenv("PATH_TO_CHROME_DRIVER")
HTTP_LOGIN = os.getenv("HTTP_LOGIN")
HTTP_PASS = os.getenv("HTTP_PASS")
LOGIN_URL = os.getenv("LOGIN_URL",
                      "https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin")


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
        time.sleep(1)

    def parse(self, response):
        self.driver.get(SITE_URL)
        self.driver.implicitly_wait(30)
        time.sleep(1)
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(PAGE_SCROLING_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        data = self.driver.find_elements_by_xpath(
            '/html/body/div[7]/div[3]/div/div/div/div/div/div/div/div/section/ul/li')
        urls = [contact.find_element_by_xpath(
            'div/a').get_attribute('href') for contact in data]
        with open('contacts.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',  quoting=csv.QUOTE_MINIMAL)
            for profile in urls:
                self.driver.get(profile)
                name = self.driver.find_element_by_css_selector(
                    'li.inline.t-24.t-black.t-normal.break-words').text
                try:
                    job = self.driver.find_element_by_css_selector('div.pv-entity__summary-info.pv-entity'
                                                                   '__summary-info--background-section > h3').text
                except NoSuchElementException:
                    job = 'Not employed'

                self .driver.get(profile + 'detail/contact-info/')
                try:
                    mailto = self.driver.find_element_by_css_selector('div > section.pv-contact-info'
                                                                      '__contact-type.ci-email > div > a')
                    mail = mailto.get_attribute('href').replace('mailto:', '')
                except NoSuchElementException:
                    mail = 'No email'
                spamwriter.writerow([name, job, mail])

        self.driver.close()
