import json

DEVIATION = 15 # 15 м2 - допустимое отклонение площади этажей из предположения, что квартиры с < 15 м2 маловероятны


def floors_average_area(entrance):
    """Вычисляет среднее значение площади квартир на этажах в подъезде. Принимает список
    данных для всех квартир в подъезде. Возвращает среднее значение площади этажей."""

    # Какие номера этажей есть в подъезде, список уникальных номеров этажей:
    floors_set_as_list = list(set([item["premisesFloor"] for item in entrance]))

    # Список площадей этажей из floors_set_as_list:
    floors_area_list = []
    for i in range(len(floors_set_as_list)):
        floor_area = 0
        for j in range(len(entrance)):
            if entrance[j]["premisesFloor"] == floors_set_as_list[i]:
                floor_area += entrance[j]["areaValue"]
        floor_area = round(floor_area)
        floors_area_list.append(floor_area)

    # Среднее значение площади этажа в подъезде:
    average_area = int(sum(floors_area_list) / len(floors_area_list))
    return average_area


def check_wrong_floors(apartments_by_entrances):
    """Проверяет правильность распределения квартир по этажам в подъезде из условия, что площадь этажа
    должна быть равна средней площади этажей по подъезду (при допущении, что все этажи в подъезде имеют равную
    площадь, то есть подъезды с секциями этажей разной площади вне области определения данной функции).
    Принимает в качестве аргумента список квартир, распределенных по подъездам. Возвращает словарь с номерами подъездов
    и номерами ошибочных этажей в этих подъездах. Список этажей содержит как минимум два ошибочных этажа, так как
    предполагается, что отклонение связано с ошибочным распределением квартир между двумя соседними этажами.
    Этаж с номером 1 исключается из рассмотрения, так как первые этажи с другим количеством квартир на этаже
    и с другой суммарной площадью квартир - частый случай, а не ошибка."""
    wrong_floors_list = []
    for n in range(len(apartments_by_entrances)):
        entrance = apartments_by_entrances[n]  # Подъезд дома
        floors_set_as_list = list(set([item["premisesFloor"] for item in entrance]))  # Номера этажей в подъезде
        if floors_set_as_list[0] == 1: # Исключить этаж с номером 1
            floors_set_as_list = floors_set_as_list[1:]
        floors_area_list = []  # Лист для значений площадей этажей подъезда
        wrong_floors = []  # Лист для номеров этажей с отклоняющейся от средней площадью этажа
        for i in range(len(floors_set_as_list)):  # Вычисление площади этажей из floors_set_as_list
            floor_area = 0
            for j in range(len(entrance)):
                if entrance[j]["premisesFloor"] == floors_set_as_list[i]:
                    floor_area += entrance[j]["areaValue"]
            floor_area = round(floor_area)
            floors_area_list.append(floor_area)
        average_area = int(sum(floors_area_list) / len(floors_area_list))
        for i in range(len(floors_area_list)):
            if floors_area_list[i] > average_area + DEVIATION or floors_area_list[i] < average_area - DEVIATION:
                wrong_floors.append(floors_set_as_list[i])
        wf = {
            "entrance": n + 1,
            "wrongFloors": wrong_floors,
        }
        wrong_floors_list.append(wf)
    return wrong_floors_list

# Список всех данных по квартирам в доме:
with open("5_all_apartments_restored.json", "r") as file:
    all_apartments = json.load(file)

# Распределить квартиры по подъездам по индексам, на которых происходит переход с последнего этажа на самый нижний
# # Лист всех этажей для квартир из all_apartments:
floors_list = [item["premisesFloor"] for item in all_apartments]

# # Лист индексов для разбивки всех квартир на подъезды:
separate_indexes = [0]
for i in range(1, len(floors_list)):
    if floors_list[i] - floors_list[i - 1] < 0:
        separate_indexes.append(i)
separate_indexes.append(len(floors_list))

# # Назначить каждой квартире в доме подъезд, в котором она расположена:
all_apartments_with_entrances = all_apartments[:]
for i in range(1, len(separate_indexes)):
    for j in range(separate_indexes[i]):
        if all_apartments_with_entrances[j].get("entrance"):
            pass
        else:
            all_apartments_with_entrances[j]["entrance"] = i

with open("6_all_apartments_with_entrances.json", "w", encoding="utf-8") as file:
    json.dump(all_apartments_with_entrances, file, ensure_ascii=False, indent=4)

# # Разбить общий список квартир в доме на подъезды как вложенные списки типа: [[подъезд1], [подъезд2], [] []]
all_apartments_by_entrances = []
for i in range(1, len(separate_indexes)):
    start = separate_indexes[i - 1]
    stop = separate_indexes[i]
    entr = all_apartments_with_entrances[start:stop]
    all_apartments_by_entrances.append(entr)

# Проверить правильность распределения квартир по этажам в подъездах
wrong_floors_list = check_wrong_floors(all_apartments_by_entrances)

# # Перераспределить квартиры на ошибочных этажах
for i in range(len(wrong_floors_list)):
    if wrong_floors_list[i]["wrongFloors"]:
        floors = wrong_floors_list[i]["wrongFloors"]  # Список ошибочных этажей в подъезде
        entrance = all_apartments_by_entrances[i]  # Подъезд
        average_area = floors_average_area(entrance)  # Средняя площадь этажа в подъезде
        aparts_at_floors = []  # Список всех aparts_at_floor
        for j in range(len(floors)):
            aparts_at_floor = [] # Список пар "id квартиры - площадь квартиры" на текущем этаже
            for item in entrance:
                if item["premisesFloor"] == floors[j]:
                    id_and_area = [item["objectId"], item["areaValue"]]
                    aparts_at_floor.append(id_and_area)
            aparts_at_floors.append(aparts_at_floor)
        for j in range(len(floors) - 1):
            if floors[j] == floors[j + 1] - 1:  # Если этажи соседние, объединить в общий список
                total_aparts = aparts_at_floors[j] + aparts_at_floors[j + 1]  # Все квартиры на обоих эатажах
                area = 0
                for k in range(len(total_aparts)):  # По одной суммируем площадь квартир в total_aparts
                    area += total_aparts[k][1]
                    if average_area + DEVIATION > area > average_area - DEVIATION:  # Признак конца этажа
                        objectId = total_aparts[k][0]  # id квартиры, которой заканчивается этаж
                for n in range(len(entrance)):  # Переназначить номер этажа, чтобы выровнять площади этажей
                    if entrance[n]["objectId"] == objectId:
                        if entrance[n]["premisesFloor"] == floors[j + 1]:  # Если квартире приписан следующий этаж
                            entrance[n]["premisesFloor"] = floors[j]  # то назначить ей текущий
                            entrance[n]["data_calculated"] = 1
                        elif entrance[n] == floors[j]:  # Если квартире приписан текущий этаж
                            entrance[n + 1]["premisesFloor"] = floors[j + 1]  # то следующей кв. назначить след. этаж
                            entrance[n + 1]["data_calculated"] = 1

with open("6_all_apartments_by_entrances.json", "w", encoding="utf-8") as file:
    json.dump(all_apartments_by_entrances, file, ensure_ascii=False, indent=4)

# Саздать план дома как состоящего из подъездов, в каждом подъезде - этажи с указанием номера этажа, его общей площади
# и списка квартир на этаже, где квартира представлена в виде пары "номер - площадь"
house_plan = []
for i in range(len(all_apartments_by_entrances)):
    floors_in_entrance = list(set([item["premisesFloor"] for item in all_apartments_by_entrances[i]]))
    entrance_plan = []
    for item in floors_in_entrance:
        current_floor = []
        current_floor_area = 0
        for j in range(len(all_apartments_by_entrances[i])):
            if all_apartments_by_entrances[i][j]["premisesFloor"] == item:
                _ = [all_apartments_by_entrances[i][j]["apartment"], all_apartments_by_entrances[i][j]["areaValue"]]
                current_floor_area += all_apartments_by_entrances[i][j]["areaValue"]
                current_floor.append(_)
        entrance_plan.append({"floor": item, "floor_area": round(current_floor_area),
                              "apartments_num_and_area": current_floor})
    house_plan.append({"entrance": i + 1, "plan": entrance_plan})

with open("6_house_plan.json", "w", encoding="utf-8") as file:
    json.dump(house_plan, file, ensure_ascii=False, indent=4)
