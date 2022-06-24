import json

with open("6_house_plan.json", "r") as file:
    house_plan = json.load(file)

floors_list = []  # Список всех номеров этажей в доме (может не совпадать со списком этажей в отдельном подъезде)
for i in range(len(house_plan)):
    flr = house_plan[i]["plan"]
    floors = []
    for item in flr:
        floors.append(item["floor"])
    floors_list.extend(floors)
floors_list = list(set(floors_list))
min_floor = min(floors_list)
max_floor = max(floors_list)

# Список этажей с квартирами на них, внутри этажа квартиры разделены также и по подъездам
aparts_by_floors = []
for i in range(1, max_floor + 1):
    lst2 = []
    for j in range(len(house_plan)):
        lst1 = []
        for k in range(len(house_plan[j]["plan"])):
            if house_plan[j]["plan"][k]["floor"] == i:
                for n in range(len(house_plan[j]["plan"][k]["apartments_num_and_area"])):
                    lst1.append(house_plan[j]["plan"][k]["apartments_num_and_area"][n][0])
        lst2.append(lst1)
        dct = {
            "floor": i,
            "aparts_at_the_floor": lst2,
        }
    aparts_by_floors.append(dct)

with open("7_aparts_by_floors.json", "w", encoding="utf-8") as file:
    json.dump(aparts_by_floors, file, ensure_ascii=False, indent=4)

# Сделать строковые значения номеров квартир одной длины за счет добавления пробелов и
# выровнять по центру для симметрии при выводе на экран
for item in aparts_by_floors:
    for i in range(len(house_plan)):  # len(house_plan) = количество подъездов
        a = item["aparts_at_the_floor"][i]
        b = [item.center(8) for item in a]
        item["aparts_at_the_floor"][i] = b

# Сцепить номера квартир на этаже и по подъездам в одну строку и добавить символы "|" по краям и между номерами квартир
for item in aparts_by_floors:
    for i in range(len(house_plan)):
        a = item["aparts_at_the_floor"][i]
        b = "|" + "|".join(a) + "|"
        item["aparts_at_the_floor"][i] = b

# Определить максимальную длину сцепленной строки, чтобы строки меньшей длины расширить до максимальной для симметрии
max_length = 0
for item in aparts_by_floors:
    for i in range(len(house_plan)):
        if len(item["aparts_at_the_floor"][i]) > max_length:
            max_length = len(item["aparts_at_the_floor"][i])

# Инвертировать порядок этажей, чтобы на экране этажи с меньшим номером отображались ниже этажей с большим номером
aparts_by_floors.reverse()

# Сформировать итоговые строки для вывода на экран
strings_to_print = []
for i in range(len(aparts_by_floors)):
    string_to_print = ""
    for j in range(len(house_plan)):
        a = aparts_by_floors[i]["aparts_at_the_floor"][j]
        if len(a) < max_length:
            a = a + " " * (max_length - len(a))
        a = a + " " * 10
        string_to_print += a
    strings_to_print.append(string_to_print)

# Вывести на экран результат парсинга и обработки в виде, похожем на "шахматку", для визуальной оценки результата
print('\n')
for i in range(len(strings_to_print)):
    a = str(aparts_by_floors[i]['floor'])
    if len(a) < 2:
        a = " " + a
    print(f"Floor {a}" + " " * 10, strings_to_print[i])

