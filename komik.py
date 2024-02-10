from PIL import Image
import requests as r
import os
from bs4 import BeautifulSoup
import img2pdf
import threading
from urllib.parse import urlparse

class Kiryuu:
    def __init__(self):
        self.api = r.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }

    def download(self, url, save):
        resp = self.api.get(url, headers=self.headers)
        if resp.status_code == 200:
            with open(save, 'wb') as file:
                file.write(resp.content)
        else:
            print(' [!] Failed')

    def single(self, urlmanga):
        resp = self.api.get(urlmanga, headers=self.headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        reader_area = soup.find('div', id='readerarea')
        if reader_area:
            imgs = reader_area.find_all('img')
            manga_name = self.extract_manga_name(urlmanga)  
            manga_dir = os.path.join('KiryuuCH', manga_name)
            os.makedirs(manga_dir, exist_ok=True)
            img_paths = []
            for img in imgs:
                img_url = img.get('src')
                img_name = os.path.basename(img_url)
                save = os.path.join(manga_dir, img_name)
                self.download(img_url, save)
                img_paths.append(save)
            pdf_file = os.path.join(manga_dir, f'{manga_name}.pdf')  
            self.convert_to_pdf(img_paths, pdf_file)
            print(' [!] Downloaded')
        else:
            print(' Invalid Area')

    def massdownload(self, linkmanga):
        resp = self.api.get(linkmanga, headers=self.headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        chapterlist = soup.find("div", class_="eplister")
        if chapterlist:
            chapters = chapterlist.find_all("div", class_="chbox")
            for i, chapter in enumerate(chapters, 1):
                eph_num = chapter.find("div", class_="eph-num")
                if eph_num:
                    chapter_link = eph_num.find("a")["href"]
                    print(f' [+] {chapter_link}')
                    self.singledua(chapter_link, i)

    def singledua(self, churl, chapter_number):  
        resp = self.api.get(churl, headers=self.headers)  
        soup = BeautifulSoup(resp.text, 'html.parser')
        reader_area = soup.find('div', id='readerarea')
        if reader_area:
            imgs = reader_area.find_all('img')
            manga_name = self.extract_manga_name(churl)  
            manga_dir = os.path.join('KiryuuCH', manga_name)
            os.makedirs(manga_dir, exist_ok=True)
            img_paths = []
            for img in imgs:
                img_url = img.get('src')
                img_name = os.path.basename(img_url)
                save = os.path.join(manga_dir, f'Chapter_{chapter_number}_{img_name}')
                self.download(img_url, save)
                self.remove_alpha_channel(save) 
                img_paths.append(save)
            pdf_file = os.path.join(manga_dir, f'{manga_name}.pdf') 
            self.convert_to_pdf(img_paths, pdf_file)
            print(f' [!] Chapter {manga_name} Downloaded')
        else:
            print(' Invalid Area')

    def remove_alpha_channel(self, img_path):
        image = Image.open(img_path)
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            image = image.convert("RGB")
            image.save(img_path)

    def convert_to_pdf(self, img_paths, pdf_file):
        if img_paths:
            with open(pdf_file, "wb") as f:
                f.write(img2pdf.convert(img_paths, verbosity=0, rotation=img2pdf.Rotation.ifvalid))
                print(f" [!] PDF '{pdf_file}' Generated")
        else:
            print(" [!] No images to convert")

    def extract_manga_name(self, url):
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        if path_parts[-1] == '':
            return path_parts[-2]
        else:
            return path_parts[-1]

if __name__ == "__main__":
    bot = Kiryuu()
    os.system('cls')
    choice = input(' 1. Single Download \n 2. Mass Download \n Pilihan: ')
    if choice == '1':
        urlmanga = input(' \n[!] Masukan Url: ')
        if urlmanga:
            bot.single(urlmanga)
        else:
            print(' [!] Mohon Masukan Link!')
    elif choice == '2':
        linkmanga = input(' [!] Link Manga: ')
        if linkmanga:
            bot.massdownload(linkmanga)
        else:
            print(' Masukan Link')
