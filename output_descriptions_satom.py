import sqlite3
from sqlite3 import Error

import ast
import re
import json

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def select_necessary_data(conn, column_name, table_name):

    cur = conn.cursor()
    cur.execute(f"SELECT {column_name} FROM {table_name}")

    return cur.fetchall()

LIMIT = 10000
# LIMIT = None
#TODO посмотреть что делает метод
def readWordsToExclude():
    """Получает что? Слова исключения?  почему не передается список"""
    wordsToExclude = []
    with open('output/exceptions.json', 'r', encoding='utf-8') as f:
        approxWords = json.load(f)
    for w in approxWords:
        m = re.match("[\n]*(\D+)", w)
        if m:
            mm = m.group(1)
            # remove last space if any
            mmm = re.match("[\n]*(.*) ", mm)
            if mmm:
                resultWords = mmm.group(1)
            else:
                resultWords = mm
            wordsToExclude.append(resultWords)
    return wordsToExclude
        # print(f"resultWords ({resultWords})")
def get_meausere_Units():
    measureUnits = "[м]*[см]*[m]*[cm]*[кВт]*[л/мин]*[']*[г/м2]*[м2]*[м3]*[%]*"
    measure_List =[]
    
    with open('support\okei.json','r',encoding='utf-8') as f:
        res = json.load(f)
    for r in res:
        # measure_List.append(r['name'])
        measure_List.append(r['shortName'])
        measure_List.append(r['codeName'])
    for m in measure_List:
        measureUnits = f"{measureUnits}[{m}]*"
    return measureUnits

def filterExceptions(exceptionWords, listOfWords):
    """промежуточный метод, который сравнивает два словаря? и пропускает готовый текст в словаре"""
    gatheredWords = []
    skippedWords = []
    for word in listOfWords:
        doGather = True
        for exWord in exceptionWords:
            if exWord in word:
                doGather = False
        if doGather:
            gatheredWords.append(word)
        else:
            skippedWords.append(word)
    return (gatheredWords, skippedWords)


def main():
    database = "db\satom22082022.db"

 

    # create a database connection
    conn = create_connection(database)
    with conn:

        cur = conn.cursor()
        cur.execute(f"SELECT description_product FROM promyshlennoe_oborudovanie_satom limit {LIMIT}" if LIMIT else f"SELECT description_product FROM promyshlennoe_oborudovanie_satom")        
        chunk_size = 1000

        # with open('output/description_texts_satom.json', 'w', encoding='utf-8') as f:
        #     pass
        with open('satom/output/characteristics_satom.json', 'w', encoding='utf-8') as f:
            pass
        with open('satom/output/skipped_words.json', 'w', encoding='utf-8') as f:
            pass


        description_texts = []
        characteristics = [] # too large, isnt it?
        exceptionWords = readWordsToExclude()
        skippedWords = []
        while True:

            rows = cur.fetchmany(chunk_size)
            if not rows:
                break
            else:
                for row in rows:

                    data_dict = ast.literal_eval(row[0])
                    description_text = data_dict['text']

                    if (description_text == "NA"):
                        continue
                    # список едениц измерения. Может, есть смысл, скачать из интернета готовый список и под
                    #гружать его        
                    measureUnits = get_meausere_Units()
                    # value or size: "102х1150x4 cm"
                    sizePattern = "[\d]+[\ ]*[\.]*[\,]*[\ ]*[/]*[\d]* ?[хxXХ]* ?[\d]* ?[хxXХ]* ?[\d]* ?" + measureUnits

                    # # "Количество полок: 4 шт." - перед цифрой не более 3х слов
                    # "Макс. сечение профиля 60 x 30 x 3 мм"
                    # "Ширина 1 000 мм"
                    # m = re.findall("[\n]*[А-ЯЁ]{1}[а-яё]+,?.?:? ?[а-яё]* ?[а-яё]* ?[а-яё]*:?,? ?"+sizePattern+" ?[а-яё]*", description_text)
                    m = re.findall("[\n]*[А-ЯЁ]{1}[а-яё]+,?.?:? ?[а-яё]* ?[а-яё]* ?[а-яё]*:?,? ?"+sizePattern, description_text)
                    # m = re.findall("[\n]*[А-ЯЁ]{1}[а-яё]+,?.?:? ?[а-яё]* ?[а-яё]* ?[а-яё]*:?,? ?", description_text)

                    # "Габаритные размеры, мм: - диаметр чаши 365- высота 520Масса, 6 кг"
                    # Да, но там есть подобные ещё.
                    m2 = re.findall("Габаритные размеры, мм: - диаметр чаши 365- высота 520Масса, 6 кг", description_text)

                    if m2:
                        m = m+m2
    
                    if m:
                        # TODO характеристики по поиску паттерна с добавлением снова 
                        fltExc = filterExceptions(exceptionWords, m)
                        # запись если распознали
                        characteristics.append(fltExc[0])
                        if (len(fltExc[1])>0):
                            # запись если не распознали
                            skippedWords.append(fltExc[1])

                    # description_texts.append(description_text)
    
        # with open('description_texts_satom.json', 'a', encoding='utf-8') as f:
            # json.dump(description_texts, f, ensure_ascii=False, indent=4)
                            #TODO прописать пути
                            
        with open('satom/output/characteristics_satom.json', 'a', encoding='utf-8') as f:
            json.dump(characteristics, f, ensure_ascii=False, indent=4)
        with open('satom/output/skipped_words.json', 'a', encoding='utf-8') as f:
            json.dump(skippedWords, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()