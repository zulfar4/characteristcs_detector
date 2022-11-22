
import json
import re

def extract_result(characteristic_line):
    measureUnits = "([м]*[см]*[m]*[cm]*[кВт]*[л/мин]*[']*[г/м2]*[м2]*[м3]*[%]*)"
    sizePattern = "([\d]+[\ ]*[\.]*[\,]*[\ ]*[/]*[\d]* ?[хxXХ]* ?[\d]* ?[хxXХ]* ?[\d]*) ?" + measureUnits
    m = re.match("([\n]*[А-ЯЁ]{1}[а-яё]+,?.?:? ?[а-яё]* ?[а-яё]* ?[а-яё]*):?,? ?"+sizePattern, characteristic_line)

    if not m:
        return []
    (name, value, measure) = ("", "", "")

    if m.group(1):
        name = m.group(1)
        name = re.findall(r"[А-ЯЁ]{1}[а-яё]+[а-яё]* ?[а-яё]* ?[а-яё]*",name)
        name = name[0].strip()
    if m.group(2):
        value = m.group(2)
    if m.group(3):
        measure = m.group(3)

    return {'name':name,'value':value,'measure':measure}
    # return (name, value, measure)

def main():
    
    raw_characteristics = []
    with open("satom/output/characteristics_satom.json", 'r', encoding='utf-8') as f:
        raw_characteristics = json.load(f)
    
    target_extracted_results = []
    for raw_characteristic in raw_characteristics:
        extracted_results = []
        for characteristic in raw_characteristic:
            extracted_results.append(extract_result(characteristic))
        target_extracted_results.append(extracted_results)

    with open('satom/output/target_extracted_results.json', 'w', encoding='utf-8') as f:
                    json.dump(target_extracted_results, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()