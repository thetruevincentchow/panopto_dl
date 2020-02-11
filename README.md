# panopto_dl
Mass-download lecture videos from NUS Panopto.

---

`panopto_dl` is a Python program using Selenium to navigate video listing pages in Panopto.  Requests to media files are captured and their URLs are used to download their corresponding lecture videos.
Since `panopto_dl` simulates key presses and mouse clicks, it does not depend on any API and will work if access to Panopto is available.

## What you need
* NUSNET account and access to [NUS Panopto](https://nuscast.ap.panopto.com/Panopto/)
* Python >= 3.5
* Python packages listed in `requirements.txt`
* Google Chrome or Chromium (for [Selenium WebDriver](https://selenium.dev/downloads/))

## Setup
1. Clone this repository on the command line
```sh
git clone https://github.com/thetruevincentchow/panopto_dl && cd panopto_dl
```
2. Install all required packages
```sh
python3 -m pip install -r requirements.txt
```

## How to use
1. Run `python3 main.py` in a terminal.
2. Follow the prompts in the console to log in to Panopto.
When presented with the "Browse" drop-down menu of modules, click on the "LumiNUS" drop-down item to expand it.
3. Press Enter in the console to start downloading videos.
4. Videos will be saved in the path specified by `download_base_path` in the `settings.json` file.


## Configuration
The `settings.json` configuration file looks like this (comments added for clarity).

```javascript
{
    /* 1. The relative path where videos are saved.
          Absolute paths can also be specified, and '~' will be expanded to the home directory. */
    "download_base_path": "videos",

    /* 2. Target semester for module videos.
          All available videos are downloaded if this is set to `null`. */
    "target_sem": {

        /* For example, this denotes "AY 2019/2020 Sem 2".
           Only videos from this semester will be downloaded */
        "start_year": 2019,
        "end_year": 2020,
        "sem": 2
    },

    /* 3. Extension of fully downloaded videos
          Files required to ignore the correpsonding video links on Panopto.
          All videos are checked for their video sources if this is set to `null`. */
    "ignore_downloaded_video_extension": ".mp4"
}
```

The default `target_sem` is `null`, while the default (sample) configuration file uses AY 2019/2020 Sem 2.
Do change this to your desired semester (or `null` if you want to download lecture videos from all semesters).

---

Another example of a valid configuration file is:
```javascript
{
    "download_base_path": "~/Videos/Lectures",
    "target_sem": null,
    "ignore_downloaded_video_extension": null
}
```

As stated in the above sample configuration file, specifying `null` is allowed for `target_sem` and `ignore_downloaded_video_extension`.

## Planned features
- Support for lecture videos hidden on LumiNUS
- Support for selecting and downloading multiple streams
- General improvements to synchronization
- Parallel crawling of video listing pages
