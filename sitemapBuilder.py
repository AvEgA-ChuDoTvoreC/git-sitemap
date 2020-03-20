#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Import external library dependencies

import time
import datetime

import argparse
import textwrap
import sys
import os

import subprocess
from subprocess import Popen, PIPE

import requests
from requests.exceptions import MissingSchema
from urllib3.exceptions import MaxRetryError, NewConnectionError
from urllib3.connection import VerifiedHTTPSConnection
from requests.exceptions import ConnectionError
import socket

from bs4 import BeautifulSoup
import re
import threading
import multiprocessing

import xml.etree.cElementTree as ET

import pandas as pd
import graphviz
import matplotlib

"""
User-Agent: Mozilla/<version> (<system-information>) <platform> (<platform-details>) <extensions>
"""
User_Agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; MSOffice 12)'
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; MSOffice 12)'
encoding = 'UTF-8'

# Mulitprocess/Threading time test
time0 = ''
time1 = ''
timetime = ''


def run_command(cmd, echo=True, exit_on_error=False):
    """Communication to bash frow terminal using subprocess"""
    p = Popen(cmd, stdout=subprocess.PIPE, stderr=PIPE, shell=True, universal_newlines=True)
    o, e = p.communicate()
    return p.returncode, o, e


class UserError(Exception):
    """класс исключений UserError"""
    pass


class Sitemap:
    """
    Class that helps to create sitemaps of any site...
    about ..."Any Site"... still working around it :P
    """
    def __init__(self):
        super(Sitemap, self).__init__()
        self.checked_links = list()                     # the final links list of each thread work
        self.new_links = list()                         # list with new links that appends to checked_links
        self.site_link = f'https://{args.domain}/'
        self.site_link_nos = f'http://{args.domain}/'
        self.workers_count = args.workers               # number of threads: depends on number of 1st level folders
        self.thread_links = list()                      # 1st level links that we need for threads to run on
        self.thread_name = ''                           # name of the link from thread_links

        self.checked_links_almost = []                  # intermediate list
        self.checked_links_end = []                     # the final list of all checked_links from each thread
        self.extra_links = []                           # not used list
        self.temp_func_list = []                        # intermediate list

    def request_session(self):
        """
        Establishing session with domain
        есть особенность пока мне не понятная, при использовании session.post:
        количество ссылок на том же сайте сокращается и процесс переходов проходит
        в разы быстрее чем при использовании прямых request запросов с 520+ до 270+
        и вместо получасовой обработки 3 минутная, и как + при этом не теряется возможность
        передавать данные юзерагента и соответсвенно возможность обхода антибот систем на сайте
        (данная функция будет реализована позже)
        """
        s = requests.Session()
        s.headers.update({
            'Referer': f'{args.domain}',
            'User-Agent': f'{User_Agent}'
        })
        s.encoding = f'{encoding}'

        return s

    def start(self, session):
        """
        Start program function

        :param session:
        :return: req.text
        """
        req = session.post('https://' + f'{args.domain}')
        time.sleep(2)

        return req.text

    def request(self, url, session):
        """
        Get request from site url or (args.domain)

        :param url:
        :param session:
        :return: session request with headers
        """
        req = session.post(f'{url}')

        return req

    def worker(self, thread_name, checked_links, qq):
        """
        Worker gonna do his job - make requests in thread!

        :param thread_name:
        :param checked_links:
        :param qq: the way I find to to put extra worker(thread)
        :return: self.checked_links
        """
        # thread name https://vistgroup.ru/company/
        if (qq + 1) == self.workers_count:
            thth = threading.Thread(target=self.crawling_1st_page_other_links,
                                    args=(0, 0, self.thread_links, self.checked_links))
            thth.start()
        if (qq + 1) != self.workers_count:
            th = threading.Thread(target=self.crawling_web_pages, args=(0, 3, thread_name, checked_links))
            th.start()

        return self.checked_links

    def worker_threading_domains(self, link, link_session):
        """
        ЗАГОТОВКА: СОЗДАНИЕ ПОТОКОВОЙ ОБРАБОТКИ НЕСКОЛЬКИХ ДОМЕНОВ ОДНОВРЕМЕННО

        :param link: he get link from        -checked_links
        :param link_session: use instrument  -session (with headers)
        :return:
        """
        # th = threading.Thread(target=self.crawling_web_pages, args=(control, arg2))
        # th.start()
        # print('\n\nBreak worker\n\n')
        pass

    def extra_worker(self):
        # thread_links = self.thread_links
        # checked_links = self.checked_links
        #
        # thth = threading.Thread(target=self.crawling_web_pages, args=(0, 3, thread_links, checked_links))
        # thth.start()
        # thth.join()
        pass

    def thread_activator(self):
        """
        Run Threads depending on number of workers
        """
        # ОБРАБОТКА: ПОЛУЧАЕМ СПИСКИ SELF.CHECKED_LINKS, SELF.THREAD_LINKS УРОВНЯ 1
        self.start_crawling()

        # the way I found to put extra thread worker and further arg for func() that'll get links from robots.txt
        self.thread_links.append(f'https://{args.domain}/robot.txt')

        # here we can put code to increase number of workers from args.worker
        self.workers_count = len(self.thread_links)
        print('Workers number =', self.workers_count)

        # ОБРАБОТКА: ЗАПУСК ПОТОКОВОЙ ОБРАБОТКИ. РАЗБИВАЕМ НА ПОТОКИ КАЖДЫЙ ЛИНК ПЕРВОГО УРОВНЯ
        # here we have absolute thread name https://vistgroup.ru/company/
        cmd = '-p'
        site_dir = f'{oo}/Sitemaps/{args.domain}'
        run_command(f'mkdir {cmd} ' + f'{site_dir}', echo=False)
        # don't find out the other good way to take args from thread so I gonna write args to text files with echo
        run_command(f'touch ' + f'{site_dir}/links_from_thread.txt', echo=False)
        run_command(f'touch ' + f'{site_dir}/extra_thread.txt', echo=False)

        # process list with workers
        workers_list = [multiprocessing.Process(target=self.worker,
                                                args=(self.thread_links[i], [self.thread_links[i]], i))
                        for i in range(self.workers_count)]
        for w in workers_list:
            w.start()
        for w in workers_list:
            w.join()

        # ВРЕМЕННОЕ РЕШЕНИЕ В ВИДУ ТОГО, ЧТО НЕ РАЗОБРАЛСЯ КАК ДОСТАВАТЬ ДАННЫЕ ИЗ ПОТОКА, ВОЗМОЖНО СТОИТ
        # РАССМОТРЕТЬ СОПРОГРАММЫ ИЛИ ПЕРЕДЕЛАТЬ С ИСПОЛЬЗОВАНИЕМ АСИНХРОННОГО ПРОГРАММИРОВАНИЯ
        # СОХРЯНЕМ ВО ВРЕМЕННЫЙ ФАИЛ.TXT ССЫЛКИ ИЗ ПОТОКА ДАЛЕЕ УДАЛЯЕМ ЕГО ЗАПИСАВ В ПЕРЕМЕННУЮ ПЕРЕД ЭТИМ
        # echo write args from threads to file.txt
        with open(f'{oo}/Sitemaps/{args.domain}/links_from_thread.txt', 'r') as f:
            a = f.read()
            self.checked_links_almost = a.split('\n')
        for links in self.checked_links_almost:
            if links is not None and links != '':
                self.checked_links_end.append(links)

        with open(f'{oo}/Sitemaps/{args.domain}/extra_thread.txt', 'r') as f:
            b = f.read()
            self.temp_func_list = a.split('\n')
        for linkss in self.temp_func_list:
            if linkss is not None and linkss != '' and linkss not in self.checked_links_end:
                self.checked_links_end.append(linkss)
        # remove temp .txt files
        run_command(f'rm {oo}/Sitemaps/{args.domain}/inks_from_thread.txt')
        run_command(f'rm {oo}/Sitemaps/{args.domain}/extra_thread.txt')

    def start_crawling(self):
        """
        Start crawling function() - активируем "ползать" по страничкам

        :return: self.checked_links, self.thread_links
        """
        print('https://' + f'{args.domain}')
        print('Crawling...')
        time.sleep(3)
        self.checked_links.append(f'https://{args.domain}/')

        # crawl 1st page to find folders and then append em to thread_links list
        self.crawling_1st_page(control=0, count_try=0, thread_links=[], checked_links=self.checked_links)

        # ЗАГОТОВКА: СОЗДАНИЕ ПОТОКОВОЙ ОБРАБОТКИ НЕСКОЛЬКИХ ДОМЕНОВ ОДНОВРЕМЕННО
        # control = 0
        # arg2 = 22
        # workers_count = 3
        # workers_list = [multiprocessing.Process(target=self.worker,
        #                                         args=(control, arg2))
        #                 for _ in range(workers_count)]
        # for w in workers_list:
        #     w.start()
        # for w in workers_list:
        #     w.join()
        return self.checked_links, self.thread_links

    # ex: checked_links = [ 'https://vistgroup.ru/', 'https://vistgroup.ru/company/about/', ... ]
    def crawling_web_pages(self, control, count_try, thread_name, checked_links):
        """
        Web scraping is ON. Выскабливаем линки с сайта
        Check main page links then -> Check all found out links

        :return: list: checked_links [link1, link2, ...]
        """
        self.checked_links = checked_links

        while control < len(self.checked_links):

            try:
                # ОБРАБОТКА: РАЗБИВАЕМ КАЖДЫЙ ЛИНК ЧЕРЕЗ .SPLIT('/') И ОТДЕЛЬНО ПРОВЕРИМ КАЖДУЮ ПАПКУ 1 УРОВНЯ
                # ДОБАВЛЯЯ ЭЛЕМ => /EN/SOLUTIONS/EXTRA/SOMETHING1/SOMETHING2/ -> /EN/ -> /EN/SOLUTIONS ->
                # /EN/SOLUTIONS/EXTRA/ -> ... ЦЕЛЬ - РАЗБИТЬ НА ПОТОКИ КАЖДЫЙ ЛИНК 1 УРОВНЯ

                # ПЕРЕНОШУ ЭТУ ОБРАБОТКУ В ОТДЕЛЬНЫЙ ПОТОК КОТОРЫЙ БУДЕТ ИСКАТЬ МНЕ ДОПОЛНИТЕЛЬНЫЕ THREAD_LINKS
                # В ФУНЦИИ crawling_1st_page_other_links ПОКА СЛОЖНО УСЛОЖНЯТЬ И БЕЗ ТОГО СЛОЖНУЮ ОБРАБОТКУ :P
                count_try += 1
                if count_try == 2:
                    for link in self.checked_links:
                        k = link.split('/')[3]
                        if k not in self.thread_links and k != "" and "mailto" not in k and "tel" not in k:
                            self.thread_links.append(k)
                    # ['company', 'solutions', 'media', 'contacts', 'en', 'es', 'fr', 'local', 'bitrix', 'upload']
                    cc = 0
                    while cc < len(self.thread_links):
                        for name in self.thread_links:
                            self.thread_links[cc] = f'https://{args.domain}/{name}/'
                            cc += 1
                # ['https://vistgroup.ru/company/', 'https://vistgroup.ru/solutions/', 'https://vistgroup.ru/media/']
                if count_try == 2:
                    break

                # ОБРАБОТКА: ПОИСК ССЫЛОК ТИПА /captcha2.php?captcha_sid=02529b019fa5ecfb5b45a1d38e04308e
                # /vg-underground_C2_A0v2_C2_A0FR.png И ИГНОР ИХ В ДАЛЬНЕЙШЕМ А ТАКЖЕ:  /*.PDF
                dot_in_the_endlink = 'None'
                search_links = re.search(
                    '/[-;:+%"!@^±§&<>#_=?.a-zA-Z0-9]{2,100}[.]{1,100}[-;:+%"!@^±§&<>#_=?.a-zA-Z0-9]{2,100}$',
                    self.checked_links[control])
                if search_links is not None:
                    dot_in_the_endlink = search_links.group()
                elif not self.checked_links[control].endswith(dot_in_the_endlink):

                    # try:
                    responses = self.request(self.checked_links[control], self.request_session())
                    source_code = responses.text
                    # except MissingSchema as err:
                    #     raise UserError(err)

                    # ОБРАБОТКА: ПОИСК DATA_HREF И SRC
                    soup = BeautifulSoup(source_code, "html.parser")
                    new_links = [w['href'] for w in soup.findAll('a', href=True)]  # get all links from that page
                    data_href = [a.get('data-href') for a in soup.findAll()]  # get "replace" links such as /en, /fr
                    src = [aa.get('src') for aa in soup.findAll()]

                    # ОБРАБОТКА: DATA_HREF И SRC В СПИСОК -> NEW_LINKS
                    for data_h in data_href:
                        if data_h is not None:
                            new_links.append(data_h)  # add "replace" links to new_links (/en, /fr ...)
                    for d_src in src:
                        if d_src is not None:
                            new_links.append(d_src)
                    c = 0
                    while c < len(new_links):
                        for k in new_links:
                            if not k.endswith('/') and not k.startswith('http') and '.' not in k:
                                new_links[c] += '/'
                            c += 1

                    # ОБРАБОТКА: ПОИСК ФАЙЛА ROBOTS.TXT И SITEMAP.XML ДЛЯ ДОБАВЛЕНИЯ ССЫЛОК, В ПРОЦЕССЕ
                    # thread_activator() str ±174

                    # ОБРАБОТКА: НОВЫЕ ССЫЛКИ В СЛОВАРЬ -> NEW_LINKS
                    counter = 0
                    while counter < len(new_links):
                        # this code is for thouse relative links witch starts with / slash
                        if "http" not in new_links[counter]:  # checking if the linking on this site is absolute or
                            # relative starts with http or /
                            verify = new_links[counter][0]

                            # getting first character of every link & if it starts with slash / then
                            # we remove this / slash because we have already added the slash at the end of the domain
                            if verify == '/':
                                new_links[counter] = new_links[counter][:1].replace('/', '') + new_links[counter][1:]
                                # this will remove only first slash in the link  /string  not every slash

                                # join these relative links with domain to make them absolute links
                                # treatment for thread links -> thread_name == thread_links[i]
                                pof = thread_name.split('/')[3]
                                if pof in new_links[counter]:
                                    new_links[counter] = thread_name + new_links[counter].replace(f'{pof}/', '')
                                    # joining thread name with relative links
                                    counter = counter + 1
                                else:
                                    counter = counter + 1
                                    self.extra_links.append(new_links[counter])
                            else:
                                # this code is for thouse relative links witch doesn't starts with / slash
                                new_links[counter] = self.site_link + new_links[counter]
                                counter = counter + 1
                        else:
                            counter = counter + 1
                    else:
                        counter2 = 0
                        while counter2 < len(new_links):
                            # here we can apply any filter so if the contain any of these strings then
                            # don't append this link into the final array where we are collecting /
                            # appending all the links found in that website
                            if "#" not in new_links[counter2] and "mailto" not in new_links[counter2] and \
                                    ".jpg" not in new_links[counter2] and new_links[counter2] not in self.checked_links \
                                    and self.site_link in new_links[counter2]:
                                # new_links[counter2] not in self.checked_links:- this condition i very important, this
                                # will never append a link in the array which already exist in the array...without this
                                # condition this script will never end and start appending the same site / link again:

                                # last condition of script will add only the links in the array which have the domain
                                # and will never append the links which redirect to another websites (many website have
                                # links to youtube facebook etc)
                                self.checked_links.append(new_links[counter2])
                                os.system('clear')
                                print(str(control) + '/' + str(len(self.checked_links)))
                                print('')
                                print(str(control) + ' Web Pages Crawler & ' + str(
                                    len(self.checked_links)) + " Web Pages Found")
                                print('')
                                print(new_links[counter2])  # display the current site_link
                                counter2 = counter2 + 1
                            else:
                                counter2 = counter2 + 1
                        else:
                            os.system('clear')
                            print(str(control) + '/' + str(len(self.checked_links)))
                            print('')
                            print(str(control) + ' Web Pages Crawler & ' + str(
                                len(self.checked_links)) + " Web Pages Found")
                            print('')
                            print(self.checked_links[control])  # display the current site_link
                            control = control + 1
                else:
                    control = control + 1

            except UserError:
                continue
            else:
                control = control + 1
        else:
            time.sleep(0.1)
            text_links = ''
            with open(f'{oo}/Sitemaps/{args.domain}/links_from_thread.txt', 'r') as f:
                for line in self.checked_links:
                    text_links += (line + '\n')
                    if line not in f:
                        run_command(f'echo "{text_links}" >> {oo}/Sitemaps/{args.domain}/links_from_thread.txt',
                                    echo=False)
            time.sleep(0.1)

        return self.checked_links, self.extra_links

    # ex: checked_links = [ 'https://vistgroup.ru/' ]
    def crawling_1st_page(self, control, count_try, thread_links, checked_links):
        """
        We start with this crawling_1st_page() -> crawling_web_pages() + crawling_1st_page_other_links() as extra worker
        Web scraping is ON. Выскабливаем линки с сайта
        Check main page links then -> Check all found out links

        :return: list: checked_links [link1, link2, ...]
        """
        self.thread_links = thread_links
        self.checked_links = checked_links

        while control < len(self.checked_links):

            try:
                # ОБРАБОТКА: РАЗБИВАЕМ КАЖДЫЙ ЛИНК ЧЕРЕЗ .SPLIT('/') И ОТДЕЛЬНО ПРОВЕРИМ КАЖДУЮ ПАПКУ 1 УРОВНЯ
                # ДОБАВЛЯЯ ЭЛЕМ => /EN/SOLUTIONS/EXTRA/SOMETHING1/SOMETHING2/ -> /EN/ -> /EN/SOLUTIONS ->
                # /EN/SOLUTIONS/EXTRA/ -> ... ЦЕЛЬ - РАЗБИТЬ НА ПОТОКИ КАЖДЫЙ ЛИНК 1 УРОВНЯ
                count_try += 1
                print(f'КОЛИЧЕСТВО TRY {count_try}')
                if count_try == 2:
                    for link in self.checked_links:
                        k = link.split('/')[3]
                        if k not in self.thread_links and k != "" and "mailto" not in k and "tel" not in k:
                            self.thread_links.append(k)
                    # ['company', 'solutions', 'media', 'contacts', 'en', 'es', 'fr', 'local', 'bitrix', 'upload']
                    cc = 0
                    while cc < len(self.thread_links):
                        for name in self.thread_links:
                            self.thread_links[cc] = f'https://{args.domain}/{name}/'
                            cc += 1
                # ['https://vistgroup.ru/company/', 'https://vistgroup.ru/solutions/', 'https://vistgroup.ru/media/']

                if count_try == 2:
                    break

                # ОБРАБОТКА: ПОИСК ССЫЛОК ТИПА /captcha2.php?captcha_sid=02529b019fa5ecfb5b45a1d38e04308e
                # /vg-underground_C2_A0v2_C2_A0FR.png И ИГНОР ИХ В ДАЛЬНЕЙШЕМ   /*.PDF
                dot_in_the_endlink = 'None'
                search_links = re.search(
                    '/[-;:+%"!@^±§&<>#_=?.a-zA-Z0-9]{2,100}[.]{1,100}[-;:+%"!@^±§&<>#_=?.a-zA-Z0-9]{2,100}$',
                    self.checked_links[control])
                if search_links is not None:
                    dot_in_the_endlink = search_links.group()
                elif not self.checked_links[control].endswith(dot_in_the_endlink):

                    responses = self.request(self.checked_links[control], self.request_session())
                    source_code = responses.text

                    # ОБРАБОТКА: ПОИСК DATA_HREF И SRC
                    soup = BeautifulSoup(source_code, "html.parser")
                    new_links = [w['href'] for w in soup.findAll('a', href=True)]  # get all links from that page
                    data_href = [a.get('data-href') for a in soup.findAll()]  # get "replace" links such as /en, /fr
                    src = [aa.get('src') for aa in soup.findAll()]

                    # ОБРАБОТКА: DATA_HREF И SRC В СЛОВАРЬ -> NEW_LINKS
                    for data_h in data_href:
                        if data_h is not None:
                            new_links.append(data_h)  # add "replace" links to new_links
                    for d_src in src:
                        if d_src is not None:
                            new_links.append(d_src)
                    c = 0
                    while c < len(new_links):
                        for k in new_links:
                            if not k.endswith('/') and not k.startswith('http') and '.' not in k:
                                new_links[c] += '/'
                            c += 1

                    # ОБРАБОТКА: ПОИСК ФАЙЛА ROBOTS.TXT И SITEMAP.XML ДЛЯ ДОБАВЛЕНИЯ ССЫЛОК,

                    # ОБРАБОТКА: НОВЫЕ ССЫЛКИ В СЛОВАРЬ -> NEW_LINKS
                    counter = 0
                    while counter < len(new_links):
                        # this code is for thouse relative links witch starts with / slash
                        if "http" not in new_links[counter]:  # checking if the linking on this site is absolute or
                            # relative starts with http or /
                            verify = new_links[counter][0]

                            # getting first character of every link & if it starts with slash / then
                            # we remove this / slash because we have already added the slash at the end of the domain
                            if verify == '/':
                                new_links[counter] = new_links[counter][:1].replace('/', '') + new_links[counter][1:]
                                # this will remove only first slash in the link  /string  not every slash

                                # join these relative links with domain to make them absolute links
                                new_links[counter] = self.site_link + new_links[counter]
                                # joining domain with relative links
                                counter = counter + 1
                            else:
                                # this code is for thouse relative links witch doesn't starts with / slash
                                new_links[counter] = self.site_link + new_links[counter]
                                counter = counter + 1
                        else:
                            counter = counter + 1
                    else:
                        counter2 = 0
                        while counter2 < len(new_links):
                            # here we can apply any filter so if the contain any of these strings then
                            # dont append this link into the final array where we are collecting /
                            # appending all the links found in that website
                            if "#" not in new_links[counter2] and "mailto" not in new_links[counter2] and \
                                    ".jpg" not in new_links[counter2] and new_links[counter2] not in self.checked_links \
                                    and self.site_link in new_links[counter2]:
                                # new_links[counter2] not in self.checked_links:- this condition i very important, this
                                # will never append a link in the array which already exist in the array...without this
                                # condition this script will never end and start appending the same site / link again:

                                # last condition of script will add only the links in the array which have the domain
                                # and will never append the links which redirect to another websites (many website have
                                # links to youtube facebook etc)
                                self.checked_links.append(new_links[counter2])
                                os.system('clear')
                                print(str(control) + '/' + str(len(self.checked_links)))
                                print('')
                                print(str(control) + ' Web Pages Crawler & ' + str(
                                    len(self.checked_links)) + " Web Pages Found")
                                print('')
                                # print(f'{os.getpid()}')
                                print(new_links[counter2])  # display the current site_link
                                counter2 = counter2 + 1
                            else:
                                counter2 = counter2 + 1
                        else:
                            os.system('clear')
                            print(str(control) + '/' + str(len(self.checked_links)))
                            print('')
                            print(str(control) + ' Web Pages Crawler & ' + str(
                                len(self.checked_links)) + " Web Pages Found")
                            print('')
                            print(self.checked_links[control])  # display the current site_link
                            control = control + 1
                else:
                    control = control + 1

            except UserError:
                continue
            else:
                control = control + 1

        else:
            time.sleep(2)

        print('End links from 1st page crawl =\n', self.checked_links)
        return self.checked_links, self.thread_links

    def crawling_1st_page_other_links(self, control, count_try, thread_links, checked_links):
        """
        Эта функция сделана только для того чтобы обработать ссылки, которые не вошли в thread_links
        в дальнейшем будет доработана в функции crawling_1st_page()
        временное решение, пока пришлось ctrl+c -> ctrl+p  x3
        """
        self.thread_links = thread_links
        self.checked_links = checked_links
        print('\nEXTRA WORKER START HIS JOB\n')

        while control < len(self.checked_links):
            try:
                count_try += 1
                if count_try == 2:
                    for link in self.checked_links:
                        k = link.split('/')[3]
                        if k not in self.thread_links and k != "" and "mailto" not in k and "tel" not in k:
                            self.thread_links.append(k)

                    cc = 0
                    while cc < len(self.thread_links):
                        for name in self.thread_links:
                            self.thread_links[cc] = f'https://{args.domain}/{name}/'
                            cc += 1

                dot_in_the_endlink = 'None'
                search_links = re.search(
                    '/[-;:+%"!@^±§&<>#_=?.a-zA-Z0-9]{2,100}[.]{1,100}[-;:+%"!@^±§&<>#_=?.a-zA-Z0-9]{2,100}$',
                    self.checked_links[control])
                if search_links is not None:
                    dot_in_the_endlink = search_links.group()
                elif not self.checked_links[control].endswith(dot_in_the_endlink) and \
                        self.checked_links[control] not in self.thread_links:

                    responses = self.request(self.checked_links[control], self.request_session())
                    source_code = responses.text

                    soup = BeautifulSoup(source_code, "html.parser")
                    new_links = [w['href'] for w in soup.findAll('a', href=True)]
                    data_href = [a.get('data-href') for a in soup.findAll()]
                    src = [aa.get('src') for aa in soup.findAll()]

                    for data_h in data_href:
                        if data_h is not None:
                            new_links.append(data_h)
                    for d_src in src:
                        if d_src is not None:
                            new_links.append(d_src)
                    c = 0
                    while c < len(new_links):
                        for k in new_links:
                            if not k.endswith('/') and not k.startswith('http') and '.' not in k:
                                new_links[c] += '/'
                            c += 1

                    counter = 0
                    while counter < len(new_links):
                        if "http" not in new_links[counter]:
                            verify = new_links[counter][0]
                            if verify == '/':
                                new_links[counter] = new_links[counter][:1].replace('/', '') + new_links[counter][1:]
                                new_links[counter] = self.site_link + new_links[counter]
                                counter = counter + 1
                            else:
                                new_links[counter] = self.site_link + new_links[counter]
                                counter = counter + 1
                        else:
                            counter = counter + 1
                    else:
                        counter2 = 0
                        while counter2 < len(new_links):
                            if "#" not in new_links[counter2] and "mailto" not in new_links[counter2] and \
                                    ".jpg" not in new_links[counter2] and new_links[counter2] not in self.checked_links \
                                    and self.site_link in new_links[counter2]:
                                self.checked_links.append(new_links[counter2])
                                counter2 = counter2 + 1
                            else:
                                counter2 = counter2 + 1
                        else:
                            control = control + 1
                else:
                    control = control + 1

            except UserError:
                continue
            else:
                control = control + 1

        else:
            time.sleep(0.1)
            text_links = ''
            with open(f'{oo}/Sitemaps/{args.domain}/links_from_thread.txt', 'r') as f:
                for line in self.checked_links:
                    text_links += (line + '\n')
                    if line not in f:
                        run_command(f'echo "{text_links}" >> {oo}/Sitemaps/{args.domain}/links_from_thread.txt',
                                    echo=False)
            time.sleep(0.1)

        return self.temp_func_list

    def creating_sitemap(self):
        """
        Sitemap cr8 func()
        """
        time.sleep(2)
        os.system('clear')
        print('Creating Sitemap...')
        urlset = ET.Element("urlset", xlmns="http://www.sitemaps.org/schemas/sitemap/0.9")
        count = 0
        while count < len(self.checked_links_end):
            urls = ET.SubElement(urlset, "url")
            today = datetime.datetime.today().strftime('%Y-%m-%d')
            ET.SubElement(urls, "loc", ).text = str(self.checked_links_end[count])
            ET.SubElement(urls, "lastmod", ).text = str(today)
            ET.SubElement(urls, "priority", ).text = "1.00"
            count = count + 1
        else:
            tree = ET.ElementTree(urlset)

            print("Your Sitemap is Ready!\n Don't close, program is still running...\n Check link below later:")

        return tree

    def save_urls_to_filedat(self, checked_links=None):
        """
        Save url links from sitemap.xml to sitemap_urls.dat

        :param checked_links: None
        :return: file.dat as f:  f
        """
        sm_file_link = f'{oo}/Sitemaps/{args.domain}/sitemap.xml'
        with open(sm_file_link, 'r') as f:
            my_lines = list(f)
            for line in my_lines:
                soup = BeautifulSoup(line, "html.parser")
                new_links = [element.text for element in soup.findAll('loc')]
                # for link in new_links:
                # print(link)
            # print(new_links)

        with open(f'{oo}/Sitemaps/{args.domain}/sitemap_urls.dat', 'w') as f:
            for i in new_links:
                f.write(i + '\n')
        time.sleep(2)

        return f

    def mkdir(self, link_list=None, cmd=None):
        """
        Create many folders with mkdir command,
        use it to get mirror view of site folders

        mkdir() -> save_urls_to_filedat()
        """
        cmd = '-p'
        site_dir = f'~/Sitemaps/{args.domain}'
        run_command(f'mkdir {cmd} ' + f'{site_dir}', echo=False)
        run_command(f'touch ' + f'{site_dir}/sitemap.xml', echo=False)

        self.creating_sitemap().write(f'{oo}/Sitemaps/{args.domain}/sitemap.xml')
        sm_file_link = f'{oo}/Sitemaps/{args.domain}/sitemap.xml'
        print(f'{oo}/Sitemaps/{args.domain}/sitemap.xml')

        countt = 0
        for link in self.checked_links_end:
            new_link = link.replace('https://', '/').strip('\n')

            if new_link.startswith('/') and new_link.endswith('/'):
                run_command(f'mkdir {cmd} ' + f'~/Sitemaps{new_link}', echo=False)
            elif new_link.startswith('/') and not new_link.endswith('/'):
                countt += 1
                run_command(f'mkdir {cmd} ' + f'{site_dir}/z_other_links/', echo=False)
                run_command(f'touch ' + f'{site_dir}/z_other_links/other.txt')
                run_command(f'echo "{countt}. {link}" >> {site_dir}/z_other_links/other.txt')
            else:
                continue
        print("Folders set Ready!")

        return sm_file_link

    def mkdir_light(self, link_list=None, cmd=None):
        """
        Create folders, files with mkdir command

        mkdir_light() -> save_urls_to_filedat()
        """
        cmd = '-p'
        site_dir = f'~/Sitemaps/{args.domain}'
        run_command(f'mkdir {cmd} ' + f'{site_dir}', echo=False)
        run_command(f'touch ' + f'{site_dir}/sitemap.xml', echo=False)

        self.creating_sitemap().write(f'{oo}/Sitemaps/{args.domain}/sitemap.xml')
        sm_file_link = f'{oo}/Sitemaps/{args.domain}/sitemap.xml'
        print(f'{oo}/Sitemaps/{args.domain}/sitemap.xml')

        return sm_file_link


class CSVCreator:
    """
    Categorize a list of URLs by file path.

    The file containing the URLs should exist in the working directory and be
    named sitemap_urls.dat. It should contain one URL per line.
    """

    # Set global variables
    def __init__(self):
        super(CSVCreator, self).__init__()
        self.sitemap_layers = pd.DataFrame()  # Store results in a dataframe

    # Main script functions, слоев 5
    def peel_layers(self, urls, layers=5):
        """
        Builds a dataframe containing all unique page identifiers up
        to a specified depth and counts the number of sub-pages for each.
        Prints results to a CSV file.

        :param urls : list
            List of page URLs.

        :param layers : int
            Depth of automated URL search. Large values for this parameter
            may cause long runtimes depending on the number of URLs.

        :return: sitemap_layers = pd.Series(in urls) == DataFrame
        """

        # Get base levels
        bases = pd.Series([url.split('//')[-1].split('/')[0] for url in urls])
        self.sitemap_layers[0] = bases

        # Get specified number of layers
        for layer in range(1, layers + 1):

            page_layer = []
            for url, base in zip(urls, bases):
                try:
                    page_layer.append(url.split(base)[-1].split('/')[layer])
                except:
                    # There is nothing that deep!
                    page_layer.append('')

            self.sitemap_layers[layer] = page_layer

        # Count and drop duplicate rows + sort
        sitemap_layers = self.sitemap_layers.groupby(list(range(0, layers + 1)))[0].count() \
            .rename('counts').reset_index() \
            .sort_values('counts', ascending=False) \
            .sort_values(list(range(0, layers)), ascending=True) \
            .reset_index(drop=True)

        # Convert column names to string types and export
        sitemap_layers.columns = [str(col) for col in sitemap_layers.columns]
        sitemap_layers.to_csv(f'{oo}/Sitemaps/{args.domain}/sitemap_layers.csv', index=False)

        # Return the dataframe
        return sitemap_layers

    def make_csv(self):

        sitemap_urls = open(f'{oo}/Sitemaps/{args.domain}/sitemap_urls.dat', 'r').read().splitlines()
        print(f'Loaded {len(sitemap_urls)} URLs')

        print(f'Depth level is {args.level}')
        sitemap_layers = self.peel_layers(urls=sitemap_urls,
                                          layers=args.level)
        print(f'Printed {len(sitemap_layers)} rows of data to sitemap_layers.csv')
        time.sleep(2)


class VisualSitemapView:
    """
    Visualize a list of URLs by site path.

    This script reads in the sitemap_layers.csv file created by the
    categorize_urls.py script and builds a graph visualization using Graphviz.
    """

    # Set global variables
    def __init__(self):
        super(VisualSitemapView, self).__init__()

        # Update variables with arguments if included
        self.graph_depth = args.depth  # same == layer
        self.limit = args.limit
        self.title = args.title
        self.style = args.style
        self.size = args.size
        self.output_format = args.output_format
        self.skip = args.skip.split(',')

        self.layers_checked = 0  # checked layers == REAL DEPTH

    # Main script functions
    def make_sitemap_graph(self, sitemap_layers, layers, limit, size,
                           output_format, skip):
        """
        Make a sitemap graph up to a specified layer depth.

        sitemap_layers : DataFrame
            The dataframe created by the peel_layers function
            containing sitemap information.

        layers : int
            Maximum depth to plot.

        limit : int
            The maximum number node edge connections. Good to set this
            low for visualizing deep into site maps.

        output_format : string
            The type of file you want to save in PDF, PNG, TIFF, JPG

        skip : list
            List of branches that you do not want to expand.

        Check --help arg in terminal for more info
        """

        # Check to make sure we are not trying to create too many layers
        if layers > len(sitemap_layers) - 1:
            layers = len(sitemap_layers) - 1
            print(f'There are only {layers} layers available to create, setting layers = {layers}')
        self.layers = layers

        # Initialize graph
        f = graphviz.Digraph('sitemap', filename=f'{oo}/Sitemaps/{args.domain}/sitemap_graph_{layers}_layer',
                             format=f'{output_format}')
        f.body.extend(['rankdir=LR', f'size="{size}"'])

        def add_branch(f, names, vals, limit, connect_to=''):
            """ Adds a set of nodes and edges to nodes on the previous layer. """

            # Get the currently existing node names
            node_names = [item.split('"')[1] for item in f.body if 'label' in item]

            # Only add a new branch it it will connect to a previously created node
            if connect_to:
                if connect_to in node_names:
                    for name, val in list(zip(names, vals))[:limit]:
                        f.node(name=f'{connect_to}-{name}', label=name)
                        f.edge(connect_to, f'{connect_to}-{name}', label='{:,}'.format(val))

        f.attr('node', shape='rectangle')  # Plot nodes as rectangles

        # Add the first layer of nodes
        for name, counts in sitemap_layers.groupby(['0'])['counts'].sum().reset_index().sort_values(['counts'],
                                                                                                    ascending=False).values:
            f.node(name=name, label='{} ({:,})'.format(name, counts))

        if layers == 0:
            return f

        f.attr('node', shape='oval')  # Plot nodes as ovals
        f.graph_attr.update()

        # Loop over each layer adding nodes and edges to prior nodes
        for i in range(1, layers + 1):
            cols = [str(i_) for i_ in range(i)]
            nodes = sitemap_layers[cols].drop_duplicates().values
            for j, k in enumerate(nodes):

                # Compute the mask to select correct data
                mask = True
                for j_, ki in enumerate(k):
                    mask &= sitemap_layers[str(j_)] == ki

                # Select the data then count branch size, sort, and truncate
                data = sitemap_layers[mask].groupby([str(i)])['counts'].sum().reset_index().sort_values(['counts'],
                                                                                                        ascending=False)

                # Add to the graph unless specified that we do not want to expand k-1
                if (not skip) or (k[-1] not in skip):
                    add_branch(f,
                               names=data[str(i)].values,
                               vals=data['counts'].values,
                               limit=limit,
                               connect_to='-'.join(['%s'] * i) % tuple(k))

                print(f'Built graph up to node {j} / {len(nodes)} in layer {i}'.ljust(50), end='\r')

        return f

    def apply_style(self, f, style, title=''):
        """
        Apply the style and add a title if desired. More styling options are
        documented here: http://www.graphviz.org/doc/info/attrs.html#d:style

        f : graphviz.dot.Digraph
            The graph object as created by graphviz.

        style : str
            Available styles: 'light', 'dark'

        title : str
            Optional title placed at the bottom of the graph.
        """

        dark_style = {
            'graph': {
                'label': args.title,
                'bgcolor': '#3a3a3a',
                'fontname': 'Helvetica',
                'fontsize': '18',
                'fontcolor': 'white',
            },
            'nodes': {
                'style': 'filled',
                'color': 'white',
                'fillcolor': 'black',
                'fontname': 'Helvetica',
                'fontsize': '14',
                'fontcolor': 'white',
            },
            'edges': {
                'color': 'white',
                'arrowhead': 'open',
                'fontname': 'Helvetica',
                'fontsize': '12',
                'fontcolor': 'white',
            }
        }

        light_style = {
            'graph': {
                'label': args.title,
                'fontname': 'Helvetica',
                'fontsize': '18',
                'fontcolor': 'black',
            },
            'nodes': {
                'style': 'filled',
                'color': 'black',
                'fillcolor': '#dbdddd',
                'fontname': 'Helvetica',
                'fontsize': '14',
                'fontcolor': 'black',
            },
            'edges': {
                'color': 'black',
                'arrowhead': 'open',
                'fontname': 'Helvetica',
                'fontsize': '12',
                'fontcolor': 'black',
            }
        }

        if style == 'light':
            apply_style = light_style

        elif style == 'dark':
            apply_style = dark_style

        f.graph_attr = apply_style['graph']
        f.node_attr = apply_style['nodes']
        f.edge_attr = apply_style['edges']

        return f

    def make_pdf_jpg(self):
        # Read in categorized data
        sitemap_layers = pd.read_csv(f'{oo}/Sitemaps/{args.domain}/sitemap_layers.csv', dtype=str)

        # Convert numerical column to integer
        sitemap_layers.counts = sitemap_layers.counts.apply(int)
        print(f'Loaded {len(sitemap_layers)} rows of categorized data from sitemap_layers.csv')

        print('Building {} layer deep sitemap graph'.format(self.graph_depth))
        f = self.make_sitemap_graph(sitemap_layers, layers=self.graph_depth,
                                    limit=self.limit, size=self.size, output_format=self.output_format, skip=args.skip)
        f = self.apply_style(f, style=self.style, title=self.title)

        f.render(cleanup=True)
        print('Exported graph to {}/Sitemaps/{}/sitemap_graph_{}_layer.{}'.
              format(oo, args.domain, self.layers, self.output_format))
        time.sleep(5)
        run_command(f'open {oo}/Sitemaps/{args.domain}/sitemap_graph_{self.layers}_layer.{self.output_format}')
        time.sleep(2)
        run_command(f'open {oo}/Sitemaps/{args.domain}/sitemap.xml')


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        prog='sitemapBuilder',
        usage='%(prog)s [domain] -l [level] -d [depth]      type -h, --help for more info\n'
              '>>> sitemapBuilder.py examplesite.com\n'
              '\n'
              'check that sitemapBuilder.py is in your Home directory\n'
              '-----',
        formatter_class=argparse.RawDescriptionHelpFormatter,  # формат красивого отображения, см. док-ю
        description=textwrap.dedent('''
            Please Note, that all sitemaps will be at your home directory: 
            for example -  /Users/agent007/Sitemaps/github.com  
            --------------------------------------------
                 _____________________________________
                < Oh wow, you're on the sitemap prog! >
                 -------------------------------------
                        \   ^__^
                         \  (oo)\_______
                            (__)\       )\/\'
                                ||----w |
                                ||     ||
                        Check --help info below
            '''),
        epilog=textwrap.dedent('''
            --------------------------------------------
            The End

            ''')
    )
    arg_parser.add_argument(
        'domain',
        type=str,
        help="Site link : vistexample.ru"
    )
    arg_parser.add_argument(
        '-l', '--level',
        dest="level",  # возвращает имя аргументу через args = parse_args() -> if args.get('level'):       nargs='?',
        default=5,  # значение по умолчанию для глубины
        type=int,
        metavar='',  # имя аргумента в сообщении использования
        help="search depth level, глубина рекурсии поиска ссылок",
        action="store"
    )
    arg_parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0'
    )
    arg_parser.add_argument(
        '-w', '--workers',
        dest="workers",  # возвращает имя аргументу через args = parse_args() -> if args.get('level'):       nargs='?',
        default=5,  # значение по умолчанию для глубины
        type=int,
        metavar='',  # имя аргумента в сообщении использования
        help="this workers = threads, the number will auto set depending on number of 1st level links, "
             "запускаем потоки исходя из количества папок первого уровня",
        action="store"
    )

    # есть проблема с отображением в связи main -> args.xxx -> make_sitemap_graph
    # depth = 5  # Number of layers deep to plot categorization
    # limit = 50  # Maximum number of nodes for a branch
    # title = ''  # Graph title
    # style = 'light'  # Graph style, can be "light" or "dark"
    # size = '8,5'  # Size of rendered graph
    # output_format = 'pdf'  # Format of rendered image - pdf,png,tiff
    # skip = ''  # List of branches to restrict from expanding
    arg_parser.add_argument('-d', '--depth', dest="depth", type=int, default=5,
                            help='number of layers deep to plot categorization, количество слоев', metavar='')
    arg_parser.add_argument('--limit', dest="limit", type=int, default=50,
                            help='maximum number of nodes for a branch', metavar='')
    arg_parser.add_argument('--title', dest="title", type=str, default='',
                            help='graph title', metavar='')
    arg_parser.add_argument('--style', dest="style", type=str, default='light',
                            help='graph style, can be "light" or "dark"', metavar='')
    arg_parser.add_argument('--size', dest="size", type=str, default='8,5',
                            help='size of rendered graph', metavar='')
    arg_parser.add_argument('--output-format', dest="output_format", type=str, default='pdf',
                            help='format of the graph you want to save. Allowed -- JPG, PDF, PNG, TIF', metavar='')
    arg_parser.add_argument('--skip', dest="skip", type=str, default='', metavar='',
                            help="list of branches that you do not want to expand. Comma separated: e.g. --skip 'news,events,datasets'")

    args = arg_parser.parse_args()

    # get home dir link: oo = /Users/box$
    run_command('cd ~/')
    oo1 = run_command('pwd')
    oo = oo1[1].strip('\n')

    wrong = re.search(
                    '/[-;:+%"!@^±§&<>#_=?.a-zA-Z0-9]{2,100}[.]{1,100}[-;:+%"!@^±§&<>#_=?.a-zA-Z0-9]{2,100}$',
                    args.domain)  # ignore dark net sites :P
    w2 = args.domain
    if '/' in w2 or ',' in w2 or 'http' in w2 or 'https' in w2 or wrong is not None:
        print('Something Wrong with Domain')
        print('Please Type:  sitemapBuilder.py --help   or correct domain')

    else:
        try:
            r = requests.get(f'https://{args.domain}/')
            if r.status_code == 200:
                print('stastus_code = 200 all is ok')
        except BaseException as err:
            raise UserError('Error!', err)
        finally:
            r = requests.get(f'https://{args.domain}/')
            if r.status_code != 200:
                print('DOMAIN WRONG, TRY READ: --help info')
                print('OR YOU CANT MAKE MACHINE REQUESTS ON THIS DOMAIN')
                print('THIS FUNCTION IS NOT UP YET')
                sys.exit()
            else:
                timestart = time.time()
                print(f'=========== START ===========')

                # make response
                SMCr8or = Sitemap()
                ses = SMCr8or.request_session()
                text = SMCr8or.start(ses)

                # crawling + folder cr8ion
                SMCr8or.thread_activator()
                SMCr8or.mkdir_light()   # or SMCr8or.mkdir()

                print(f'===========CR8 DAT===========')

                # saving data
                SMCr8or.save_urls_to_filedat()

                print(f'===========CR8 SCV=========== {time0}')

                # creating scv file
                creator = CSVCreator()
                creator.make_csv()

                print(f'===========CR8 PDF=========== {time1}')

                # create pdf/jpg/png/tif (chouse in terminal, default = pdf)
                creator2 = VisualSitemapView()
                creator2.make_pdf_jpg()

                time_ = time.time()
                timeend = time_ - timestart
                print(f'===========THE END=========== Time = '
                      f'{str(timeend).split(".")[0]}.{str(timeend).split(".")[1][:3]} sec')
