
import json
import re
import itertools
from tabulate import tabulate
def get_meausere_Units():
    """добавление единиц измерения из словаря"""
    measureUnits = "[м]*[см]*[m]*[cm]*[кВт]*[л/мин]*[']*[г/м2]*[м2]*[м3]*[%]*[mm]*[мм]*"
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

def extract_result(characteristic_line):
    # mUnits = "[м]*[см]*[m]*[cm]*[кВт]*[л/мин]*[']*[г/м2]*[м2]*[м3]*[%]*"
    # mUnits = r"\b(см|mm|мм|Вт|кг)\b"
    mUnits = r"\b(%|см|мм|л/мин|литров|м|л|кг|мг/л|атм)"
    measureUnits = f"({get_meausere_Units()})"
    # sizePattern = "([\d]+[\ ]*[\.]*[\,]*[\ ]*[/]*[\d]* ?[хxXХ]* ?[\d]* ?[хxXХ]* ?[\d]*) ?" + measureUnits
    sizePattern = "([\d]+[.,]?[\d]+[\s]*[-]?[\s]*[\d]*[.,]?[\d]*)"+measureUnits
    m = re.match("([\n]*[\s]*[А-ЯЁ]?[а-яё]+,?.?:? ?[а-яё]* ?[а-яё]* ?[а-яё]*):?,? ?"+sizePattern, characteristic_line)

    if not m:
        return []
    (name, value, measure) = ("", "", "")

    if m.group(1):
        name = m.group(1)

        if re.findall(mUnits,name):
            split_name = re.split(mUnits,name)
            name = split_name[0]
            measure = split_name[1]
            # print(tabulate([[name, measure]],tablefmt="textile"))
            print(f"{name}{measure}")


        name = re.search("[А-ЯЁ]*[а-яё].*[^\s^,^:^;]",name)
        # name = re.search("\w*",name)
        if name:
           name = name.group(0)
        else:
            name=""
    if m.group(2):
        value = m.group(2)
        if value:
            value = re.match(r".*[^\s^.^,]",value)
            value = value.group(0)
        else:
            value = ''
    if m.group(3):
        
    
        m_g = m.group(3)
        if m_g != "":
            measure = m_g
        else:
            pass
        # if measure!="":
        #     pass
        # else:
        #     measure = m_g
    return {'name':name,'value':value,'measure':measure}
   

def main():
    # data_json = 'satom'
    # data_json = 'avito'
    data_json = 'pulsecen'
    path_input = f"output/{data_json}/characteristics_{data_json}.json"
    path_output = f"output/{data_json}/target_extracted_results_{data_json}.json"
    with open(path_output, 'w', encoding='utf-8') as f:
        pass
    
    raw_characteristics = []
    with open(path_input, 'r', encoding='utf-8') as f:
        raw_characteristics = json.load(f)
    
    target_extracted_results = []

   
    # for raw_dict in itertools.islice(raw_characteristics,500):
    print(len(raw_characteristics))
    for raw_dict in itertools.islice(raw_characteristics,500):
        extracted_results = []
        for raw_string in raw_dict['char']:
        
            # for raw_characteristic in raw_string:
          
            extracted_results.append(extract_result(raw_string))
        target_extracted_results.append({'id':raw_dict['id'],'raw_text':raw_dict['rawtext'],'char':extracted_results})
        
    print(f"Размер массива {data_json} --> {len(target_extracted_results)}")
    with open(path_output, 'w', encoding='utf-8') as f_dump:
        json.dump(target_extracted_results, f_dump, ensure_ascii=False, indent=4)
    print('done')


if __name__ == '__main__':
    main()