""" Класс парсера """
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs


class Parser:
    def __init__(self):
        print('Start parse schools')
        self.school_host_find = 'https://russiaedu.ru/_ajax/schools?edu_school_filter%5BschoolName%5D' \
                                '=&edu_school_filter' \
                                '%5Bregion%5D=&edu_school_filter%5Bdistrict%5D=&edu_school_filter%5BformType%5D' \
                                '=&edu_school_filter%5BownershipType%5D=&edu_school_filter%5B_token%5D' \
                                '=Qr2e4n4x9jjqP7gbQTbwMibL3CZnPapd9vIDPOtYeuc&pp=10'
        self.school_host = 'https://www.math-solution.ru/school-reg/'
        self.school_data = {}
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

    def get_exist_school_data(self):
        return pd.read_excel(io='schools_es.xlsx', sheet_name='Школы')

    def get_school_list(self, schools_exists=False):
        if not schools_exists:
            return self.get_all_schools()
        return None

    def get_all_schools(self):
        schools = []
        session = requests.session()
        max_page = 900  # узнал вручную
        for page in range(1, max_page + 1):
            print(f'Обработка школ, страница {page}')
            url = self.school_host_find + f'&pageNumber={page}&direction=&pp=40'
            response = session.get(url)

            if response.status_code == 200:
                schools += json.loads(response.text)['eduSchools']

        if len(schools) <= 0:
            return False
        return schools

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

        with pd.ExcelWriter('schools_es.xlsx') as writer:
            df1.to_excel(writer, sheet_name='Школы')
            df2.to_excel(writer, sheet_name='Университеты')
            print('Запись в Excel завершена!')
