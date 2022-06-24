import json

with open("3_final_details.json", "r") as file:
    final_details_to_sort = json.load(file)

# Унифицировать строковые значения для поля "apartment" с учетом литерных (типа "10а") и сдвоенных (типа "315, 316")
# номеров квартир для дальнейшей сортировки и восстановления пропущенных номеров квартир

for item in final_details_to_sort:
    num_to_sort = item["apartment"]
    if num_to_sort.isdigit():  # Проверить, что в номере квартиры только цифры
        while len(num_to_sort) < 4:
            num_to_sort = "0" + num_to_sort  # Дополнить номера до "0001", "0012", "0221"
    elif "," in num_to_sort:  # Разделить номера сдвоеных квартир типа "315, 316" и дополнить до вида "0315x"
        num = num_to_sort.split(",")
        num = num[0]
        while len(num) < 4:
            num = "0" + num
        num_to_sort = num + "x"
    else:  # Дополнить литерные номера квартир до вида "0001а"
        while len(num_to_sort) < 5:
            num_to_sort = "0" + num_to_sort
    item["num_to_sort"] = num_to_sort  # Добавить ко всем объектам служебное поле "num_to_sort" для сортировки по нему
    item["data_calculated"] = 0  # Добавить ко всем объектам служебное поле "data_calculated" для различения
    # исходных данных и измененных в результате вычислений

# Отсортировать квартиры по "num_to_sort"
final_details_sorted = sorted(final_details_to_sort, key=lambda x: x["num_to_sort"])

with open("4_final_details_sorted.json", "w", encoding="utf-8") as file:
    json.dump(final_details_sorted, file, ensure_ascii=False, indent=4)
