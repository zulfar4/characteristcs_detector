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
#TODO снять ограничения
LIMIT = 1000
# LIMIT = None

def readWordsToExclude():
    
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
def filterExceptions(exceptionWords, listOfWords):
   
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

def split_characteristic(description_text,min_char = 5,max_char= 10):
  
    caracteristic_dict = []
    measureUnits = r"(?:[а-яё/.,]{0,5})"      
    sizePattern =r"[\d]+[.,]?[\d]+[\s]*[-]?[\s]*[\d]*[.,]?[\d]*[\s]?"

    
    while re.search(r"[\n]*[\t]*[\s]*[А-ЯЁ]?[а-яё]+,?:? ?[а-яё]* ?[а-яё]* ?[а-яё]*:?-? ?"+sizePattern, description_text):
        size_find = re.search(r"[\n]*[\t]*[\s]*[А-ЯЁ]?[а-яё]+,?:? ?[а-яё]* ?[а-яё]* ?[а-яё]*:?-? ?"+sizePattern, description_text)

        print(f"Найденное вхождение -> {size_find.group(0)}")
        # print(f"{m.start(0)} {m.end(0)} {m.pos} {m.endpos}\n{m.group(0)}")
        print(f"Все что после нахождения вхождения -> {description_text[size_find.end(0):size_find.end(0)+50]}")
        description_text =  description_text[size_find.end(0):]

        m = re.search(r"(?:[А-ЯЁ]?[а-яё/.,]{4,30})",description_text)
        if m:
            print(f"{m.start(0)} {m.end(0)} {m.pos} {m.endpos} {m.group(0)}")
            # description_text = description_text[m.end(0):]
            find = size_find.group(0)+description_text[0:m.start(0)]
            caracteristic_dict.append(find)
            description_text = description_text[m.start(0):]
            print (f"Полное описание -> {find}")

    if caracteristic_dict:
        return caracteristic_dict

    else:
        return None
 
def main():
    database = "db/pulsecen_30062022.db"

    # create a database connection
    conn = create_connection(database)
    with conn:

        cur = conn.cursor()
        cur.execute(f"SELECT description_product FROM promyshlennoe_oborudovanie limit {LIMIT}" if LIMIT else f"SELECT description_product FROM promyshlennoe_oborudovanie")        
        chunk_size = 1000

        description_texts = []
        characteristics = []
        exceptionWords = readWordsToExclude()
        skippedWords = []
        skip_description=[]
        with open('output/pulsecen/characteristics_pulsecen.json', 'w', encoding='utf-8') as f:
            pass
        with open('output/pulsecen/skipped_words_pulsecen.json', 'w', encoding='utf-8') as f:
            pass

        while True:
            rows = cur.fetchall()
            if not rows:
                break
            else:
                count_rows = len(rows)
                all_row = 0
                pass_row=0
                parsed_row = 0
                # print(f'Общее количество записей {count_rows}')
                for row in rows:
                    # print(f"Обработано {round(all_row/count_rows,2)*100} %")
                    all_row+=1
                    description_text = row[0]
                    if (description_text != "NA" and isinstance(description_text,str) ):
                        m = split_characteristic(description_text=description_text)
                        if m:
                          
                            fltExc = filterExceptions(exceptionWords, m)
            
                            characteristics.append({'id':parsed_row,'rawtext':description_text ,'char':fltExc[0]})
                            parsed_row+=1
                            if (len(fltExc[1])>0):
                              
                                skippedWords.append(fltExc[1])
                
                        else:
                            skip_description.append(description_text)

                            pass_row+=1
                        
                        description_texts.append(description_text)
                        
                    else:
                        
                        pass_row+=1
                        
                        continue
        print(f"Всего строк: {all_row} из них:\nобработано: {parsed_row} {round(parsed_row/all_row,2)*100} %\nпропущено: {pass_row} {round(pass_row/all_row,2)*100} %")                
        with open('output/pulsecen/description_texts_pulsecen.json', 'w', encoding='utf-8') as f:
            json.dump(description_texts, f, ensure_ascii=False, indent=4)
        with open('output/pulsecen/characteristics_pulsecen.json', 'w', encoding='utf-8') as f:
            json.dump(characteristics, f, ensure_ascii=False, indent=4)
        with open('output/pulsecen/skipped_words_pulsecen.json', 'w', encoding='utf-8') as f:
            json.dump(skippedWords, f, ensure_ascii=False, indent=4)
        with open('output/pulsecen/skipped_description.json', 'w', encoding='utf-8') as f:
            json.dump(skip_description, f, ensure_ascii=False, indent=4)
        print('DONE')



if __name__ == '__main__':
    main()