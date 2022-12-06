import json
import csv
import os
import pymorphy2

file_to_fix_results='characteristics_core.csv'
file_to_fix_cores='core_universe.csv'

stop_words=['и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со',
'как', 'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к',
'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 'вот',
'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже',
'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него',
'до', 'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там', 'потом',
'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где', 'есть', 'надо',
'ней', 'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без',
'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда',
'кто', 'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним',
'здесь', 'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее',
'сейчас', 'были', 'куда', 'зачем', 'всех', 'никогда', 'можно', 'при',
'наконец', 'два', 'об', 'другой', 'хоть', 'после', 'над', 'больше',
'тот', 'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много',
'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой',
'перед', 'иногда', 'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им',
'более', 'всегда', 'конечно', 'всю', 'между']

morph = pymorphy2.MorphAnalyzer() #Работаем с модулем русского языка

count=0
count_core=0

core_universe=[]

with open("output/target_extracted_results.json", encoding='utf-8') as file:
    charac_a = json.load(file)
    char =[]
    
    for ch in charac_a:
        for c in ch:
            # print(c['name'])
            if 'name' in c and c['name'] != "":
                char.append(c['name'])
    charac_a.clear()
    charac_a = char    
    


for phrase in charac_a:
    core=False          #Суть
    sub_core=False      #Уточнение

    #Токенизируем фразу
    """
    from nltk.tokenize import sent_tokenize, word_tokenize
    text = phrase

    tokens=word_tokenize(text, language="russian")
    """

    tokens=phrase.split()

    #Исключаем стоп-слова
    """
    from nltk.corpus import stopwords
    stopwords.words("russian")
    """

    filtered_tokens=[]
    for token in tokens:
        if token not in stop_words:
            filtered_tokens.append(token)


    for token in filtered_tokens:
        #Определяем лингвистические параметры слова
        word=morph.parse(token)[0]
        normal_form=0
       
        #Определяем главную суть
        if not core:
            #Ищем первое имя существительно в именительном падеже
            if word.tag.POS=='NOUN' and word.tag.case=='nomn':
                normal_form=word.normal_form
                core=normal_form #Фиксируем суть

                #Отдельно фиксируем уникальные core
                if not(core in core_universe):
                    core_universe.append(core)

                    if count_core==0:
                        file_status=open(file_to_fix_cores, mode='w')
                        file_writer = csv.writer(file_status, delimiter = ';', lineterminator='\r')
                        file_writer.writerow(['core', 'phrase'])
                        file_status.close()
                    
                    file_status=open(file_to_fix_cores, mode='a')
                    file_writer = csv.writer(file_status, delimiter = ';', lineterminator='\r')
                    try:
                        file_writer.writerow([core, phrase])
                    except:
                        pass
                    file_status.close()

                    count_core+=1

        #Определяем уточнение
        sub_core_trigger=False #Флаг нахождения sub_core
        #Если до core, то прилагательное или причастие
        if (not sub_core and not core):
            if word.tag.POS=='ADJF' or word.tag.POS=='PRTF': #Прилагательное или причастие
                sub_core_trigger=True
        #Если после core, то существительное
        elif (not sub_core and core and core!=normal_form):
            if word.tag.POS=='NOUN':
                sub_core_trigger=True

        if sub_core_trigger:                
            sub_core=word.normal_form #Фиксируем суть                
            
            #Находим стемму уточнения
            from nltk.stem import SnowballStemmer

            snowball = SnowballStemmer(language="russian")
            sub_core=snowball.stem(sub_core)

    #Вывод результата
    print(count, core, sub_core)

    if count==0:
        file_status=open(file_to_fix_results, mode='w')
        file_writer = csv.writer(file_status, delimiter = ';', lineterminator='\r')
        file_writer.writerow(['core', 'sub_core', 'phrase'])
        file_status.close()
    
    file_status=open(file_to_fix_results, mode='a')
    file_writer = csv.writer(file_status, delimiter = ';', lineterminator='\r')
    try:
        file_writer.writerow([core, sub_core, phrase])
    except:
        pass        
    file_status.close()

    count+=1

    if 2==1 and count>20:
        os._exit(0)

print (f'Обработанно {count} характеристик. Найдено {count_core} уникальных.')

