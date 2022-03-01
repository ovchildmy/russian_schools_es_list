""" Парсер школ и вузов Москвы """

from parserData import Parser

if __name__ == '__main__':
    parser = Parser()
    # schools = parser.get_school_list(schools_exists=True)
    # ess = parser.get_es_list(json_exists=True)
    # parser.to_excel(schools, ess)
    # parser.save_school_data()
    parser.get_schools_emails_from_page()