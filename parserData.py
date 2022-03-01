""" Класс парсера """
import json
import os
import random
import re
import time

import pandas as pd
import urllib.request
import requests
import yandex_search
from fake_useragent import UserAgent
from urllib import parse
import urllib3
from bs4 import BeautifulSoup as bs
from requests import HTTPError


class Parser:
    def __init__(self):
        self.school_host_find = 'https://russiaedu.ru/_ajax/schools?edu_school_filter%5BschoolName%5D' \
                                '=&edu_school_filter' \
                                '%5Bregion%5D=&edu_school_filter%5Bdistrict%5D=&edu_school_filter%5BformType%5D' \
                                '=&edu_school_filter%5BownershipType%5D=&edu_school_filter%5B_token%5D' \
                                '=Qr2e4n4x9jjqP7gbQTbwMibL3CZnPapd9vIDPOtYeuc&pp=10'
        self.school_host = 'https://www.math-solution.ru/school-reg/'
        self.school_data = {}
        self.proxies = ["203.34.28.75:80", "45.8.104.116:80", "203.24.102.165:80", "203.24.102.130:80",
                        "203.28.8.43:80", "203.24.102.122:80", "45.12.31.153:80", "203.34.28.55:80", "91.243.35.182:80",
                        "172.67.3.114:80", "203.24.108.24:80", "203.34.28.120:80", "203.24.108.191:80",
                        "203.30.189.247:80", "203.24.102.244:80", "203.32.120.191:80", "185.162.231.69:80",
                        "203.28.8.253:80", "45.14.173.22:80", "203.28.9.144:80", "45.8.107.178:80", "203.32.121.239:80",
                        "203.32.121.124:80", "203.30.188.235:80", "203.28.9.176:80", "185.162.229.124:80",
                        "185.162.230.47:80", "91.226.97.206:80", "185.171.230.40:80", "203.30.188.191:80",
                        "203.23.106.178:80", "203.13.32.50:80", "203.30.191.34:80", "203.30.190.198:80",
                        "91.243.35.27:80", "199.60.103.234:80", "185.162.229.210:80", "45.8.105.80:80",
                        "172.67.180.10:80", "185.162.231.183:80", "203.23.103.208:80", "203.23.106.137:80",
                        "185.162.228.188:80", "203.13.32.16:80", "45.12.31.224:80", "203.34.28.97:80",
                        "203.30.191.45:80", "199.60.103.21:80", "45.8.107.52:80", "45.12.31.168:80", "203.32.120.93:80",
                        "45.8.104.11:80", "199.60.103.189:80", "185.162.231.30:80", "203.22.223.207:80",
                        "203.13.32.47:80", "91.226.97.144:80", "185.162.231.62:80", "203.23.103.75:80",
                        "203.23.104.54:80", "203.23.104.155:80", "203.32.121.87:80", "203.32.120.132:80",
                        "203.22.223.40:80"]
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': UserAgent().random
        }
        self.es_host = 'https://vuzopedia.ru'

    # Возвращается код страницы
    def get_html(self, url=''):
        if url == '':
            return False

        res = requests.get(url)

        if res.status_code == 200:
            return res.content
        else:
            return False

    def find_all_school_emails_test(self):
        print('Find all schools emails!')
        # df = pd.read_excel(io='schools_es.xlsx', sheet_name='Школы').to_json(orient="records")

        with open('school.json', 'r', encoding='utf-8') as file:
            # json.dump(json.loads(df), file, ensure_ascii=False, indent=4)
            schools = json.loads(file.read())

        ya_host = 'http://yandex.ru/search?text='
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-en,ru;q=0.8,en-us;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'cache-control': 'max-age=0',
            'device-memory': '4',
            'dnt': '1',
            'downlink': '3.6',
            'dpr': '1.375',
            'ect': '4g',
            'rtt': '50',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Yandex";v="22"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'serp-rendering-experiment': 'snippet-with-header',
            'upgrade-insecure-requests': '1',
        }
        replace_pares = {}  # Объект замены данных после поиска всех почт
        yandex = yandex_search.Yandex(api_user='ovildmy', api_key='03.473923288:bd8ccf51bfdbdd166845a340d3a21afb')
        iteration = 1  # итерация для отслеживания прогресса
        # http = urllib3.PoolManager()

        res = requests.get('https://yandex.ru/search/xml?action=limits-info&user=ovildmy' \
                           '&key=03.473923288:bd8ccf51bfdbdd166845a340d3a21afb')
        # print(f'YA res: {}')
        for school in schools:
            iteration += 1
            if not school['E-mail']:
                with open('all_school_names.txt', 'a', encoding='utf-8') as file:
                    file.write('\n' + school['Название'])
                continue
                print(f'Progress: {(iteration / len(schools)) * 100} %')
                school_name = school['Название']
                url_name = '+'.join(school_name.split())
                url = ya_host + url_name
                params = {
                    'text': url_name
                }
                headers['user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)' \
                                        ' Chrome/96.0.4664.174 YaBrowser/22.1.3.850 Yowser/2.5 Safari/537.36'

                # UserAgent().random
                y_url = 'https://yandex.ru/search/xml?user=ovildmy&key=03.473923288:bd8ccf51bfdbdd166845a340d3a21afb' \
                        '&query=' + url_name
                print(f'Get item: {y_url}')
                # proxy = 'http://' + self.proxies[random.randint(0, len(self.proxies) - 1)]
                # response = requests.get(url, proxies={'https': proxy}, headers=headers)  # , params=params)
                # yitems = yandex.search(school_name).items
                response = requests.get(y_url)

                # Поиск страницы школы в Яндекс
                if response.ok:
                    print('page is ok')
                    print(response.text)
                    break
                    # html = bs(response.text, 'html.parser')
                    # print(f'max len of select <a>: {len(html.select("a.path__item"))}')
                    # a_tags = html.select('a.path__item')

                    # if len(a_tags) <= 0:
                    #     with open('ya.html', 'w', encoding='utf-8') as file:
                    #         file.write(response.text)
                    # time.sleep(3)
                    # print('[BREAK]...')
                    # continue
                    # break
                    school_site = yitems[0]['url']  # a_tags[0].get('href')
                    print(f'school_site: {school_site}')

                    # Переход на сайт и поиск в нём всех почт
                    print(f'Get URL: {school_site}')
                    try:
                        school_response = requests.get(school_site, headers=headers)
                        if school_response.status_code == 200:
                            # school_html = bs(school_response.text, 'html.parser')

                            replace_pares[school_name] = self.find_emails_on_page(school_response.text)
                        else:
                            print(f'School site doesn`t work: {school_site}')
                    except HTTPError as http_err:
                        print(f'HTTP error occurred: {http_err}')  # Python 3.6
                    except Exception as err:
                        print(f'Other error occurred: {err}')  # Python 3.6
                else:
                    print(f'URL HAS ERROR: {url}')

        print(f'Итого: {iteration}')
        print('Замена данных в эксель файле')
        for pare_key in replace_pares.keys():
            for school in schools:
                if " ".join(school['Название'].split()) == " ".join(pare_key.split()):
                    print(f'Replace email in {pare_key} -> {replace_pares[pare_key]}')
                    school['E-mail'] = replace_pares[pare_key]

        with open('school.json', 'w', encoding='utf-8') as file:
            json.dump(schools, file, indent=4, ensure_ascii=False)

    def find_emails_on_page(self, email_txt):
        found_emails = list(set([x[0] for x in re.findall(r'(\w*@\w*\.\w*(\.\w*)?)', email_txt)]))
        found_emails = ', '.join(found_emails)
        # print(found_emails)
        return found_emails

    def get_exist_school_data(self):
        assert os.path.isfile('schools_es.xlsx'), 'Не существует готового файла со школами и вузами!'
        return pd.read_excel(io='schools_es.xlsx', sheet_name='Школы')

    def save_school_data(self):
        with open('new_school_data.json', 'w', encoding='utf-8') as file:
            sch = self.get_all_schools()
            json.dump(sch, file, indent=4, ensure_ascii=False)

    def get_all_schools(self):
        schools = []
        session = requests.session()
        all_schools_emails = []
        response = session.get('https://russiaschools.ru/')
        response.encoding = response.apparent_encoding

        if response.ok:
            html = bs(response.text, 'html.parser')

            # Проход по регионам
            for li in html.select('li[itemprop=name]'):
                region_response = session.get(li.find('a').get('href'), headers=self.headers)
                region_response.encoding = region_response.apparent_encoding

                print(f'[REGION]: {li.find("a").text}')

                if region_response.ok:
                    # Проход по городам в регионе
                    for city in bs(region_response.text, 'html.parser').select('div.contents a'):
                        city.encoding = city.apparent_encoding

                        print(f'[CITY]: {city.text}')
                        # Просмотр города или его областей
                        city_response = session.get(city.get('href'))
                        city_response.encoding = city_response.apparent_encoding

                        if city_response.ok:
                            school_adding_data = {
                                'city': city.text
                            }

                            if city.text == 'г. Москва':
                                # Если в городе есть округа
                                print('{CITY HAS DISTRICT}')
                                for district in bs(city_response.text, 'html.parser').select('div.contents a'):
                                    district_response = session.get(district.get('href'), headers=self.headers)
                                    district_response.encoding = district_response.apparent_encoding

                                    if district_response.ok:
                                        # выборка школ
                                        print(f'[WRITE SCHOOLS]: district')

                                        school_adding_data['district'] = district.text
                                        all_schools_emails += self.get_schools_from_page(district_response.content,
                                                                                         school_adding_data)

                                        # all_schools_emails.append(school_adding_data)
                            else:
                                # Выборка школ
                                print(f'[WRITE SCHOOLS]: city')
                                # self.get_schools_from_page(city_response.content)
                                all_schools_emails += self.get_schools_from_page(city_response.content,
                                                                                 school_adding_data)

                            # all_schools_emails.append(data)
        return all_schools_emails

    def get_schools_from_page(self, site_txt, adding_data):
        # if os.path.exists('new_school_data.json'):
        #     with open('new_school_data.json', 'r') as file:
        #         # print(f'file: {file.read()}')
        #         if file.read().strip() == '':
        #             exists_school = []
        #         else:
        #             exists_school = json.loads(file.read())
        # else:
        #     exists_school = []
        result = []

        for school in bs(site_txt, 'html.parser').select('div.contents table a'):
            school_data = {
                'name': school.text,
                'url': school.get('href')
            }
            school_data.update(adding_data)
            # print(f'[SCHOOL DATA]: {school_data}')
            result.append(school_data)

        return result

        # with open('new_school_data.json', 'w', encoding='utf-8') as file:
        #     json.dump(exists_school, file, indent=4, ensure_ascii=False)

    def get_schools_emails_from_page(self):
        with open('new_school_data.json', 'r', encoding='utf-8') as file:
            schools = json.loads(file.read())
        unsuccessed_urls = []
        iteration = 1
        for school in schools:
            print(f'[PROGRESS]: {(iteration / len(schools)) * 100}%')
            iteration += 1
            try:
                response = requests.get(school['url'], headers=self.headers)
                response.encoding = response.apparent_encoding
                if response.ok:
                    school['emails'] = self.find_emails_on_page(response.text)
            except:
                print(f'[ERR]: {school["url"]}')
                unsuccessed_urls.append(school['url'])

        with open('result_school_data.json', 'w', encoding='utf-8') as file:
            json.dump(schools, file, indent=4, ensure_ascii=False)

    def get_es_list(self, json_exists=False):
        if json_exists:
            file = json.loads(open('es_data.json', encoding='utf-8').read())
            return file
        else:
            links = self.get_es_links()
            es_data = self.get_es_data(links)
            return es_data

    def get_es_data(self, links):
        if not links:
            return False
        all_es_data = []
        session = requests.session()
        es_iteration = 1
        for es_link in links:
            response = session.get(es_link)

            if response.status_code == 200:
                print(f'Обработка ВУЗа: {str((es_iteration / len(links)) * 100)}%')
                html = bs(response.text, 'html.parser')
                es_data = {
                    'es_name': html.find('h1', class_='mainTitle fc-white').text.replace('\n', '')
                        .replace('', '').strip(),
                    'es_email': [],
                    'es_phone': []
                }
                for p_data in html.select('div.col-lg-12.col-md-12.col-xs-12.col-sm-12'):
                    p_value = p_data.find('div', class_='col-lg-8 col-md-8 col-xs-8 col-sm-8').text
                    if 'телефон' in p_data.text.lower():
                        es_data['es_phone'].append(p_value)
                    elif 'email' in p_data.text.lower():
                        es_data['es_email'].append(p_value)
                    elif 'сайт' in p_data.text.lower():
                        es_data['es_site'] = p_value

                es_data['es_email'] = ', '.join(es_data['es_email'])  # Соединение всех найденных почт
                es_data['es_phone'] = ', '.join(es_data['es_phone'])  # Соединение всех найденных телефонов

                all_es_data.append(es_data)
            else:
                print(f'Проблемы со страницей {es_link}')
            es_iteration += 1

        with open('es_data.json', 'w', encoding='utf-8') as file:
            json.dump(all_es_data, file, ensure_ascii=False, indent=4)

        return all_es_data

    def get_es_links(self):
        urls = [
            {
                'url': 'https://vuzopedia.ru/vuz?s=psihologicheskie',
                'max_page': 16
            },
            {
                'url': 'https://vuzopedia.ru/vuz?s=pedagogicheskie',
                'max_page': 16
            }
        ]
        print('Start ES parsing')
        es_links = []  # Ссылки на все страницы вузов, чтобы собрать подробную инф-ию

        for es_data in urls:
            for page in range(1, es_data['max_page'] + 1):
                url = es_data['url'] + '&page=' + str(page)
                print(f'Взятие ссылок ВУЗов. {page} страница. УРЛ: {url}')
                response = requests.post(url)

                if response.status_code == 200:
                    html = bs(response.text, 'html.parser')
                    for es_div in html.find_all('div', class_='col-md-12 itemVuz'):
                        new_link = self.es_host + es_div.find('a').get('href')
                        if new_link not in es_links:  # добавить ссылку на вуз, если её нет в выборке
                            es_links.append(new_link)
                else:
                    return False

        return es_links

    def to_excel(self, schools, ess):
        print('Запись в Excel!')

        # Обработка школ
        if schools:
            schools_data = []
            for sch in schools:
                sch_item = [sch['data']['title'], sch['data']['address'], sch['data']['director'], sch['data']['email'],
                            sch['data']['phone'], sch['data']['site']]
                schools_data.append(sch_item)
            df1 = pd.DataFrame(schools_data, columns=['Название', 'Адрес', 'Директор', 'E-mail', 'Телефон', 'Сайт'])
        else:
            df1 = self.get_exist_school_data()

        # Обработка ВУЗов
        ess_data = []
        for es in ess:
            es_item = [es['es_name'], es['es_email'], es['es_phone']]
            ess_data.append(es_item)
        df2 = pd.DataFrame(ess_data, columns=['Название', 'Почта', 'Телефон'])

        assert df1 and df2  # Проверка на правильное существование переменных

        with pd.ExcelWriter('schools_es.xlsx') as writer:
            df1.to_excel(writer, sheet_name='Школы')
            df2.to_excel(writer, sheet_name='Университеты')
            print('Запись в Excel завершена!')
