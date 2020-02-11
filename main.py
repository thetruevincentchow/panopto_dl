import time
import re
from typing import *

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

from login import login

driver = login()


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


Module = Tuple[str, ModuleTime]


def get_list_item_text(elem):
    try:
        return elem.find_element_by_xpath("a/div[@class='name']").text
    except:
        return None


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


def extract_module_list(folder_tree) -> Dict[Module, str]:
    ul = WebDriverWait(folder_tree, 2).until(lambda x: x.find_element_by_tag_name("ul"))
    WebDriverWait(driver, 2).until(
        lambda x: sum(len(y.text) for y in ul.find_elements_by_tag_name("li"))
    )
    # print("\n".join(repr(k) for k in ul.find_elements_by_tag_name("li")))
    candidates = {}
    for child in ul.find_elements_by_tag_name("li"):
        text = get_list_item_text(child)
        # print(len(text), text, child)
        x = match_module_name(text)
        if (text is not None) and (x is not None):
            module, sem = x
            candidates[(module, sem)] = child.get_attribute("id")
    return candidates


def print_module_titles(candidates: Dict[Module, WebElement]):
    prev = None
    c = 0
    for k, (mod_name, sem) in enumerate(sorted(candidates, key=lambda a: a[1])):
        if sem != prev:
            prev = sem
            print()
        print(mod_name, sem)
        c += 1
    if c == 0:
        print("No modules found. Did you expand some folders?")


def expand_folder_browser():
    folder_browser = WebDriverWait(driver, 2).until(
        lambda x: x.find_element_by_id("folderBrowser")
    )

    browse_folder = driver.find_element_by_id("folderSelector")
    if "display: none" in folder_browser.get_attribute("style"):
        print("Expanded folder list")
        browse_folder.click()

    folder_tree = WebDriverWait(folder_browser, 2).until(
        lambda x: x.find_element_by_id("folderTree")
    )
    return folder_tree


# Initial user selection
target_sem = ModuleTime(2019, 2020, 2)

folder_tree = expand_folder_browser()
input("Expand folders to download, then press Enter in this console")

candidates = extract_module_list(folder_tree)
candidates = {
    (mod_name, sem): index
    for (mod_name, sem), index in candidates.items()
    if sem == target_sem
}
module_names = sorted(candidates.keys(), key=lambda a: a[1])

print_module_titles(candidates)


# Now we iterate over modules
# There may be a need to reload the folder browser, if the page reloads
# but the folders should remain expanded
# TODO: automatically expand folders based on initial selection


def extract_video_list():
    time.sleep(1)  # TODO: fix waiting issues properly
    driver.implicitly_wait(2)
    results_div = driver.find_element_by_id("resultsDiv")
    driver.implicitly_wait(2)
    videos_table = results_div.find_element_by_xpath(
        "div[@class='content-table-list']/table[@id='detailsTable']/tbody"
    )

    driver.implicitly_wait(2)
    children = videos_table.find_elements_by_tag_name("tr")
    print(len(children), "videos")
    r = []
    for video_tr in children:
        if video_tr.get_attribute("id") != "panePlaceholder":
            video_title_a = video_tr.find_element_by_xpath(
                "td[@class='detail-cell']/div/a"
            )
            video_date_span = video_tr.find_element_by_xpath(
                "td[@class='detail-cell']/div/span/span"
            )

            video_url = video_title_a.get_attribute("href")
            # print(video_title_span, video_date_span)
            r.append(
                (video_title_a.text, video_date_span.get_attribute("title"), video_url)
            )
    return r


for mod in module_names:
    # There are issues with repeatedly fetching the candidate list
    # folder_tree = expand_folder_browser()
    # candidates = extract_module_list(folder_tree)
    # candidates[mod].click()

    # Instead, we can just go to a particular folder directly
    index = candidates[mod]
    driver.get(
        'https://nuscast.ap.panopto.com/Panopto/Pages/Sessions/List.aspx#folderID="%s"'
        % index
    )
    print(mod, index)
    for x in extract_video_list():
        print(x)
    print()
