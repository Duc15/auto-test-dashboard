import requests    # Thư viện dùng để gửi HTTP request
import json        # Thư viện để xử lý dữ liệu JSON

def send_request(method, url, body=None, token=None):
    # Tạo headers mặc định là JSON
    headers = {"Content-Type": "application/json"}
    
    # Nếu có token thì thêm vào header Authorization
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Chuyển method thành chữ in hoa (GET, POST, PUT...)
    method = method.upper()

    # Nếu có body thì chuyển dict thành chuỗi JSON
    data = json.dumps(body) if body else None

    # Gửi request dựa theo method đã cho
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, data=data)
    elif method == "PUT":
        response = requests.put(url, headers=headers, data=data)
    elif method == "PATCH":
        response = requests.patch(url, headers=headers, data=data)
    elif method == "DELETE":
        response = requests.delete(url, headers=headers, data=data)
    else:
        # Nếu method không hỗ trợ thì raise lỗi
        raise ValueError(f"Unsupported HTTP method: {method}")

    # Trả về status code và JSON body (nếu có)
    try:
        return response.status_code, response.json()
    except Exception:
        # Nếu không parse được JSON (ví dụ lỗi 204 No Content), trả về status và dict rỗng
        return response.status_code, {}
