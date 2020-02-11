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
                "         `ignore_downloaded_video_extension` = %r\n"
                "         does not have a leading '.'" % ext
            )
            ext = ".%s" % ext
            print("Interpreting extension as %r." % ext)
        Settings.ignore_downloaded_video_extension = ext
    elif ext is None:
        pass
    else:
        print(
            "Warning: invalid `ignore_downloaded_video_extension`, defaulting to %r."
            % Settings.ignore_downloaded_video_extension
        )


def load_settings():
    print("Loading settings from 'settings.json':")
    try:
        with open("settings.json") as f:
            tree = json.load(f)

        if "download_base_path" in tree:
            base_path = tree["download_base_path"]
            if type(base_path) is str:
                Settings.download_base_path = base_path
                print("Base path at %r." % base_path)
            else:
                print(
                    "Warning: `download_base_path` should be a string, but is %r."
                    % base_path
                )
                print(
                    "         Using default value of %r." % Settings.download_base_path
                )
        else:
            print("Warning: `download_base_path` is missing." % base_path)
            print("         Using default value of %r." % Settings.download_base_path)

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
            print("Warning: `target_sem` has invalid format.")
            print("         Using default value of %r." % Settings.target_sem)
    except FileNotFoundError:
        print("Warning: Configuration file 'settings.json' not found")
        print("         Using default values.")
    except (JSONDecodeError, ValueError) as e:
        print("Warning: Configuration file 'settings.json' has invalid JSON")
        print("         Using default values.")

    print("Target semester: %s." % (Settings.target_sem or "All"))
    if Settings.ignore_downloaded_video_extension:
        print(
            "Ignoring downloaded videos with extension %s."
            % Settings.ignore_downloaded_video_extension,
        )
    else:
        print("Not ignoring any downloaded videos.")
    print()


if __name__ == "__main__":
    load_settings()
