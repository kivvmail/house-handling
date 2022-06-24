import json

with open('2_raw_details.json', 'r') as file:
    raw_details = json.load(file)

# Из спарсенных объектов выбрать те, которые в адресе имеют указание, что это квартира, и отсеять квартиры с удаленными
# данными (иначе будут дубли - актуальные и удаленные записи для одного и того же объекта)
final_details = []
for item in raw_details:
    if " кв" in item["objectData"]["addressNote"] and item["objectData"]["removed"] != 1:
        _ = {
            "objectId": item["objectId"],
            "addressNote": item.get("objectData").get("addressNote"),
            "apartment": item.get("objectData").get("objectAddress").get("apartment"),
            "areaValue": item.get("premisesData").get("areaValue"),
            "premisesFloor": item.get("premisesData").get("premisesFloor"),
        }
        final_details.append(_)

# Для квартир с пустыми "premisesFloor" попробовать извлечь номер этажа из поля "objectName" в "2_raw_details.json"
for item in final_details:
    if item["premisesFloor"] is None:
        for _ in raw_details:
            if _["objectId"] == item["objectId"]:
                raw_item = _
        if raw_item.get("objectData").get("objectName"):
            for_floor = raw_item.get("objectData").get("objectName")[-4:].strip(". :аж")
            if for_floor.isdigit():
                item["premisesFloor"] = int(for_floor)
            else:
                item["premisesFloor"] = ""

with open("3_final_details.json", "w", encoding='utf-8') as file:
    json.dump(final_details, file, ensure_ascii=False, indent=4)
