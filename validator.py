def validate_response(actual_status, actual_response, expected_status, expected_response):
    try:
        if int(actual_status) != int(expected_status):
            return "Fail", f"Mong đợi status {expected_status}, thực tế {actual_status}"

        for key, expected_value in expected_response.items():
            # Trường đặc biệt trong mảng: products[].title
            if "[]" in key:
                array_key, sub_key = key.split("[]")
                array_key = array_key.strip(".")
                sub_key = sub_key.strip(".")
                
                array_items = actual_response.get(array_key)
                if not isinstance(array_items, list):
                    return "Fail", f"Trường '{array_key}' không phải mảng"

                for idx, item in enumerate(array_items):
                    if sub_key not in item:
                        return "Fail", f"Thiếu '{sub_key}' trong phần tử {idx} của '{array_key}'"
                
                # Nếu giá trị có dấu ~, kiểm tra chuỗi con
                if isinstance(expected_value, str) and expected_value.startswith("~"):
                    substring = expected_value[1:]  # Bỏ dấu ~ để lấy chuỗi con cần kiểm tra
                    for idx, item in enumerate(array_items):
                        actual_value = str(item[sub_key])  # Chuyển thành chuỗi để đảm bảo
                        if substring not in actual_value:
                            return "Fail", f"Phần tử {idx} của '{array_key}.{sub_key}' không chứa '{substring}'"
                    continue
                # Kiểm tra giá trị chính xác nếu không có ~
                for idx, item in enumerate(array_items):
                    if item[sub_key] != expected_value:
                        return "Fail", f"Lỗi tại '{array_key}[{idx}].{sub_key}': mong đợi {expected_value}, thực tế {item[sub_key]}"
                continue  # Kiểm xong field trong mảng, sang field khác

            # Trường bình thường
            if key not in actual_response:
                return "Fail", f"Thiếu trường '{key}'"

            # Nếu expected_value là một dictionary, kiểm tra đệ quy
            if isinstance(expected_value, dict):
                sub_result, sub_message = validate_response(actual_status, actual_response[key], expected_status, expected_value)
                if sub_result == "Fail":
                    return "Fail", f"Lỗi tại '{key}': {sub_message}"
                continue

            if expected_value == "*":
                continue

            # Kiểm tra giá trị có dấu ~ (kiểm tra chuỗi con)
            if isinstance(expected_value, str) and expected_value.startswith("~"):
                substring = expected_value[1:]  # Bỏ dấu ~ để lấy chuỗi con cần kiểm tra
                actual_value = str(actual_response[key])  # Chuyển thành chuỗi để đảm bảo
                if substring not in actual_value:
                    return "Fail", f"Trường '{key}' không chứa '{substring}'"
                continue

            # So sánh giá trị chính xác nếu không có ~
            if actual_response[key] != expected_value:
                return "Fail", f"Lỗi tại '{key}': mong đợi {expected_value}, thực tế {actual_response[key]}"
            
        return "Pass", ""
    except Exception as e:
        return "Fail", f"Exception: {str(e)}"