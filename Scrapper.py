from bs4 import Tag, NavigableString, BeautifulSoup
import re
import os

from libretranslatepy import LibreTranslateAPI
#Google translate api has 400 request limit because of it i use self hosted libretranslate
lt = LibreTranslateAPI("http://some.vali.libratranslateapi:5000")

import cloudscraper
scraper = cloudscraper.create_scraper(delay=100, browser='chrome')

def ChangeNode(soupObj, collectRefs):
    refs = []

    def getStr( node , transNode):
        for (n, a) in zip(node.children, transNode.children):
            if( n != "html" and (isinstance(n, Tag) or (len(re.findall("^[\s\n]*$", n)) == 0) )):
                if(n.name == "script" or n.name == "style"):
                    continue
                if(isinstance(n, NavigableString)):
                    #Language selection
                    a.replaceWith( lt.translate(a, "en", "hi"))
                    return
                if( "placeholder" in n.attrs.keys()):
                    a.attrs["placeholder"] = lt.translate(a.attrs["placeholder"], "en", "hi")
                else:
                    getStr(n, a)
            if(collectRefs and n.name == "a" and ( "href" in n.attrs.keys())):
                refs.append(n.attrs["href"])

    obj = soupObj
    trans = obj.__copy__()

    getStr(obj, trans)

    return (trans, refs)

def RecursiveThing(firstURL, Depth):
    BaseURL = firstURL

    currentLevel = [BaseURL]
    nextLevel = []

    for i in range(Depth):
        for url in currentLevel:
            if(not url.startswith("http")):
                url = BaseURL + url
            page =  scraper.get(url).text
            soup = BeautifulSoup(page, "html5lib")
            soup, refs = ChangeNode(soup, True if not i == (Depth-1) else False)
            if (not i == (Depth-1)):
                nextLevel = nextLevel + refs

            if(url.replace(BaseURL, "").strip("/") != ""):
                os.makedirs(url.replace(BaseURL, "").strip("/"), exist_ok=True)
            f = open((url.replace(BaseURL, "") + "/index.html").strip("/") , "wb")
            f.write(soup.encode('utf-8'))
            f.close()
        currentLevel = nextLevel
        nextLevel = []

URL = "https://some.valid.url"
DEPTH = 2

RecursiveThing(URL, DEPTH)
