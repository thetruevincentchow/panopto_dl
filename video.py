from typing import *
from datetime import datetime
import urllib


# NOTE: viewer and embed URLs:
# Viewer: https://nuscast.ap.panopto.com/Panopto/Pages/Viewer.aspx?id={PublicID}')
# Embed: https://nuscast.ap.panopto.com/Panopto/Pages/Embed.aspx?id={PublicID}&v=1&internal=true&autoplay=true


class VideoEntry:
    def __init__(self, title, date, url, sources=None):
        self.title = title
        self.date = date
        self.url = url

        # video sources
        self.sources = sources
        # TODO: video slides

    def embed_url(self):
        return (
            r"https://nuscast.ap.panopto.com/Panopto/Pages/Embed.aspx?id=%s&v=1&internal=true&autoplay=true"
            % (self.id())
        )

    def date_as_datetime(self) -> datetime:
        return datetime.strptime(self.date, "%a, %m/%d/%Y %I:%M %p")

    def to_file_name(self):
        d = self.date_as_datetime()
        return "%s_%s_%s" % (
            d.isoformat(),
            d.strftime("%a"),
            self.title.replace("/", "-"),
        )

    def id(self):
        q = urllib.parse.urlparse(self.url).query
        return urllib.parse.parse_qs(q)["id"][0]

    def __str__(self):
        return "<Video %r on %s>" % (self.title, self.date)

    def __repr__(self):
        return "VideoEntry%r" % ((self.title, self.date, self.url, self.sources),)
