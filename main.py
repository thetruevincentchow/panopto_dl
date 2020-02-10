import re
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from login import login

driver = login()


def get_list_item_text(elem):
    try:
        return elem.find_element_by_xpath("a/div[@class='name']").text
    except:
        return None


class ModuleTime:
    def __init__(self, start_year, end_year, sem):
        self.start_year = start_year
        self.end_year = end_year
        self.sem = sem
    
    def key(self):
        return (self.start_year, self.end_year, self.sem)
    
    def __lt__(self, other):
        return self.key() < other.key()
    
    def __eq__(self, other):
        if type(self) is not type(other):
            return False
        return self.key() == other.key()
    
    def __hash__(self):
        return hash(self.key())
    
    def __repr__(self):
        return "ModuleTime%r" % (self.key(),)


def match_module_name(
    text, pat=re.compile(r"([A-Z0-9/]+) \- \[\d+\] (\d+)/(\d+) Semester (\d)")
):
    # MODULE_CODE - [year number] [year]/[year] Semester [semester]
    if type(text) is not str:
        print("Failed to match", text)
        return None
    m = pat.match(text)
    if m is not None:
        mod_name, start_year, end_year, sem = m.groups()
        return mod_name, ModuleTime(int(start_year), int(end_year), int(sem))


def extract_module_list(folder_tree):
    ul = WebDriverWait(folder_tree, 2) \
        .until(lambda x: x.find_element_by_tag_name("ul"))
    candidates = {}
    for child in ul.find_elements_by_tag_name("li"):
        text = get_list_item_text(child)
        x = match_module_name(text)
        if (text is not None) and (x is not None):
            module, sem = x
            candidates[(module, sem)] = child
    return candidates


def print_module_titles(candidates):
    prev = None
    c = 0
    for k, (mod_name, sem, elem) in enumerate(candidates):
        if sem != prev:
            prev = sem
            print()
        print(mod_name, sem)
        c += 1
    if c == 0:
        print("No modules found. Did you expand some folders?")


folder_browser = WebDriverWait(driver, 2).until(
    lambda x: x.find_element_by_id("folderBrowser")
)

browse_folder = driver.find_element_by_id("folderSelector")
if "display: none" in folder_browser.get_attribute("style"):
    browse_folder.click()

folder_tree = WebDriverWait(folder_browser, 2).until(
    lambda x: x.find_element_by_id("folderTree")
)
input("Expand folders to download, then press Enter in this console")

candidates = extract_module_list(folder_tree)

target_sem = ModuleTime(2019, 2020, 2)
print_module_titles(candidates)
