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

from bs4 import BeautifulSoup
import re
import threading
import multiprocessing

import xml.etree.cElementTree as ET

import pandas as pd
import graphviz

"""User-Agent: Mozilla/<version> (<system-information>) <platform> (<platform-details>) <extensions>"""

User_Agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; MSOffice 12)'
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; MSOffice 12)'
encoding = 'UTF-8'

# Mulitprocess/Threading time test
time0 = ''
time1 = ''
timetime = ''

"""List of status codes:
Diagram of web-server decision based on headers
Code statistic from log analyzer: Webalizer
1xx: Informational:
2xx: Success:
3xx: Redirection:
4xx: Client Error:
5xx: Server Error:
check https://ru.wikipedia.org/wiki/Список_кодов_состояния_HTTP"""

stat_code_dict = {
    '100': 'Continue («продолжай»)[2][3];',
    '101': 'Switching Protocols («переключение протоколов»)[2][3];',
    '102': 'Processing («идёт обработка»).',

    '200': 'OK («хорошо»)[2][3];',
    '201': 'Created («создано»)[2][3][4];',
    '202': 'Accepted («принято»)[2][3];',
    '203': 'Non-Authoritative Information («информация не авторитетна»)[2][3];',
    '204': 'No Content («нет содержимого»)[2][3];',
    '205': 'Reset Content («сбросить содержимое»)[2][3];',
    '206': 'Partial Content («частичное содержимое»)[2][3];',
    '207': 'Multi-Status («многостатусный»)[5];',
    '208': 'Already Reported («уже сообщалось»)[6];',
    '226': 'IM Used («использовано IM»).',

    '300': 'Multiple Choices («множество выборов»)[2][7];',
    '301': 'Moved Permanently («перемещено навсегда»)[2][7];',
    '302': 'Moved Temporarily («перемещено временно»)[2][7];',
    # '302': 'Found («найдено»)[7];',
    '303': 'See Other («смотреть другое»)[2][7];',
    '304': 'Not Modified («не изменялось»)[2][7];',
    '305': 'Use Proxy («использовать прокси»)[2][7];',
    '306': '— зарезервировано (код использовался только в ранних спецификациях)[7];',
    '307': 'Temporary Redirect («временное перенаправление»)[7];',
    '308': 'Permanent Redirect («постоянное перенаправление»)[8].',

    '400': 'Bad Request («плохой, неверный запрос»)[2][3][4];',
    '401': 'Unauthorized («не авторизован (не представился)»)[2][3];',
    '402': 'Payment Required («необходима оплата»)[2][3];',
    '403': 'Forbidden («запрещено (не уполномочен)»)[2][3];',
    '404': 'Not Found («не найдено»)[2][3];',
    '405': 'Method Not Allowed («метод не поддерживается»)[2][3];',
    '406': 'Not Acceptable («неприемлемо»)[2][3];',
    '407': 'Proxy Authentication Required («необходима аутентификация прокси»)[2][3];',
    '408': 'Request Timeout («истекло время ожидания»)[2][3];',
    '409': 'Conflict («конфликт»)[2][3][4];',
    '410': 'Gone («удалён»)[2][3];',
    '411': 'Length Required («необходима длина»)[2][3];',
    '412': 'Precondition Failed («условие ложно»)[2][3][9];',
    '413': 'Payload Too Large («полезная нагрузка слишком велика»)[2][3];',
    '414': 'URI Too Long («URI слишком длинный»)[2][3];',
    '415': 'Unsupported Media Type («неподдерживаемый тип данных»)[2][3];',
    '416': 'Range Not Satisfiable («диапазон не достижим»)[3];',
    '417': 'Expectation Failed («ожидание не удалось»)[3];',
    '418': 'I’m a teapot («я — чайник»);',
    '419': 'Authentication Timeout (not in RFC 2616) («обычно ошибка проверки CSRF»);',
    '421': 'Misdirected Request [10];',
    '422': 'Unprocessable Entity («необрабатываемый экземпляр»);',
    '423': 'Locked («заблокировано»);',
    '424': 'Failed Dependency («невыполненная зависимость»);',
    '426': 'Upgrade Required («необходимо обновление»);',
    '428': 'Precondition Required («необходимо предусловие»)[11];',
    '429': 'Too Many Requests («слишком много запросов»)[11];',
    '431': 'Request Header Fields Too Large («поля заголовка запроса слишком большие»)[11];',
    '449': 'Retry With («повторить с»)[1];',
    '451': 'Unavailable For Legal Reasons («недоступно по юридическим причинам»)[12].',
    '499': 'Client Closed Request (клиент закрыл соединение);',

    '500': 'Internal Server Error («внутренняя ошибка сервера»)[2][3];',
    '501': 'Not Implemented («не реализовано»)[2][3];',
    '502': 'Bad Gateway («плохой, ошибочный шлюз»)[2][3];',
    '503': 'Service Unavailable («сервис недоступен»)[2][3];',
    '504': 'Gateway Timeout («шлюз не отвечает»)[2][3];',
    '505': 'HTTP Version Not Supported («версия HTTP не поддерживается»)[2][3];',
    '506': 'Variant Also Negotiates («вариант тоже проводит согласование»)[13];',
    '507': 'Insufficient Storage («переполнение хранилища»);',
    '508': 'Loop Detected («обнаружено бесконечное перенаправление»)[14];',
    '509': 'Bandwidth Limit Exceeded («исчерпана пропускная ширина канала»);',
    '510': 'Not Extended («не расширено»);',
    '511': 'Network Authentication Required («требуется сетевая аутентификация»)[11];',
    '520': 'Unknown Error («неизвестная ошибка»)[15];',
    '521': 'Web Server Is Down («веб-сервер не работает»)[15];',
    '522': 'Connection Timed Out («соединение не отвечает»)[15];',
    '523': 'Origin Is Unreachable («источник недоступен»)[15];',
    '524': 'A Timeout Occurred («время ожидания истекло»)[15];',
    '525': 'SSL Handshake Failed («квитирование SSL не удалось»)[15];',
    '526': 'Invalid SSL Certificate («недействительный сертификат SSL»)[15].'
}


def run_command(cmd, echo=True, exit_on_error=False):
    """Communication to bash frow terminal using subprocess"""
    p = Popen(cmd, stdout=subprocess.PIPE, stderr=PIPE, shell=True, universal_newlines=True)
    o, e = p.communicate()
    return p.returncode, o, e


class UserError(Exception):
    """exception class UserError"""
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
        self.site_link_nos = f'https://{args.domain}'
        self.workers_count = args.workers               # number of threads: depends on number of 1st level folders
        self.thread_folders = list()                      # 1st level links that we need for threads to run on
        self.thread_name = ''                           # name of the link from thread_folders

        self.checked_links_almost = []                  # intermediate list
        self.checked_links_end = []                     # the final list of all checked_links from each thread
        self.checked_threads = []                           # not used list
        self.temp_func_list = []                        # intermediate list

    def status_codes_checker(self, code):
        """
        Check the response status code match with stat_code_dict and print message
            for ex: 401 Unauthorized
        """
        code = str(code)
        if code.startswith('1'):
            print(code + ' ' + stat_code_dict[code])
        elif code.startswith('2'):
            print(code + ' ' + stat_code_dict[code])
        elif code.startswith('3'):
            print(code + ' ' + stat_code_dict[code])
        elif code.startswith('4'):
            print(code + ' ' + stat_code_dict[code])
        elif code.startswith('5'):
            print(code + ' ' + stat_code_dict[code])

        # return code

    def chouse_filter(self, filter):
        """This function will filter links.
            for example you don't want: '-' or '?' or '_' in your sitemap links then chouse filter='max',
            else chouse filter='min'
            .......in development
        """
        if filter == 'max':
            pass

        elif filter == 'min':
            pass
        else:
            pass

    def chouse_depth(self, fdepth, link_list):
        """Folders number depth you want to check in links"""
        if type(fdepth) is not int or fdepth < 1:
            fdepth = 1
            print('Wrong folders depth. Setting: -fd 1')
        if fdepth > 10:
            fdepth = 10
            print('Too high depth. Setting: -fd 10')

        fdepth_list = list()
        for link in link_list:
            aa = '/'
            folder = link.replace(f'{self.site_link}', '').split('/')
            for i in folder:
                if i == '':
                    folder.remove(i)
            for i in range(len(folder)):
                if i <= fdepth - 1:
                    aa = aa + f'{folder[i]}/'
            # print('aa=', aa)
            if aa is not "/" and "mailto" not in aa and "#" not in aa and "tel" not in aa and aa not in fdepth_list and \
                    " " not in aa and "?" not in aa and ":" not in aa and not aa.endswith('dot'):
                fdepth_list.append(aa)
            #     print('appended aa=', aa)
            # print('folder=', folder)

        # print(fdepth_list)
        cc = 0
        while cc < len(fdepth_list):
            for i in fdepth_list:
                fdepth_list[cc] = f'{self.site_link_nos}' + i
                cc += 1

        return fdepth_list

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
        req = session.get(f'{url}')

        return req

    def worker(self, thread_name, checked_links, qq):
        """
        Worker gonna do his job - make requests in thread!

        :param thread_name:
        :param checked_links:
        :param qq: the way I find to to put extra worker(thread)
        :return: self.checked_links
        """
        if (qq + 1) != self.workers_count:
            print('Main worker ', qq + 1)
            th = threading.Thread(target=self.crawling_web_pages, args=(0, 3, self.thread_folders, self.checked_threads,
                                                                        thread_name, qq))
            th.start()
        else:
            if (qq + 1) == self.workers_count:
                print('Extra worker', qq + 1)
                thth = threading.Thread(target=self.crawling_1st_page_other_links,
                                    args=(0, self.thread_folders, self.checked_threads, self.checked_links, qq))
                thth.start()

        return self.checked_links

    def worker_threading_domains(self, link, link_session):
        """
        BACKGROUND: CREATION OF THREAD PROCESSING FOR MULTIPLE DOMAINS AT THE SAME TIME IN ONE PROCESS

        :param link: he get link from        -checked_links
        :param link_session: use instrument  -session (with headers)
        :return:
        """
        # th = threading.Thread(target=self.crawling_web_pages, args=(control, arg2))
        # th.start()
        # print('\n\nBreak worker\n\n')
        pass

    def dot_in_the_endlink(self, counter_x=None, link_list=None, link=None):
        dot_in_the_endlink = 'None'
        if link is None:
            search_links = re.search(
                '/[-;:+%"!@^±§& <>#_=?.a-zA-Z0-9]{2,100}[.]{1,100}[-;:+%"!@^±§& <>#_=?.a-zA-Z0-9]{2,100}$',
                link_list[counter_x])
            if search_links is not None:
                dot_in_the_endlink = search_links.group()
        else:
            search_links = re.search(
                '/[-;:+%"!@^±§& <>#_=?.a-zA-Z0-9]{2,100}[.]{1,100}[-;:+%"!@^±§& <>#_=?.a-zA-Z0-9]{2,100}$',
                link)
            if search_links is not None:
                dot_in_the_endlink = search_links.group()

        return dot_in_the_endlink

    def BSoup(self, source_code, parser=None):
        """
        Find all HREF, DATA_HREF, SRC -> and put it in list:  NEW_LINKS

        :param source_code:
        :param parser: "html.parser", "lxml", "lxml-xml", "xml", "html5lib"
        check https://en.wikipedia.org/wiki/Beautiful_Soup_(HTML_parser)
        :return: new_links
        """
        soup = BeautifulSoup(source_code, parser)
        new_links = [h['href'] for h in soup.findAll('a', href=True)]  # get all links from that page
        data_href = [d.get('data-href') for d in soup.findAll()]  # get "replace" links such as /en, /fr
        src = [s.get('src') for s in soup.findAll()]
        # add links to list
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

        return new_links

    def thread_activator(self):
        """
        Run Threads depending on number of workers
        """
        # PROCESSING: WE RECEIVE LIST SELF.CHECKED_LINKS, SELF.THREAD_FOLDERS LEVELS 1
        self.start_crawling()

        # the way I found to put extra thread worker.
        # in development: further args for func() that'll get links from robots.txt
        self.thread_folders.append(f'https://{args.domain}/robot.txt')

        # here we can put code to increase number of workers from args.worker
        self.workers_count = len(self.thread_folders)
        print('Workers number =', self.workers_count)

        # PROCESSING: STARTING STREAM PROCESSING. WE STRIPE EVERY FIRST LEVEL LINK
        # here we have absolute thread name https://vistgroup.ru/company/
        cmd = '-p'
        site_dir = f'{home}/Sitemaps/{args.domain}'
        run_command(f'mkdir {cmd} ' + f'{site_dir}', echo=False)
        # don't find out the other good way to take args from thread so I gonna write args to text files with echo
        run_command(f'touch ' + f'{site_dir}/links_from_thread.txt', echo=False)
        run_command(f'touch ' + f'{site_dir}/extra_thread.txt', echo=False)

        # process list with workers
        workers_list = [multiprocessing.Process(target=self.worker,
                                                args=(self.thread_folders[i], [self.thread_folders[i]], i))
                        for i in range(self.workers_count)]
        for w in workers_list:
            w.start()
        for w in workers_list:
            w.join()

        # TEMPORARY DECISION BECAUSE I'VE NO IDEA HOW TO TAKE DATA FROM THREADS, POSSIBLY SHOULD
        # CHECK SUBPROGRAMS AND TRY USE ASINCIO PROGRAMING
        # SAVE TO TEMPORARY FILE.TXT ALL LINKS FROM THREAD, GET DATA AND DELETE IT AFTER
        # echo write args from threads to file.txt
        with open(f'{home}/Sitemaps/{args.domain}/links_from_thread.txt', 'r') as f:
            a = f.read()
            self.checked_links_almost = a.split('\n')

        for links in self.checked_links_almost:
            dot_in_link = self.dot_in_the_endlink(link_list=self.checked_links_almost, link=links)
            if links is not None and links != '' and links not in self.checked_links_end and \
                    not links.endswith(dot_in_link):
                self.checked_links_end.append(links)

        with open(f'{home}/Sitemaps/{args.domain}/extra_thread.txt', 'r') as f:
            b = f.read()
            self.temp_func_list = b.split('\n')
        for linkss in self.temp_func_list:
            if linkss is not None and linkss != '' and linkss not in self.checked_links_end:
                self.checked_links_end.append(linkss)
        # remove temp .txt files
        run_command(f'rm {home}/Sitemaps/{args.domain}/links_from_thread.txt')
        run_command(f'rm {home}/Sitemaps/{args.domain}/extra_thread.txt')

    def start_crawling(self):
        """
        Starts crawling function to find first level links

        :return: self.checked_links, self.thread_folders, self.checked_threads
        """
        print('https://' + f'{args.domain}')
        print('Crawling...')
        time.sleep(3)
        self.checked_links.append(f'https://{args.domain}/')
        print('len = ', len(self.checked_links))

        # crawl 1st page to find folders and then append em to thread_folders list
        self.crawling_web_pages(control=0, count_try=0, thread_folders=[], checked_links=self.checked_links)

        # BACKGROUND: CREATION OF THREAD PROCESSING FOR MULTIPLE DOMAINS AT THE SAME TIME IN ONE PROCESS
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

        return self.checked_links, self.thread_folders, self.checked_threads

    # ex: checked_links = [ 'https://vistgroup.ru/', 'https://vistgroup.ru/company/about/', ... ]
    def crawling_web_pages(self, control, count_try, thread_folders, checked_links, thread_name=None, qq=None):
        """
        We start with:
        crawling_web_pages(0, 0, [], [https://domain]) -> crawling_web_pages() +
        crawling_1st_page_other_links() as extra worker
        Web scraping is ON. Выскабливаем линки с сайта
        Check main page links then -> Check all found out links

        :return: list: checked_links [link1, link2, ...]
        """
        self.thread_folders = thread_folders
        self.checked_links = checked_links

        # CHECK ALL LINKS IN LIST: CHECKED_LINKS
        # I: fill in lists: checked_links, checked_threads, thread_folders
        # II: start threads processing
        # III: start extra thread processing for links except checked_threads links, thread_folders
        while control < len(self.checked_links):
            try:
                # PROCESSING: USE .SPLIT('/') FUNCTION TO EVERY LINK AND SEPARATELY CHECK EACH LEVEL 1 FOLDER
                # WAY OF CREATION => /EN/SOLUTIONS/EXTRA/SOMETHING1/SOMETHING2/ -> /EN/ -> /EN/SOLUTIONS ->
                # /EN/SOLUTIONS/EXTRA/ -> ...

                # THIS PROCESSING FIND NEW THREAD_FOLDERS ON THE MAIN PAGE
                count_try += 1
                if 2 <= count_try <= 3 and len(self.checked_links) > 1:   # and thread_name is None:
                    for link in self.checked_links:
                        k = link.split('/')
                        if f'/{k[3]}/' not in self.thread_folders and k[3] != "" and \
                                "mailto" not in k and "tel" not in k:
                            self.thread_folders.append(f'/{k[3]}/')
                            self.checked_threads.append(self.site_link_nos + f'/{k[3]}/')
                    # ['/company/', '/solutions/', '/media/', '/contacts/', '/en/', '/local/', '/bitrix/', '/upload/']
                    # ['https://vistgroup.ru/company/', 'https://vistgroup.ru/solutions/', 'https://... ]
                if count_try == 3:
                    break

                # PROCESSING: FIND ALL LINKS LIKE /captcha2.php?captcha_sid=02529b019fa5ecfb5b45a1d38e04308e
                # /vg-underground_C2_A0v2_C2_A0FR.png AND IGNORE THEM, ALSO IGNORE:  /*.PDF
                dot_in_link = self.dot_in_the_endlink(counter_x=control, link_list=self.checked_links)

                if not self.checked_links[control].endswith(dot_in_link):
                    if thread_name is not None:
                        try:
                            # setting folders number depth you want to check in links
                            self.checked_links = self.chouse_depth(args.fdepth, self.checked_links)

                            responses = self.request(self.checked_links[control], self.request_session())
                            source_code = responses.text
                            status_code = responses.status_code
                        except IndexError as err:
                            raise UserError('Error!', err)
                    else:
                        responses = self.request(self.checked_links[control], self.request_session())
                        source_code = responses.text
                        status_code = responses.status_code

                    # check status, prints status, if 400+ pass
                    self.status_codes_checker(code=status_code)
                    if str(status_code).startswith('4'):
                        control = control + 1
                    else:
                        # PROCESSING: FIND ALL HREF, DATA_HREF, SRC -> AND PUT IN LIST:  NEW_LINKS
                        new_links = self.BSoup(source_code=source_code, parser="html.parser")

                        # PROCESSING: LINKS FROM NEW_LINKS TO -> CHECKED_LINKS
                        counter = 0
                        while counter < len(new_links):
                            # this code is for thouse relative links witch starts with / slash
                            if "http" not in new_links[counter]:  # checking if the linking on this site is absolute or
                                # relative -> starts with http or /
                                # Enter '/company/', '/solutions/'
                                verify0 = new_links[counter][0]

                                # getting first character of every link & if it starts with slash / then
                                # we remove this / slash bec we have already added the slash at the end of the domain
                                if verify0 == '/':
                                    # join thread links with domain to make them absolute links
                                    # processing for thread links -> thread_name == thread_folders[i]

                                    # /mobile/separate_desktop/
                                    new_links[counter] = new_links[counter][:1].replace('/', '') + new_links[counter][1:]
                                    # mobile/separate_desktop/
                                    # this will remove only first slash in the link  /string  not every slash

                                    # join these relative links with domain to make them absolute links
                                    new_links[counter] = self.site_link + new_links[counter]
                                    # ['https://vistgroup.ru/company/', 'https://vistgroup.ru/solutions/']
                                else:
                                    # this code is for thouse relative links witch doesn't starts with / slash
                                    new_links[counter] = self.site_link + new_links[counter]
                                    counter = counter + 1
                            else:
                                counter = counter + 1
                        else:
                            counter2 = 0
                            while counter2 < len(new_links):
                                if thread_name is None and qq is None:
                                    # here we can apply any filter so if the contain any of these strings then
                                    # don't append this link into the final array where we are collecting /
                                    # appending all the links found in that website
                                    if "#" not in new_links[counter2] and "mailto" not in new_links[counter2] and \
                                            ".jpg" not in new_links[counter2] and new_links[counter2] not in \
                                            self.checked_links and self.site_link in new_links[counter2]:
                                        # new_links[counter2] not in self.checked_links:- this condition is very
                                        # important,
                                        # this will never append a link in the array which already exist in the array...
                                        # without this condition this script will never end and start appending the same
                                        # site / link again:

                                        # last condition of script will add only the links in the array which have the
                                        # domain and will never append the links which redirect to another websites
                                        # (many website have links to youtube facebook etc)
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
                                    # thread_name is not None:
                                    if "#" not in new_links[counter2] and "mailto" not in new_links[counter2] and \
                                            ".jpg"not in new_links[counter2] and \
                                            new_links[counter2] not in self.checked_links and \
                                            self.site_link in new_links[counter2] and \
                                            thread_name in new_links[counter2] and \
                                            new_links[counter2].startswith(f'{self.site_link_nos}{thread_name}'):

                                        self.checked_links.append(new_links[counter2])

                                        time.sleep(0.1)
                                        os.system('clear')
                                        # if qq is not None and int(qq) < 10:
                                        #     qq = str(qq) + ' '
                                        # else:
                                        #     string = ''
                                        print(f'thread {qq}: ' + str(control) + '/' + str(len(self.checked_links)))
                                        print('')
                                        print(str(control) + ' Web Pages Crawler & ' + str(
                                            len(self.checked_links)) + " Web Pages Found")
                                        print('')
                                        print(new_links[counter2])  # display the current site_link
                                        counter2 = counter2 + 1
                                    else:
                                        counter2 = counter2 + 1
                            else:
                                time.sleep(0.1)
                                os.system('clear')
                                # if qq is not None and int(qq) < 10:
                                #     qq = str(qq) + ' '
                                print(f'thread {qq}: ' + str(control) + '/' + str(len(self.checked_links)))
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
            with open(f'{home}/Sitemaps/{args.domain}/links_from_thread.txt', 'r') as f:
                for line in self.checked_links:
                    text_links += (line + '\n')
                    if line not in f:
                        run_command(f'echo "{text_links}" >> {home}/Sitemaps/{args.domain}/links_from_thread.txt',
                                    echo=False)
            time.sleep(0.1)

        return self.checked_links, self.thread_folders, self.checked_threads, self.temp_func_list

    # ex: checked_links = [ 'https://vistgroup.ru/' ]
    def crawling_1st_page_other_links(self, control, thread_folders, checked_threads, checked_links, qq):
        """
        This function is for those links, which do not contains thread_folders
        """
        self.checked_threads = checked_threads
        self.checked_links = checked_links
        self.thread_folders = thread_folders

        while control < len(self.checked_links):
            try:
                # PROCESSING: FIND ALL LINKS LIKE /captcha2.php?captcha_sid=02529b019fa5ecfb5b45a1d38e04308e
                # /vg-underground_C2_A0v2_C2_A0FR.png AND IGNORE THEM, ALSO IGNORE:  /*.PDF
                dot_in_link = self.dot_in_the_endlink(counter_x=control, link_list=self.checked_links)

                if not self.checked_links[control].endswith(dot_in_link) and \
                        self.checked_links[control] not in self.checked_threads:

                    try:
                        # setting folders number depth you want to check in links
                        self.checked_links = self.chouse_depth(args.fdepth, self.checked_links)

                        responses = self.request(self.checked_links[control], self.request_session())
                        source_code = responses.text
                        status_code = responses.status_code
                    except IndexError as err:
                        raise UserError('Error!', err)

                    # check status, prints status, if 400+ pass link
                    self.status_codes_checker(code=status_code)
                    if str(status_code).startswith('4'):
                        control = control + 1
                    else:
                        # PROCESSING: FIND ALL HREF, DATA_HREF, SRC -> AND PUT IN LIST:  NEW_LINKS
                        new_links = self.BSoup(source_code=source_code, parser="html.parser")

                        counter = 0
                        while counter < len(new_links):
                            if "http" not in new_links[counter]:
                                verify = new_links[counter][0]
                                if verify == '/':
                                    new_links[counter] = new_links[counter][:1].replace('/', '') + \
                                                         new_links[counter][1:]
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
                                ignore_start = 'ffs'
                                # /company/
                                for elsfolder in self.thread_folders:
                                    if elsfolder in new_links[counter2]:
                                        # 'https://vistgroup.ru/company/'
                                        ignore_start = f'{self.site_link_nos}{elsfolder}'
                                if "#" not in new_links[counter2] and "mailto" not in new_links[counter2] and \
                                        ".jpg" not in new_links[counter2] and \
                                        new_links[counter2] not in self.checked_links \
                                        and self.site_link in new_links[counter2] and \
                                        not new_links[counter2].startswith(ignore_start):

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
            with open(f'{home}/Sitemaps/{args.domain}/links_from_thread.txt', 'r') as f:
                for line in self.checked_links:
                    text_links += (line + '\n')
                    if line not in f:
                        run_command(f'echo "{text_links}" >> {home}/Sitemaps/{args.domain}/links_from_thread.txt',
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
        sm_file_link = f'{home}/Sitemaps/{args.domain}/sitemap.xml'
        with open(sm_file_link, 'r') as f:
            my_lines = list(f)
            for line in my_lines:
                soup = BeautifulSoup(line, "html.parser")
                new_links = [element.text for element in soup.findAll('loc')]

        with open(f'{home}/Sitemaps/{args.domain}/sitemap_urls.dat', 'w') as f:
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

        self.creating_sitemap().write(f'{home}/Sitemaps/{args.domain}/sitemap.xml')
        sm_file_link = f'{home}/Sitemaps/{args.domain}/sitemap.xml'
        print(f'{home}/Sitemaps/{args.domain}/sitemap.xml')

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

        self.creating_sitemap().write(f'{home}/Sitemaps/{args.domain}/sitemap.xml')
        sm_file_link = f'{home}/Sitemaps/{args.domain}/sitemap.xml'
        print(f'{home}/Sitemaps/{args.domain}/sitemap.xml')

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
        sitemap_layers.to_csv(f'{home}/Sitemaps/{args.domain}/sitemap_layers.csv', index=False)

        # Return the dataframe
        return sitemap_layers

    def make_csv(self):

        sitemap_urls = open(f'{home}/Sitemaps/{args.domain}/sitemap_urls.dat', 'r').read().splitlines()
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
        f = graphviz.Digraph('sitemap', filename=f'{home}/Sitemaps/{args.domain}/sitemap_graph_{layers}_layer',
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
        sitemap_layers = pd.read_csv(f'{home}/Sitemaps/{args.domain}/sitemap_layers.csv', dtype=str)

        # Convert numerical column to integer
        sitemap_layers.counts = sitemap_layers.counts.apply(int)
        print(f'Loaded {len(sitemap_layers)} rows of categorized data from sitemap_layers.csv')

        print('Building {} layer deep sitemap graph'.format(self.graph_depth))
        f = self.make_sitemap_graph(sitemap_layers, layers=self.graph_depth,
                                    limit=self.limit, size=self.size, output_format=self.output_format, skip=args.skip)
        f = self.apply_style(f, style=self.style, title=self.title)

        f.render(cleanup=True)
        print('Exported graph to {}/Sitemaps/{}/sitemap_graph_{}_layer.{}'.
              format(home, args.domain, self.layers, self.output_format))
        time.sleep(5)
        run_command(f'open {home}/Sitemaps/{args.domain}/sitemap_graph_{self.layers}_layer.{self.output_format}')
        time.sleep(2)
        run_command(f'open {home}/Sitemaps/{args.domain}/sitemap.xml')


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        prog='sitemapBuilder',
        usage='%(prog)s [domain] -l [level] -d [depth]      type -h, --help for more info\n'
              '>>> sitemapBuilder.py examplesite.com\n'
              '\n'
              'check that sitemapBuilder.py is in your Home directory\n'
              '-----',
        formatter_class=argparse.RawDescriptionHelpFormatter,  # pretty print format
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
        dest="level",  # returns the name of the argument through args = parse_args() -> if args.get('level'):
        default=5,  # default value for depth
        type=int,
        metavar='',  # argument name in usage message
        help="search depth level (fo CSVCreator), глубина рекурсии поиска ссылок (для CSVCreator)",
        action="store"
    )
    arg_parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0'
    )
    arg_parser.add_argument(
        '-w', '--workers',
        dest="workers",
        default=5,
        type=int,
        metavar='',
        help="this workers = threads, the number will auto set depending on number of 1st level links, "
             "запускаем потоки исходя из количества папок первого уровня",
        action="store"
    )
    arg_parser.add_argument(
        '-fd', '--folder-depth',
        dest="fdepth",
        default=2,
        type=int,
        metavar='',
        help="THE MOST USEFUL ARGUMENT, default set -fd 2, if you try to make sitemap and graph map for yandex.ru "
             "or google.com it will stops on /news/ folder and all will be good. Else if you set -fd 4 for yandex.ru "
             "it wil find links over 50 000+ in /news/ folder and probably you get request exception or any bug "
             "that I do not explore yet, глубина поиска папок на сайте ",
        action="store"
    )

    # there are some problems with display dependencies: main -> args.xxx -> make_sitemap_graph
    # depth = 5  # Number of layers deep to plot categorization
    # limit = 50  # Maximum number of nodes for a branch
    # title = ''  # Graph title
    # style = 'light'  # Graph style, can be "light" or "dark"
    # size = '8,5'  # Size of rendered graph
    # output_format = 'pdf'  # Format of rendered image - pdf,png,tiff
    # skip = ''  # List of branches to restrict from expanding
    arg_parser.add_argument('-d', '--depth', dest="depth", type=int, default=5, metavar='',
                            help='number of layers deep to plot categorization (for VisualSitemapView), '
                                 'количество слоев (для VisualSitemapView)')
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
                            help="list of branches that you do not want to expand. "
                                 "Comma separated: e.g. --skip 'news,events,datasets'")

    args = arg_parser.parse_args()

    # get home dir link: home = /Users/box$
    run_command('cd ~/')
    oo1 = run_command('pwd')
    home = oo1[1].strip('\n')

    wrong = re.search(
                    '/[-;:+%"!@^±§& <>#_=?.a-zA-Z0-9]{2,100}[.]{1,100}[-;:+%"!@^±§& <>#_=?.a-zA-Z0-9]{2,100}$',
                    args.domain)  # ignore dark net sites :P
    w2 = args.domain
    if '/' in w2 or ',' in w2 or 'http' in w2 or 'https' in w2 or wrong is not None:
        print('Something Wrong with Domain')
        print('Please Type:  sitemapBuilder.py --help   or correct domain')

    else:
        try:
            r = requests.get(f'https://{args.domain}/')
            _code = r.status_code

            if _code == 200:
                print('Status_code = 200 all is ok')
            else:
                Sitemap().status_codes_checker(code=_code)
                print('Wrong Domain or need authorization')

        except BaseException as err:
            raise UserError('Error!', err)

        finally:
            r = requests.get(f'https://{args.domain}/')
            _code = r.status_code
            if _code != 200:
                Sitemap().status_codes_checker(code=_code)
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

                # ========
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
