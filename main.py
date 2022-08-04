from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import tkinter as tk
from orglist import OrganizationList

def get_org_links(url):
    opts = Options()
    opts.headless = True
    driver = Chrome(options=opts)
    print(f"Fetching {url}...", end=" ")
    driver.get(url)
    print("fetched.")

    delay = 1

    button_xpath = '/html/body/div[2]/div/div/div/div/div[2]/div[3]/div/div[2]/div[2]/button'

    print("Loading all organizations (this might take a while)...", end=" ")

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

    print("loaded.")

    links = driver.find_elements(By.TAG_NAME, "a")
    links = [link.get_attribute("href") for link in links if "engage/organization/" in link.get_attribute("href")]

    driver.close()

    print("Organization links found and Selenium web driver closed.")

    return links

def main():
    URL = "https://gatech.campuslabs.com/engage/organizations?query=eco"

    links = get_org_links(URL)

    root = tk.Tk()
    OrganizationList(root, links).pack(side="top", fill="both", expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()