import json

MAX_APARTS_AT_FLOOR = 10  # заведомо большое (нереальное) количество квартир на этаже в подъезде
DEVIATION = 15  # 15 м2 - допустимое отклонение площади этажей из предположения, что квартиры с < 15 м2 маловероятны

# Лист отсортированных данных по квартирам:
with open("4_final_details_sorted.json", "r") as file:
    sorted_aparts = json.load(file)

# Лист исходных спарсенных данных по квартирам:
with open("2_raw_details.json", "r") as file:
    raw_details = json.load(file)

# Лист унифицированных номеров квартир из sorted_aparts:
aparts_list = [item["num_to_sort"] for item in sorted_aparts]

# Преобразовать унифицированные номера квартир в числовые значения:
apart_numbers = []
for item in aparts_list:
    num = item.lstrip('0')
    num = num.rstrip('aаx')  # Одна "а" - латиница, другая - кириллица
    apart_numbers.append(int(num))

# Наибольший номер квартиры в доме:
max_apart_numbers = max(apart_numbers)

# Вычислить недостающие / пропущенные номера квартир в доме:
# # Список недостающих номеров квартир:
missing_numbers = []
for apart in range(1, max_apart_numbers + 1):
    if apart not in apart_numbers:
        missing_numbers.append(apart)
missing_numbers = [str(item) for item in missing_numbers]

# # Список унифицированных недостающих номеров квартир:
list_num_to_sort = []
for item in missing_numbers:
    num_to_sort = str(item)
    while len(num_to_sort) < 4:
        num_to_sort = '0' + num_to_sort
    list_num_to_sort.append(num_to_sort)

# # Удалить расчетный пропущеный номер квартиры, если он является частью сдвоенной квартиры (num_to_sort с "х" на конце)
for item in list_num_to_sort:
    apart = int(item.lstrip("0"))
    previous_apart = str(apart - 1)
    while len(previous_apart) < 4:
        previous_apart = "0" + previous_apart
    previous_apart = previous_apart + "x"
    for i in range(len(sorted_aparts)):
        if previous_apart == sorted_aparts[i]["num_to_sort"]:
            list_num_to_sort.remove(item)

# Добавить недостающие квартиры в общий список с пустыми полями:
# # Найти данные по пропущеным номерам в "2_raw_details.json" и добавить их в записи для недостающих квартир
for item in list_num_to_sort:
    apart = item.lstrip("0")
    missing_apart = {
        "objectId": "unknown",
        "addressNote": "",
        "apartment": apart,
        "areaValue": 0,
        "premisesFloor": "",
        "num_to_sort": item,
        "data_calculated": 1,
    }
    sorted_aparts.append(missing_apart)

    for i in range(len(raw_details)):
        if raw_details[i].get("objectData").get("objectAddress").get("apartment") == apart:
            if raw_details[i]["objectData"]["removed"] != 1:
                sorted_aparts.remove(missing_apart)
                missing_apart = {
                    "objectId": raw_details[i].get("objectId", "unknown"),
                    "addressNote": raw_details[i].get("objectData").get("objectAddress").get("addressNotes", ""),
                    "apartment": apart,
                    "areaValue": raw_details[i].get("premisesData").get("areaValue", 0),
                    "premisesFloor": raw_details[i].get("premisesData").get("premisesFloor", ""),
                    "num_to_sort": item,
                    "data_calculated": 1,
                }
                sorted_aparts.append(missing_apart)

            

# Отсортировать после добавления записей для недостающих квартир:
all_apartments_restored = sorted(sorted_aparts, key=lambda x: x["num_to_sort"])

# Восстановить отсутствующие номера этажей по значениям для этажей у предшествующей и следующей квартир.
# Если квартира находится между квартирами на разных этажах, значению этажа присвоить среднее между этажами
# для послежующего уточнения. Если квартира может быть в разных подъездах (или последняя в предыдущем подъезде
# или первая в следующем), установить значение этажа = 1000 для последующего уточнения. Значение 1000,
# чтобы не ломать алгоритм разбивки на подъезды, и заведомо нереальное, чтобы можно было обработать и уточнить

# # Список num_to_sort с отсутствующим номером этажа:
missing_floors = []
for item in all_apartments_restored:
    if item["premisesFloor"] == "":
        missing_floors.append(item["num_to_sort"])

# # Лист уникальных значений этажей в доме:
floors_list = [item["premisesFloor"] for item in all_apartments_restored if item["premisesFloor"] != ""]
floors_list = sorted(list(set(floors_list)))

# # Рассчитать значения для отсутствующих "premisesFloor" (работает при условии, что нет двух квартир подряд
# # с пустыми значениями для "premisesFloor"
if missing_floors:
    for item in missing_floors:
        for i in range(1, len(all_apartments_restored) - 1):
            current_apart = all_apartments_restored[i]
            previous_apart = all_apartments_restored[i - 1]
            next_apart = all_apartments_restored[i + 1]
            if current_apart["num_to_sort"] == item:
                if previous_apart["premisesFloor"] == next_apart["premisesFloor"]:
                    current_apart["premisesFloor"] = previous_apart["premisesFloor"]
                elif previous_apart["premisesFloor"] == next_apart["premisesFloor"] - 1:
                    current_apart["premisesFloor"] = previous_apart["premisesFloor"] + 0.5
                else:
                    current_apart["premisesFloor"] = 1000
                current_apart["data_calculated"] = 1

# Исправить возможные ошибки в спарсенных значениях этажей, когда номер этажа текущей квартиры не совпадает
# с номером этажей предшествующей и следующей квартирой, которые обе имеют одинаковый номер этажа:
for i in range(1, len(all_apartments_restored) - 1):
    current_apart = all_apartments_restored[i]
    previous_apart = all_apartments_restored[i - 1]
    next_apart = all_apartments_restored[i + 1]
    if previous_apart["premisesFloor"] == next_apart["premisesFloor"] + 1 \
            and current_apart["premisesFloor"] != previous_apart["premisesFloor"]:
        current_apart["premisesFloor"] = previous_apart["premisesFloor"]
        current_apart["data_calculated"] = 1

# Попробовать скорректировать вычисленные значения этажей типа 8.5 (квартиры на границах этажей)
# # Лист значений этажей после корректировок:
floors_list_2 = [item["premisesFloor"] for item in all_apartments_restored]
floors_list_2 = sorted(list(set(floors_list_2)))  # В отличие от floors_list может содержать этажи типа 8.5 и 1000

# # Лист некорректных значений этажей (как этажи, которые есть в floors_list_2 и которых нет в floors_list)
wrong_floors = list(set(floors_list_2).difference(set(floors_list)))

# # Список индексов в all_apartments_restored квартир с некорректными значениями этажей
apart_indexes = []
for item in wrong_floors:
    for i in range(len(all_apartments_restored)):
        if all_apartments_restored[i]["premisesFloor"] == item:
            apart_indexes.append(i)

# # Скорректировать значения этажей для квартир из apart_indexes из условия равенства площади соседних этажей:
for item in apart_indexes:
    if all_apartments_restored[item]["premisesFloor"] != 1000:  # Обработка для этажей со значениями 3.5, 6.5 и т.д.
        previous_floor = all_apartments_restored[item - 1]["premisesFloor"]
        next_floor = previous_floor + 1
        all_apartments_restored[item]["premisesFloor"] = previous_floor
        j = 1
        previous_area = all_apartments_restored[item]["areaValue"]  # Прибавляем площадь симметрично вверх и вниз по индексу
        next_area = all_apartments_restored[item + 1]["areaValue"]
        while j < MAX_APARTS_AT_FLOOR:
            if all_apartments_restored[item - j]["premisesFloor"] == previous_floor:
                previous_area += all_apartments_restored[item - j]["areaValue"]
            else:
                break
            if all_apartments_restored[item + j + 1]["premisesFloor"] == next_floor:
                next_area += all_apartments_restored[item + j + 1]["areaValue"]
            j += 1
        if abs(previous_area - next_area) < DEVIATION:
            pass  # То есть назначение all_apartments_restored[item]["premisesFloor"] = previous_floor верно.
        else: # Переносим квартиру на следующий этаж. Верно, если не попались квартиры с площадью 0.
            all_apartments_restored[item]["premisesFloor"] = next_floor
    else:  # Обработка для этажей со значениями 1000
        previous_floor = all_apartments_restored[item - 1]["premisesFloor"]
        pre_previous_floor = previous_floor - 1
        all_apartments_restored[item]["premisesFloor"] = previous_floor
        j = 0
        start1 = item
        start2 = item
        previous_area = 0
        pre_previous_area = 0
        while j < MAX_APARTS_AT_FLOOR * 2:
            j += 1
            if all_apartments_restored[item - j]["premisesFloor"] == previous_floor:
                start1 += -1
                start2 += -1
            if all_apartments_restored[item - j]["premisesFloor"] == pre_previous_floor:
                start2 += -1
            if all_apartments_restored[item - j]["premisesFloor"] == pre_previous_floor - 1:
                break
        for k in range(start1, item + 1):
            previous_area += all_apartments_restored[k]["areaValue"]
        for n in range(start2, start1):
            pre_previous_area += all_apartments_restored[n]["areaValue"]
        if abs(previous_area - pre_previous_area) < DEVIATION:
            pass  # То есть назначение all_apartments_restored[item]["premisesFloor"] = previous_floor верно.
        else:  # Переносим квартиру в следующий подъезд на нижний этаж. Верно, если не попались квартиры с площадью 0.
            all_apartments_restored[item]["premisesFloor"] = all_apartments_restored[item + 1]["premisesFloor"]

with open('5_all_apartments_restored.json', 'w', encoding='utf-8') as file:
    json.dump(all_apartments_restored, file, ensure_ascii=False, indent=4)
