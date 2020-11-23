import requests
import os
import re
import csv
from bs4 import BeautifulSoup
from os import path, listdir
from os.path import isfile, join
from zipfile import ZipFile
import numpy as np
import datetime
import gzip
import pickle
import io
from io import BytesIO
import time


class DataDownloader:

    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pkl.gz",
                 regions={
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
            'KVK': '19'}):

        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename
        self.regions = regions
        self.data_files = []
        self.cache = {}
        self.zips = []
        self.col_list = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a", "p13b", "p13c", "p14", "p15",
                         "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28", "p34", "p35", "p39", "p44", "p45a", "p47", "p48a",
                         "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a", "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l",
                         "n", "o", "p", "q", "r", "s", "t", "p5a", 'region']

        if not path.isdir(self.folder):
            try:
                os.mkdir(folder)
            except OSError:
                print("Creation of the directory %s failed" % path)

    def save_zip_file(self, filename, response):
        '''Writes the zip data to a file.'''
        with open(filename, 'wb') as fd:
            fd.write(response.content)

    def find_latest_zips(self, files):
        '''Searching the most recent file for every year.'''
        p = re.compile("([0-9]*).([0-9]*)\.zip")
        past_year = p.search(files[0]).group(2)
        for i, file in enumerate(files):
            result = p.search(file)
            present_year = result.group(2)
            if(int(present_year) != int(past_year)):
                self.data_files.append(past_file)
            if(i == len(files)-1):
                self.data_files.append(file)
            past_year = present_year
            past_file = file

    def download_data(self):
        '''Downloads all latest zip files or loads data from data folder.'''
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

        # request sites html and parsing all available links with zip data files
        response = requests.get(self.url, headers=headers, cookies=cookies)
        soup = BeautifulSoup(response.text, 'html.parser')
        files = [a['href'] for a in soup.find_all("a", class_="btn-primary")]
        self.find_latest_zips(files)

        # requesting files and saving them to folder, if already saved, just load them
        for file in self.data_files:
            url = self.url + file
            if not path.isfile(file):
                r = requests.get(url, headers=headers,
                                 cookies=cookies, stream=True)
                self.save_zip_file(file, r)
                zipfile = ZipFile(BytesIO(r.content))
                self.zips.append(zipfile)
            else:
                zipfile = ZipFile(file, 'r')
                self.zips.append(zipfile)

    def parse_region_data(self, region):
        '''Parses csv files, converts rows in csv to ndarray with correct datatypes, return column names and list of aforementioned ndarrays.'''
        if region in self.regions.keys():
            # in case the data is not downloaded or loaded
            if(not self.zips):
                self.download_data()
            # datatype for given columns in csv files
            d_type = np.dtype([('f1', 'i8'), ('f2', 'i'), ('f3', 'i2'), ('f5', 'datetime64[D]'), ('f6', 'i'), ('f7', 'i2'), ('f8', 'i'), ('f9', 'i'),
                               ('f10', 'i'), ('f11', 'i'), ('f12', 'i2'), ('f13', 'i'), ('f14',
                                                                                         'i4'), ('f15', 'i2'), ('f16', 'i2'), ('f17', 'i2'), ('f18', 'i4'),
                               ('f19', 'i'), ('f20', 'i'), ('f21', 'i'), ('f22', 'i'), ('f23',
                                                                                        'i'), ('f24', 'i'), ('f25', 'i'), ('f26', 'i'), ('f27', 'i'),
                               ('f28', 'i'), ('f29', 'i2'), ('f30', 'i'), ('f31', 'i2'), ('f32',
                                                                                          'i2'), ('f33', 'i'), ('f34', 'i'), ('f35', 'i4'), ('f36', 'i2'),
                               ('f37', 'i'), ('f38', 'i'), ('f39', 'i'), ('f40', 'i'), ('f41',
                                                                                        'i'), ('f42', 'i'), ('f43', 'i'), ('f44', 'i'), ('f45', 'i'),
                               ('f46', 'i'), ('f47', 'd'), ('f48', 'd'), ('f49', 'd'), ('f50',
                                                                                        'd'), ('f51', 'd'), ('f52', 'd'), ('f53', 'U25'), ('f54', 'U25'),
                               ('f55', 'i'), ('f56', 'U25'), ('f57', 'U10'), ('f58', 'U25'), ('f59',
                                                                                              'd'), ('f60', 'U25'), ('f61', 'U25'), ('f62', 'i8'), ('f63', 'i8'),
                               ('f64', 'U25'), ('f65', 'i'), ('f66', 'U25')])

            nplist = []
            # regex for XX, A:/B:.., empty string elimination
            regex = r"^(\w:|\w\w|)$"
            # processes rows in csv files to ndarrays with appropriate datatypes
            for z in self.zips:
                for name in z.namelist():
                    if name[:-4] == self.regions.get(region):
                        content = io.TextIOWrapper(
                            z.open(name), encoding='windows-1250', newline='')
                        data_iter = csv.reader(
                            content, delimiter=';', quotechar='"')
                        for data in data_iter:
                            a = tuple(
                                "-1" if re.match(regex, x) else x.replace(',', '.') for x in data) + (region,)
                            nplist.append(np.asarray(a, dtype=d_type))
            return self.col_list, nplist

    def save_cache(self, region):
        '''Save cache locally.'''
        with gzip.open("data/" + self.cache_filename.format(region), 'wb') as f:
            pickle.dump(self.cache.get(region), f, pickle.HIGHEST_PROTOCOL)

    def load_cache(self, region):
        '''Load cache from local storage.'''
        with gzip.open("data/" + self.cache_filename.format(region), 'rb') as f:
            try:
                while f.read(1024 * 1024):
                    pass
            except:
                print("Corrupted cache gzip file!")
                exit(1)
            f.seek(0)
            return pickle.load(f)

    def search_cache_file(self, region):
        '''Looks for cache file in data folder'''
        files_and_directories = os.listdir("data")
        if self.cache_filename.format(region) in files_and_directories:
            return True
        return False

    def get_list(self, regions=None):
        '''processes all specified regions '''
        if regions is None:
            regions = self.regions.keys()
        nplist = []
        # in case only one region was passed as a string
        if(type(regions) == str):
            regions = [regions]
        # loads data from cache or asks for missing data from parse_region_data
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


if __name__ == "__main__":
    downloader = DataDownloader()
    downloader.download_data()
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
