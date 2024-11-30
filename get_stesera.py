import requests, json
from bs4 import BeautifulSoup

URL = "https://www.staseraintv.com"

output = {"highlights": {}}

for i in range(1, 10):
    page = requests.get(f"{URL}/index{i}.html").content
    soup = BeautifulSoup(page, "html.parser")
    for canale, continua in zip(soup.find_all("chnum"), soup.select("html body div.container div.header div.chpreviewbox div.singlechprevbox div.thumbprevbox table tbody tr td table tbody tr th table tbody tr th.prgpreviewtext a")):
        if canale.text.isnumeric():
            canale = int(canale.text)
            output["highlights"][canale] = {}

            programma_page = requests.get(f"{URL}{continua["href"]}").content
            soup2 = BeautifulSoup(programma_page, "html.parser")

            # get title
            title = soup2.select_one("html body div.container div.header div.maincolumn div.schedabox h1")
            output["highlights"][canale]["title"] = title.text

            # get description
            desc = soup2.select_one("html body div.container div.header div.maincolumn div.schedabox")
            output["highlights"][canale]["description"] = str(desc.text.split("  ")[6].replace("\n", "").replace("\r", ""))

            # get program info
            info_list = soup2.select(".schedatavbox li")
            if len(info_list) > 0:
                if len(info_list[-1].text) < 8:
                    info = "\n".join(i.text for i in info_list[:-1])
                else:
                    info = "\n".join(i.text for i in info_list)
                output["highlights"][canale]["info"] = info

            # get trailer link
            link_trailer = soup2.select_one("div.video-container iframe")
            if link_trailer != None:
                output["highlights"][canale]["trailer"] = link_trailer["src"]

            # get channel name
            with open("canali.json", "r") as canali_file:
                canali = json.load(canali_file)
            output["highlights"][canale]["channel"] = canali[str(canale)]

            # get image
            image = soup2.select_one("html body div.container div.header div.maincolumn div.schedabox img")
            image_url = URL + "/".join(continua["href"].split("/")[:-1]).replace(" ", "") + "/" + image["src"].replace(" ", "")
            try:
                response = requests.get(image_url, stream=True).content
                with open(f'./images/{canale}.jpg', 'wb') as f:
                    f.write(response)
            except:
                output["highlights"][canale]["image"] = image_url


                

output["highlights"] = dict(sorted(output["highlights"].items()))

output_file = open("stasera.json", "w")
output_file.write(json.dumps(output))
output_file.close()