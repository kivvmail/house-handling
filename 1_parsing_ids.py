import requests
import json

address = 'Свердловская область, Екатеринбург, "Бисертская", 16 корпус 4'

# Спарсить краткие данные обо всех объектах (помещениях) по заданному адресу, сохранить данные в "1_all_ids.json"
# Цель - получить список "objectId" для последующего парсинга детальной информации по помещениям по адресу
parameters = {
    "macroRegionId": 165000000000,  # id для 'Свердловская область' из https://rosreestr.gov.ru/api/online/macro_regions
    "regionId": 165401000000,  # id для 'Екатеринбург' из https://rosreestr.ru/api/online/regions/{macroRegionId}
    "settlementId": None,  # id для населенного пункта их https://rosreestr.ru/api/online/regions/{regionId} (проверить)
    "street": "Бисертская",
    "house": 16,  # номер дома, в том числе литерный типа 16а
    "building": 4,  # номер корпуса, если есть
    "apartment": "*",
}
headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/86.0.4240.111 Safari/537.36'}
response = requests.get(url="https://rosreestr.gov.ru/fir_rest/api/fir/address/fir_objects",
                        params=parameters, headers=headers, verify=False)
response.raise_for_status()
all_ids = response.json()

with open("1_all_ids.json", "w", encoding='utf-8') as file:
    json.dump(all_ids, file, ensure_ascii=False, indent=4)
