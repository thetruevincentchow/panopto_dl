import time
import re
from typing import *

import urllib

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementNotInteractableException,
)

from login import login
from module import *
from video import *
from downloader import *

from settings import Settings, load_settings

load_settings()

create_base_folder(Settings.download_base_path)

driver = login()
driver.scopes = [
    ".*://s-cloudfront.cdn.ap.panopto.com/sessions/.*\\.m3u8",
    ".*://s-cloudfront.cdn.ap.panopto.com/sessions/.*\\.mp4",
    ".*://nuscast.ap.panopto.com/Panopto/Pages/Viewer/DeliveryInfo.aspx",
]


def get_list_item_text(elem) -> Optional[WebElement]:
    try:
        return elem.find_element_by_xpath("a/div[@class='name']").text
    except:
        return None


def match_module_name(
    text, pat=re.compile(r"([A-Z0-9/]+) \- \[\d+\] (\d+)/(\d+) Semester (\d)")
) -> Optional[ModuleInfo]:
    # MODULE_CODE - [year number] [year]/[year] Semester [semester]
    if type(text) is not str:
        print("Failed to match", text)
        return None
    m = pat.match(text)
    if m is not None:
        mod_name, start_year, end_year, sem = m.groups()
        return ModuleInfo(
            mod_name, ModuleTime(int(start_year), int(end_year), int(sem))
        )


def extract_module_list(folder_tree) -> Dict[ModuleInfo, str]:
    ul = WebDriverWait(folder_tree, 2).until(lambda x: x.find_element_by_tag_name("ul"))
    WebDriverWait(driver, 2).until(
        lambda x: sum(len(y.text) for y in ul.find_elements_by_tag_name("li"))
    )
    # print("\n".join(repr(k) for k in ul.find_elements_by_tag_name("li")))
    candidates = {}
    for child in ul.find_elements_by_tag_name("li"):
        text = get_list_item_text(child)
        # print(len(text), text, child)
        mod: Optional[ModuleInfo] = match_module_name(text)
        if (text is not None) and (mod is not None):
            mod: ModuleInfo
            candidates[mod] = child.get_attribute("id")
    return candidates


def print_module_titles(candidates: Dict[ModuleInfo, WebElement]):
    prev = None
    c = 0
    for k, mod in enumerate(sorted(candidates, key=lambda a: a.time)):
        if mod.time != prev:
            prev = mod.time
            print()
        print(mod.name, mod.time)
        c += 1
    if c == 0:
        print("No modules found. Did you expand some folders?")


def expand_folder_browser() -> WebElement:
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
folder_tree = expand_folder_browser()
input("Expand folders to download, then press Enter in this console")

# Assume the user may have refreshed the page, opened other windows to log in to LumiNUS, etc.
# The only requirement is that the user must be in Panopto's video selection page
# where the module list can be accessed.
folder_tree = expand_folder_browser()

candidates = extract_module_list(folder_tree)
# for mod in candidates:
#    mod: ModuleInfo
#    print(str(mod), str(mod.time))
candidates = {
    mod: index
    for mod, index in candidates.items()
    if (mod.time == Settings.target_sem) or (Settings.target_sem is None)
}
mod_names = sorted(candidates.keys(), key=lambda a: a.time)

print_module_titles(candidates)


# Now we iterate over modules
# There may be a need to reload the folder browser, if the page reloads
# but the folders should remain expanded
# TODO: automatically expand folders based on initial selection


def extract_video_list_gen():
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
            yield VideoEntry(
                video_title_a.text, video_date_span.get_attribute("title"), video_url,
            )


def extract_video_list() -> List[VideoEntry]:
    return list(extract_video_list_gen())


def extract_video_sources(url) -> List[str]:
    del driver.requests
    driver.get(url)

    # Autoplay doesn't seem to be enabled, so we need to click the play icon
    # play_button = driver.find_element_by_id("playIcon")
    try:
        play_button = WebDriverWait(driver, 2).until(
            lambda x: x.find_element_by_id("playIcon")
        )
        play_button.click()
    except ElementNotInteractableException:
        # e.g. if video isn't ready yet
        return None

    time.sleep(1)
    for attempt in range(3)[::-1]:
        r = []
        for req in driver.requests:
            r.append(req.path)
        if len([i for i in r if is_video_extension(i)]):
            break
        if attempt:
            time.sleep(3)
    else:
        return None

    return r


def extract_module_videos_gen():
    for mod in mod_names:
        # There are issues with repeatedly fetching the candidate module list

        # folder_tree = expand_folder_browser()
        # candidates = extract_module_list(folder_tree)
        # candidates[mod].click()

        # Instead, we can just go to a particular folder directly using its ID
        index = candidates[mod]
        driver.get(
            'https://nuscast.ap.panopto.com/Panopto/Pages/Sessions/List.aspx#folderID="%s"'
            % index
        )
        print(mod, "(ID: %s)" % index)

        seen = set()
        for attempt in range(3):  # TODO: fix loading issues
            try:
                for v in extract_video_list_gen():
                    key = (mod, v)
                    if key not in seen:
                        yield mod, v
                    seen.add(key)
                break
            except StaleElementReferenceException:
                continue
        else:
            print("Failed to fetch video list for module", mod)


def extract_module_videos() -> Dict[ModuleInfo, List[VideoEntry]]:
    mod_videos = {}
    for mod, v in extract_module_videos_gen():
        mod_videos.setdefault(mod, []).append(v)
    return mod_videos


# for mod, v in extract_module_videos_gen():
#    print(get_video_folder_path(Settings.download_base_path, mod, v))

mod_videos = extract_module_videos()
create_folder_paths(mod_videos, Settings.download_base_path)


num_videos = 0
for mod, videos in mod_videos.items():
    # print(mod, "has", len(videos), "videos")
    print("%s (%d videos)" % (mod, len(videos)))
    for v in videos:
        num_videos += 1

print("Found %d videos" % num_videos)

cur = 0
for mod, videos in mod_videos.items():
    # print(mod, "has", len(videos), "videos")
    print("%s (%d videos)" % (mod, len(videos)))
    for v in videos:
        cur += 1
        v: VideoEntry
        if is_video_downloaded(
            Settings.download_base_path,
            mod,
            v,
            Settings.ignore_downloaded_video_extension,
        ):
            print("(%d / %d) SKIPPED %s" % (cur, num_videos, v))
            continue
        folder_path = get_video_folder_path(Settings.download_base_path, mod, v)
        v.sources = extract_video_sources(v.embed_url())

        # print(folder_path)
        # print(len(v.sources), "sources")
        # print("\n".join(v.sources))

        if v.sources:
            print("(%d / %d) %s" % (cur, num_videos, v))
            download_video(Settings.download_base_path, mod, v)
        else:
            print("(%d / %d) FAILED %s" % (cur, num_videos, v))
    print()

print("Done! Closing browser window")
driver.close()
