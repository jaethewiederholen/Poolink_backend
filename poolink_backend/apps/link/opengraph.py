from opengraph.opengraph import OpenGraph


class LinkImage:

    def get_link_image(self, url):
        try:
            image = OpenGraph(url=url)
            return image.image
        except Exception as e:
            print(e)
            return None


'''
from urllib.error import URLError

import pandas as pd
import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class LinkImage:

    def get_page(url):
        req = urllib.request.Request(url)
        try:
            response = urllib.request.urlopen(req)

            soup = BeautifulSoup(response,
                                 'html.parser',
                                 from_encoding=response.info().get_param('charset'))

            return soup
        except URLError as e:
            if hasattr(e, 'reason'):
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'):
                print('The server couldn\'t fulfill the request.')
                print('Error code: ', e.code)

        #response = response.decode('utf-8')


    def get_og_iamge(self,soup):
        if soup.findAll("meta", property="og:image"):
            return soup.find("meta", property="og:image")["content"]
        else:
            return

        return
'''
