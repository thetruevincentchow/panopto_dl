import json
from json.decoder import JSONDecodeError
from module import *

# Default values
class Settings:
    download_base_path = "videos"
    target_sem = None
    ignore_downloaded_video_extension = None


def load_extension(tree):
    ext = tree.get("ignore_downloaded_video_extension")
    if type(ext) is str:
        if not ext.startswith("."):
            print(
                "Warning: extensions should start with '.', but extension from\n"
                "         ignore_downloaded_video_extension = %r\n"
                "         does not have a leading '.'" % ext
            )
            ext = ".%s" % ext
            print("Interpreting extension as %r" % ext)
        Settings.ignore_downloaded_video_extension = ext
    elif ext is None:
        pass
    else:
        print(
            "Warning: invalid ignore_downloaded_video_extension, defaulting to",
            Settings.ignore_downloaded_video_extension,
        )


def load_settings():
    try:
        with open("settings.json") as f:
            tree = json.load(f)
        Settings.download_base_path = tree.get("download_base_path", "videos")
        x = tree.get("target_sem", Settings.target_sem)

        if type(x) is dict:
            start_year = x.get("start_year")
            end_year = x.get("end_year")
            sem = x.get("sem")
            if all(type(x) is int for x in (start_year, end_year, sem)):
                Settings.target_sem = ModuleTime(start_year, end_year, sem)

            load_extension(tree)
        elif x is None:
            pass
        else:
            raise ValueError
    except FileNotFoundError:
        print("Warning: Configuration file 'settings.json' not found")
        print("Using default values.")
    except (JSONDecodeError, ValueError) as e:
        print("Warning: Configuration file 'settings.json' has invalid JSON")
    print("Target semester: %s" % (Settings.target_sem or "All"))
    if Settings.ignore_downloaded_video_extension:
        print(
            "Ignoring downloaded videos with extension",
            Settings.ignore_downloaded_video_extension,
        )
    else:
        print("Not ignoring any downloaded videos")
    print()


if __name__ == "__main__":
    load_settings()
