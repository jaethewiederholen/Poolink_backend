from grabicon import FaviconGrabber


class Favicon():

    def get_favicon(self, url=None):

        grabber = FaviconGrabber()
        try:
            favicons = grabber.grab(url)
        except Exception as e:
            print(e)
            return None

        if favicons is None or len(favicons) == 0:
            return None

        else:
            favicon = None
            max = 0
            for i in range(len(favicons)):
                if max < favicons[i].size:
                    max = favicons[i].size
                    favicon = favicons[i]

            return favicon.url
