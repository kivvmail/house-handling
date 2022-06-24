import requests
import json
import time
import random

with open("1_all_ids.json", "r") as file:
    all_ids = json.load(file)

list_ids = [item["objectId"] for item in all_ids if len(item["objectId"]) > 12] # отсеять устаревшие короткие id

# Спарсить детальные данные для каждого объекта по "objectId" из list_ids с сайта Росреестра
# Парсинг всего списка или пакетами по 50 запросов с паузой между пакетами 4-5 минут:
# срабатывает или тот или другой способ, но больше похоже на нестабильность работы сайта росреестра,
# чем на лимиты для одного ip. При обоих способах может потребоваться перезапуск парсинга при неудаче.
# Ночью стабильнее. В крайнем случае можно парсить пакетами и сохранять результат в промежуточный файл,
# с последующим объединением успешно спарсенных пакетов.
details = []
for i in range(len(list_ids)):
    headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/86.0.4240.111 Safari/537.36'}
    response = requests.get(
        url="https://rosreestr.gov.ru/fir_rest/api/fir/fir_object/%s" % list_ids[i],
        headers=headers, verify=False)
    response.raise_for_status()
    _ = response.json()
    details.append(_)
    # Если парсить пакетами по 50 запросов:
    # if i % 50 == 0 and i != 0:
    #     time.sleep(random.randint(240, 300))

with open("2_raw_details.json", "w", encoding='utf-8') as file:
    json.dump(details, file, ensure_ascii=False, indent=4)
