import requests, os, re, csv
from bs4 import BeautifulSoup
from os import path, listdir
from os.path import isfile, join
from zipfile import ZipFile
import numpy as np
import datetime, gzip, pickle



class DataDownloader:

    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pkl.gz", 
    regions = { 
        'PHA': '00', 
        'STC': '01', 
        'JHC': '02',
        'PLK': '03',
        'ULK': '04',
        'HKK': '05',
        'JHM': '06',
        'MSK': '07',
        'OLK': '14',
        'ZLK': '15',
        'VYS': '16',
        'PAK': '17',
        'LBK': '18',
        'KVK': '19' }):

        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename
        self.regions = regions
        self.data_files = []
        self.cache = {}
        self.col_list = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a", "p13b", "p13c", "p14", "p15", 
                        "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28", "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", 
                        "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a", "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", 
                        "n", "o", "p", "q", "r", "s", "t", "p5a", 'region']

        if not path.isdir(self.folder):
            try:
                os.mkdir(folder)
            except OSError:
                print ("Creation of the directory %s failed" % path)

    def download_data(self):
        cookies = {
            '_ranaCid': '207473589.1568325762',
            '_ga': 'GA1.2.789520775.1568325762',
            '_fbp': 'fb.1.1601117742080.263834980',
            '_gcl_au': '1.1.1395316238.1603826617',
            '_gid': 'GA1.2.1350174918.1604404951',
        }

        headers = {
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Referer': 'https://ehw.fit.vutbr.cz/izv/',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        #request sites html and parsing all available links with zip data files
        response = requests.get(self.url, headers=headers, cookies=cookies)
        soup = BeautifulSoup(response.text, 'html.parser')
        files = [a['href'] for a in soup.find_all("a", class_="btn-primary")]
        
        #searching the most recent file for every year
        p = re.compile("([0-9]*).([0-9]*)\.zip")
        past_year = p.search(files[0]).group(2)
        for i, file in enumerate(files):
            result = p.search(file)
            present_year = result.group(2)
            if(int(present_year) != int(past_year) or i == len(files)-1):
                self.data_files.append(past_file)
            past_year = present_year
            past_file = file

        #requesting files and saving them to folder
        for file in self.data_files:
            url = self.url + file
            if not path.isdir(file[:-4]):
                r = requests.get(url, headers=headers, cookies=cookies, stream=True)
                with open(file, 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        fd.write(chunk)            
                with ZipFile(file, 'r') as zip:
                    zip.extractall(file[:-4])
                os.remove(file)
        self.data_files = [f[:-4] for f in self.data_files]


    def parse_region_data(self, region):
        if region in self.regions.keys():
            #find csv files comforming to given region
            csv_files = []
            for root, dirs, files in os.walk(self.folder, topdown = False):
                for name in files:
                    if name[:-4] == self.regions.get(region):
                        csv_files.append(os.path.join(root, name))

            """col_list = ["ID", "Druh komunikace", "Číslo komunikácie", "Dátum", "Čas", "Druh nehody", "Druh srážky vozidel", "Druh pevné překážky", 
                        "Charakter nehody", "Zaviněný nehody", "Alkohol u viníka", "Hlavní príčiny nehody", "Usmrceno", "Těžce zraněno",
                        "Lehce zraněno", "Hmotná škoda", "Druh povrchu vozovky", "Stav povrchu vozovky", "Stav komunikace", "Povětrnostní podmínky", 
                        "Viditelnost", "Rozhledové poměry", "Dělené komunikace", "Situování nehody na komunikaci", "Řízení provozu v době nehody", 
                        "Místní úprava přednosti v jízdě", "Specifická místa a objekty v místě nehody", "Směrové pomery", "Kategorie chodce", "Stav chodce",
                        "Chování chodce", "Situace v místě nehody", "Následky na životech a zdraví chodcu", "Počet zúčastněných vozidel", "Místo doprvní nehody",
                        ""]"""
            d_type= np.dtype([('f1', 'i8'), ('f2', 'i'), ('f3', 'i2'), ('f5', 'datetime64[D]'), ('f6', 'i'), ('f7', 'i2'), ('f8', 'i'), ('f9', 'i'),
                    ('f10', 'i'), ('f11', 'i'), ('f12', 'i2'), ('f13', 'i'), ('f14', 'i4'), ('f15', 'i2'), ('f16', 'i2'), ('f17', 'i2'), ('f18', 'i4'), 
                    ('f19', 'i'), ('f20', 'i'), ('f21', 'i'), ('f22', 'i'), ('f23', 'i'), ('f24', 'i'), ('f25', 'i'), ('f26', 'i'), ('f27', 'i'), 
                    ('f28', 'i'), ('f29', 'i2'), ('f30', 'i'), ('f31', 'i2'), ('f32', 'i2'), ('f33', 'i'), ('f34', 'i'), ('f35', 'i4'), ('f36', 'i2'), 
                    ('f37', 'i'), ('f38', 'i'), ('f39', 'i'), ('f40', 'i'), ('f41', 'i'), ('f42', 'i'), ('f43', 'i'), ('f44', 'i'), ('f45', 'i'),
                    ('f46', 'i'), ('f47', 'd'), ('f48', 'd'), ('f49', 'd'), ('f50', 'd'), ('f51', 'd'), ('f52', 'd'), ('f53', 'U25'), ('f54', 'U25'), 
                    ('f55', 'i'), ('f56', 'U25'), ('f57', 'U10'), ('f58', 'U25'), ('f59', 'd'), ('f60', 'U25'), ('f61', 'U25'), ('f62', 'i8'), ('f63', 'i8'),
                     ('f64', 'U25'), ('f65', 'i'), ('f66', 'U25')])
            #lada: muzes si vytvořit array pro zrovna otevrenej soubor podle poctu radku, a potom ty pole concatenovat funkci np.concatenate
            #hound: nebo to hazet do listu a na konci to pretvorit do array
            #lada: to bude slow
            nplist = []
            #regex for XX, A:/B:.., empty string elimination
            regex = r"^(\w:|\w\w|)$"
            for csv_file in csv_files:
                with open(csv_file,'r', encoding = "windows-1250", newline="") as dest_f:
                    data_iter = csv.reader(dest_f, delimiter = ';', quotechar = '"')
                    #num_of_rows = len(list(data_iter))
                    #num_of_cols = len(self.col_list)
                    #anArray = zeros((ph,pw), dtype='O')
                    dest_f.seek(0)
                    for data in data_iter:
                        a = tuple("-1" if re.match(regex, x) else x.replace(',', '.') for x in data) + (region,)
                        nplist.append(np.asarray(a, dtype=d_type).T)
                    #exit(1)
                    #spocitat kolko ma csv riadkov, alokovat pole a potom vkladat na indexy np.empty()\

            return self.col_list, nplist

    def save_cache(self, region):
        with gzip.open("data/" + self.cache_filename.format(region), 'wb') as f:
            pickle.dump(self.cache.get(region), f, pickle.HIGHEST_PROTOCOL)

    def load_cache(self, region):
        with gzip.open("data/" + self.cache_filename.format(region), 'rb') as f:
            return pickle.load(f)

    def search_cache_file(self, region):
        files_and_directories = os.listdir("data")
        if self.cache_filename.format(region) in files_and_directories:
            return True
        return False

    def get_list(self, regions = None):
        if regions is None:
            regions = self.regions.keys()
        nplist = []
        if(type(regions) == str):
            regions = [regions]
        for region in regions:
            if region in self.cache.keys():
                nplist += self.cache.get(region)
            elif self.search_cache_file(region) is True:
                data = self.load_cache(region)
                nplist += data
                self.cache[region] = data
            elif region in self.regions.keys():
                data = self.parse_region_data(region)
                self.cache[region] = data[1]
                self.save_cache(region)
                nplist += data[1]
                           
        return self.col_list, nplist

downloader = DataDownloader()
data = downloader.parse_region_data('VYS')
if __name__ == "__mainkek__d":
    downloader = DataDownloader()
    #downloader.download_data()
    regions = ["VYS", "PHA", "PLK"]
    region_data = downloader.get_list(regions)
    print("                   COLUMNS")
    print("----------------------------------------------")
    print(str(region_data[0]))
    print("----------------------------------------------\n")
    print("              NUMBER OF RECORDS")
    print("----------------------------------------------")
    print("                   " + str(len(region_data[1])))
    print("----------------------------------------------\n")
    print("           REGIONS IN THIS DATASET")
    print("----------------------------------------------")
    print("           " + str(regions))
    print("----------------------------------------------")
