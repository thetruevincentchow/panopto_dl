import os
import re
from pathlib import Path
import urllib.request
import shutil

from module import *
from video import *


def resolve_path(path: str):
    return os.path.abspath(Path(path).expanduser())


def get_video_folder_path(base_path: str, mod: ModuleInfo, video: VideoEntry):
    folder_path = os.path.join(base_path, mod.to_file_name(), video.to_file_name())
    return resolve_path(folder_path)


def create_base_folder(base_path: str):
    try:
        os.makedirs(base_path)
        print("Created base folder at", resolve_path(base_path))
        return True
    except OSError:
        print("Base folder alread exists at", resolve_path(base_path))
        return False


def create_folder_paths(mod_videos: Dict[ModuleInfo, List[VideoEntry]], base_path: str):
    for mod, videos in mod_videos.items():
        print(mod, "has", len(videos), "videos")
        for v in videos:
            folder_path = get_video_folder_path(base_path, mod, v)
            try:
                os.makedirs(folder_path)
                print("Creating", folder_path)
            except OSError:
                pass


def is_video_extension(url: str):
    path = urllib.parse.urlparse(url).path
    ext = os.path.splitext(path)[1]
    return ext in (".mp4", ".m3u8")


def resolve_video_source(
    sources: List[str],
    pat=re.compile(
        r".*://s-cloudfront.cdn.ap.panopto.com/sessions/([a-zA-Z0-9\-]+)/([a-zA-Z0-9\-]+)\."
    ),
):
    sources = [s for s in sources if is_video_extension(s)]
    # print(len(sources))
    if len(sources) == 0:
        return None

    # These are 3 common URLs:
    # https://s-cloudfront.cdn.ap.panopto.com/sessions/{session_id}/{public_id}.mp4
    # https://s-cloudfront.cdn.ap.panopto.com/sessions/{session_id}/{public_id}.hls/master.m3u8
    # https://s-cloudfront.cdn.ap.panopto.com/sessions/{session_id}/{public_id}.hls/{object_sequence_id}/master.m3u8
    # so we just need to parse enough of the URLs to find matching session and public IDs

    ms = [pat.match(s) for s in sources]
    if all(type(m) is re.Match for m in ms):
        ids = ms[0].groups()
        for m in ms:
            if ids != m.groups():
                break
        else:
            return "https://s-cloudfront.cdn.ap.panopto.com/sessions/%s/%s.mp4" % ids

    us = [s for s in sources if (".mp4" in s)] or [  # otherwise, try to find .mp4
        s for s in sources if ("master.m3u8" in s)
    ]  # otherwise, try to find master.m3u8
    return (us or [None])[0]


# TODO: download slides
def download_video(base_path: str, mod: ModuleInfo, video: VideoEntry):
    assert video.sources
    main_source = resolve_video_source(video.sources)
    ext = os.path.splitext(main_source)[1]
    assert type(main_source) is str

    download_folder = get_video_folder_path(base_path, mod, video)
    # print(main_source)
    # print(download_folder)
    video_path = os.path.join(download_folder, "video%s" % ext)
    temp_path = os.path.join(download_folder, "video_partial%s" % ext)

    if os.path.isfile(video_path):
        print("Skipping %s %s" % (mod, video))
        return

    print("Downloading", main_source, "to", temp_path)
    with urllib.request.urlopen(main_source) as res:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(res, f, 2 ** 20)  # 1 MB chunks

    print("Moving", temp_path, "to", video_path)
    shutil.move(temp_path, video_path)


if __name__ == "__main__":
    from private.mod_info import mod_videos, download_base_path

    create_base_folder(download_base_path)
    create_folder_paths(mod_videos, download_base_path)

    c = 0
    for mod, videos in mod_videos.items():
        c += len(videos)

    cur = 0
    for mod, videos in mod_videos.items():
        print("%s (%d videos)" % (mod, len(videos)))
        for v in videos:
            cur += 1
            print("(%d / %d) %s" % (cur, c, v))
            download_video(download_base_path, mod, v)
