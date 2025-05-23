from utils import load_test_cases_from_excel
from request_handler import send_request
from validator import validate_response
from reporter import save_test_results
import json

def main(base_url, token=None):
    test_cases = load_test_cases_from_excel("test_cases.xlsx")
    passed = 0
    failed_cases = []
    results = []

    for i, case in enumerate(test_cases, start=1):
        full_url = base_url.rstrip('/') + '/' + case['endpoint'].lstrip('/')
        print(f"\n🧪 Test Case {i}: {case['api_name']} [{case['method']}]")

        status_code, response_data = send_request(
            method=case['method'],
            url=full_url,
            body=case['request_body'],
            token=token  # Truyền token vào đây
        )

        result, message = validate_response(status_code, response_data, case['expected_status'], case['expected_response'])

        result_data = {
            'actual_response': json.dumps(response_data, indent=4, ensure_ascii=False),
            'result': result,
            'message': message
        }

        if result == "Pass":
            print("✅ Passed 🎉")
            passed += 1
        else:
            print("❌ Failed 💥")
            failed_cases.append(f"TC{i}")

        results.append(result_data)

    print(f"\n🎯 Tổng số test: {len(test_cases)} | ✅ Passed: {passed} | ❌ Failed: {len(test_cases) - passed}")

    if failed_cases:
        print(f"  🔍 Lỗi ở: {', '.join(failed_cases)}")

    save_test_results(test_cases, results)

if __name__ == "__main__":
    # Để test local, bạn có thể tạm thời thêm giá trị mặc định
    main(base_url="http://example.com", token="your_token_here")