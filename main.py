
# session = HTMLSession()
# r = session.get(URL)
# r.html.render()

# # print(r.html.text)

# # for html in r.html:
# #     print(html)
# #     # for link in html.absolute_links:
# #     #     print(link)

# while 

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from requests_html import HTMLSession
import requests
from bs4 import BeautifulSoup

URL = "https://gatech.campuslabs.com/engage/organizations?query=eco"

opts = Options()
opts.headless = True

driver = Chrome(options=opts)
driver.get(URL)

delay = 1

button_xpath = '/html/body/div[2]/div/div/div/div/div[2]/div[3]/div/div[2]/div[2]/button'

try:
    load_more = driver.find_element(By.XPATH, button_xpath)
    prev_src = ""
    while prev_src != driver.page_source:
        prev_src = driver.page_source
        load_more.click()
        try:
            load_more = WebDriverWait(driver, delay).until(expected_conditions.presence_of_element_located((By.XPATH, button_xpath)))
        except TimeoutException:
            break
except NoSuchElementException:
    pass

links = driver.find_elements(By.TAG_NAME, "a")
links = [link.get_attribute("href") for link in links if "engage/organization/" in link.get_attribute("href")]

driver.close()

print(f"{len(links)} organizations found.")

# session = HTMLSession()

# for link in links:
#     page = session.get(link)
#     page.html.render()
#     print(page.html.find("#react-app", first=True).text)

def get_page_desc(html_text):
    page_desc_begin = "window.initialAppState = "
    page_desc_end = ";</script>"
    new_text = html_text[html_text.find(page_desc_begin) + len(page_desc_begin):]
    new_text = new_text[:new_text.find(page_desc_end)]
    print(new_text)

for link in links:
    page = requests.get(link)
    get_page_desc(str(page.content))