import requests, json
from bs4 import BeautifulSoup
import re, os

DIR = os.environ.get("DIR", f"/usr/src/app")

def main():
    if not os.path.exists(f"{DIR}/data/images/"):
        os.makedirs(f"{DIR}/data/images/")

    URL = "https://www.staseraintv.com"

    output = {"highlights": {}}
    backup_images = {}

    with open(f"{DIR}/canali.json", "r") as canali_file:
        canali = json.load(canali_file)
    for i in range(1, 10):
        page = requests.get(f"{URL}/index{i}.html").content
        soup = BeautifulSoup(page, "html.parser")
        for canale, continua in zip(soup.find_all("chnum"), soup.select("html body div.container div.header div.chpreviewbox div.singlechprevbox div.thumbprevbox table tbody tr td table tbody tr th table tbody tr th.prgpreviewtext a")):
            if canale.text.isnumeric() and canale.text in canali.keys():
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
                if link_trailer != None and re.match(r"(http:|https:|)\/\/www\.youtube\.com\/.*", link_trailer['src']):
                    src = link_trailer['src']
                    src = src if src.startswith("https:") else "https:" + src
                    output["highlights"][canale]["trailer"] = src

                # get channel name
                output["highlights"][canale]["channel"] = canali[str(canale)]

                # get image
                image = soup2.select_one("html body div.container div.header div.maincolumn div.schedabox img")
                image_url = URL + "/".join(continua["href"].split("/")[:-1]).replace(" ", "") + "/" + image["src"].replace(" ", "")
                backup_images[canale] = image_url
    
    URL = "https://www.superguidatv.it"

    response = requests.get(URL + "/serata/").text
    soup = BeautifulSoup(response, 'html.parser')

    for canale, item in zip(
        soup.select(".sgtvfullevening_divContent:has(.sgtvfullevening_divProgram:nth-of-type(3) .sgtvfullevening_eventLink) > .sgtvfullevening_divProgram:nth-of-type(1) .sgtvfullevening_spanFullPlan > div > span:first-of-type"),
        soup.select('.sgtvfullevening_divContent > .sgtvfullevening_divProgram:nth-of-type(3) .sgtvfullevening_eventLink')
    ):
        canale = canale.text.split(' ')[1]
        if canale in canali.keys():
            href = item['href']
            
            r = requests.get(href)
            s = BeautifulSoup(r.text, 'html.parser')
            try:
                image = s.select_one('.sgtvdetails_cover')['src']
                if image == "":
                    image = s.select_one('.sgtvdetails_imgBackdrop')['src']
                image = image if image.startswith("https://") else URL + image
                if "cover-placeholder.png" in image:
                    raise Exception("No image")
                image_url = image.split("?")[0] + "?width=480"
                response_image = requests.get(image_url, stream=True).content
                with open(f'{DIR}/data/images/{canale}.jpg', 'wb') as f:
                    f.write(response_image)
            except:
                try:
                    response_image = requests.get(backup_images[int(canale)], stream=True).content
                    with open(f'{DIR}/data/images/{canale}.jpg', 'wb') as f:
                        f.write(response_image)
                except:
                    print(f"Error downloading image for {canale}")
            

                

    output["highlights"] = dict(sorted(output["highlights"].items()))

    output_file = open(f"{DIR}/data/stasera.json", "w")
    output_file.write(json.dumps(output))
    output_file.close()

if __name__ == "__main__":
    main()
