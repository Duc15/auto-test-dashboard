from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for, session
from main import main as run_tests
import pandas as pd
import os
import traceback
import json
import sqlite3
from datetime import datetime
import shutil

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Thay bằng key bảo mật thực tế

# Đọc user từ file
def load_users():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading users.json: {str(e)}")
        return []

# Khởi tạo SQLite
def init_db():
    with sqlite3.connect('library.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT,
                test_case_file TEXT,
                result_file TEXT,
                username TEXT,
                project TEXT,
                created_at TEXT,
                total_tests INTEGER,
                pass_count INTEGER,
                fail_count INTEGER,
                base_url TEXT,
                token TEXT
            )
        ''')
        cursor.execute("PRAGMA table_info(test_library)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'test_name' not in columns:
            cursor.execute('ALTER TABLE test_library ADD COLUMN test_name TEXT')
        if 'total_tests' not in columns:
            cursor.execute('ALTER TABLE test_library ADD COLUMN total_tests INTEGER')
        if 'pass_count' not in columns:
            cursor.execute('ALTER TABLE test_library ADD COLUMN pass_count INTEGER')
        if 'fail_count' not in columns:
            cursor.execute('ALTER TABLE test_library ADD COLUMN fail_count INTEGER')
        if 'base_url' not in columns:
            cursor.execute('ALTER TABLE test_library ADD COLUMN base_url TEXT')
        if 'token' not in columns:
            cursor.execute('ALTER TABLE test_library ADD COLUMN token TEXT')
        conn.commit()

init_db()

# Hàm chuyển đổi thời gian
def format_timestamp(timestamp):
    try:
        dt = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
        return dt.strftime('%d/%m/%Y %H:%M:%S')
    except ValueError:
        return timestamp

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form.get('username')
        password = request.form.get('password')

        for user in users:
            if user['username'] == username and user['password'] == password:
                session['username'] = user['username']
                session['project'] = user['project']
                return redirect(url_for('index'))

        return render_template('login.html', error="Sai tên đăng nhập hoặc mật khẩu.")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session.get('username'), project=session.get('project'))

@app.route('/upload', methods=['POST'])
def upload_excel():
    try:
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401

        if 'file' not in request.files or not request.files['file']:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['file']
        if not file.filename.endswith('.xlsx'):
            return jsonify({'error': 'File must be .xlsx'}), 400

        # Lấy base_url và token từ form
        base_url = request.form.get('base_url')
        token = request.form.get('token', None)

        if not base_url:
            return jsonify({'error': 'Base URL is required'}), 400

        test_name = request.form.get('test_name', 'Unnamed Test')

        # Tạo thư mục library
        os.makedirs('library', exist_ok=True)
        
        # Tạo tên file với timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        test_case_file = f'library/test_cases_{timestamp}.xlsx'
        result_file = f'library/test_result_{timestamp}.xlsx'
        
        # Lưu file test case
        try:
            file.seek(0)
            file.save(test_case_file)
            print(f"Saved test case file: {test_case_file}, Size: {os.path.getsize(test_case_file)} bytes")
            if not os.path.exists(test_case_file) or os.path.getsize(test_case_file) == 0:
                return jsonify({'error': 'Saved test case file is empty or not created'}), 400
        except Exception as e:
            print(f"Error saving file: {str(e)}")
            return jsonify({'error': f'Error saving file: {str(e)}'}), 500

        # Sao chép file test case
        try:
            if os.path.exists('test_cases.xlsx'):
                os.remove('test_cases.xlsx')
            shutil.copy(test_case_file, 'test_cases.xlsx')
            print(f"Copied test case file to test_cases.xlsx")
        except Exception as e:
            print(f"Error copying test case file: {str(e)}")
            return jsonify({'error': f'Error copying test case file: {str(e)}'}), 500

        # Chạy kiểm thử
        try:
            run_tests(base_url=base_url, token=token)
            print(f"Ran tests with base_url={base_url}, token={token}")
        except Exception as e:
            print(f"Error running tests: {str(e)}")
            return jsonify({'error': f'Error running tests: {str(e)}'}), 500

        # Kiểm tra file kết quả
        if not os.path.exists('test_result.xlsx'):
            return jsonify({'error': 'Test result file not generated'}), 500
        try:
            shutil.move('test_result.xlsx', result_file)
            print(f"Moved test_result.xlsx to {result_file}")
        except Exception as e:
            print(f"Error moving result file: {str(e)}")
            return jsonify({'error': f'Error moving result file: {str(e)}'}), 500

        # Đọc kết quả
        try:
            results_df = pd.read_excel(result_file, sheet_name='Test Results')
            summary_df = pd.read_excel(result_file, sheet_name='Summary')
            print(f"Read result file: {result_file}")
        except Exception as e:
            print(f"Error reading result file: {str(e)}")
            return jsonify({'error': f'Error reading result file: {str(e)}'}), 500

        results_df = results_df.fillna('')
        summary_df = summary_df.fillna('')

        def safe_json_loads(x):
            if isinstance(x, str) and x.strip():
                try:
                    return json.loads(x)
                except Exception:
                    return x
            return x

        for col in ['request_body', 'expected_response', 'actual_response']:
            if col in results_df.columns:
                results_df[col] = results_df[col].apply(safe_json_loads)

        results = results_df.to_dict(orient='records')
        summary = summary_df.to_dict(orient='records')

        total_tests = summary[0]['Total Tests'] if summary and 'Total Tests' in summary[0] else 0
        pass_count = summary[0]['Pass'] if summary and 'Pass' in summary[0] else 0
        fail_count = summary[0]['Fail'] if summary and 'Fail' in summary[0] else 0

        # Lưu vào thư viện
        try:
            with sqlite3.connect('library.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO test_library (test_name, test_case_file, result_file, username, project, created_at, total_tests, pass_count, fail_count, base_url, token)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (test_name, test_case_file, result_file, session.get('username'), session.get('project'), timestamp, total_tests, pass_count, fail_count, base_url, token))
                conn.commit()
            print(f"Saved test run to database: {test_name}")
        except Exception as e:
            print(f"Error saving to database: {str(e)}")
            return jsonify({'error': f'Error saving to database: {str(e)}'}), 500

        return jsonify({
            'results': results,
            'summary': summary,
            'result_file': result_file
        }), 200

    except Exception as e:
        print(f"Unexpected error in upload: {traceback.format_exc()}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/library', methods=['GET'])
def get_library():
    try:
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401

        with sqlite3.connect('library.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, test_name, test_case_file, result_file, username, project, created_at, total_tests, pass_count, fail_count, base_url, token
                FROM test_library
                WHERE username = ? AND project = ?
                ORDER BY created_at DESC
            ''', (session.get('username'), session.get('project')))
            library = [
                {
                    'id': row[0],
                    'test_name': row[1],
                    'test_case_file': row[2],
                    'result_file': row[3],
                    'username': row[4],
                    'project': row[5],
                    'created_at': format_timestamp(row[6]),
                    'total_tests': row[7],
                    'pass_count': row[8],
                    'fail_count': row[9],
                    'base_url': row[10],
                    'token': row[11]
                } for row in cursor.fetchall()
            ]
        print(f"Retrieved library for user: {session.get('username')}")
        return jsonify({'library': library}), 200
    except Exception as e:
        print(f"Error in get_library: {traceback.format_exc()}")
        return jsonify({'error': f'Exception: {str(e)}'}), 500

@app.route('/rerun/<int:id>', methods=['POST'])
def rerun_test(id):
    try:
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401

        with sqlite3.connect('library.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT test_name, test_case_file, base_url, token
                FROM test_library
                WHERE id = ? AND username = ? AND project = ?
            ''', (id, session.get('username'), session.get('project')))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': f'Test case ID {id} not found'}), 404
            test_name, test_case_file, base_url, token = row

        if not os.path.exists(test_case_file):
            return jsonify({'error': f'Test case file {test_case_file} not found'}), 404

        if not base_url:
            return jsonify({'error': 'Base URL is missing for this test case'}), 400

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = f'library/test_result_{timestamp}.xlsx'

        try:
            if os.path.exists('test_cases.xlsx'):
                os.remove('test_cases.xlsx')
            shutil.copy(test_case_file, 'test_cases.xlsx')
            print(f"Copied test case file to test_cases.xlsx for rerun")
        except Exception as e:
            print(f"Error copying test case file: {str(e)}")
            return jsonify({'error': f'Error copying test case file: {str(e)}'}), 500

        try:
            run_tests(base_url=base_url, token=token)
            print(f"Ran rerun tests with base_url={base_url}, token={token}")
        except Exception as e:
            print(f"Error running tests: {str(e)}")
            return jsonify({'error': f'Error running tests: {str(e)}'}), 500

        if not os.path.exists('test_result.xlsx'):
            return jsonify({'error': 'Test result file not generated'}), 500
        try:
            shutil.move('test_result.xlsx', result_file)
            print(f"Moved test_result.xlsx to {result_file}")
        except Exception as e:
            print(f"Error moving result file: {str(e)}")
            return jsonify({'error': f'Error moving result file: {str(e)}'}), 500

        try:
            results_df = pd.read_excel(result_file, sheet_name='Test Results')
            summary_df = pd.read_excel(result_file, sheet_name='Summary')
            print(f"Read result file: {result_file}")
        except Exception as e:
            print(f"Error reading result file: {str(e)}")
            return jsonify({'error': f'Error reading result file: {str(e)}'}), 500

        results_df = results_df.fillna('')
        summary_df = summary_df.fillna('')

        def safe_json_loads(x):
            if isinstance(x, str) and x.strip():
                try:
                    return json.loads(x)
                except Exception:
                    return x
            return x

        for col in ['request_body', 'expected_response', 'actual_response']:
            if col in results_df.columns:
                results_df[col] = results_df[col].apply(safe_json_loads)

        results = results_df.to_dict(orient='records')
        summary = summary_df.to_dict(orient='records')

        total_tests = summary[0]['Total Tests'] if summary and 'Total Tests' in summary[0] else 0
        pass_count = summary[0]['Pass'] if summary and 'Pass' in summary[0] else 0
        fail_count = summary[0]['Fail'] if summary and 'Fail' in summary[0] else 0

        try:
            with sqlite3.connect('library.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO test_library (test_name, test_case_file, result_file, username, project, created_at, total_tests, pass_count, fail_count, base_url, token)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (f"{test_name} (Rerun)", test_case_file, result_file, session.get('username'), session.get('project'), timestamp, total_tests, pass_count, fail_count, base_url, token))
                conn.commit()
            print(f"Saved rerun to database: {test_name} (Rerun)")
        except Exception as e:
            print(f"Error saving to database: {str(e)}")
            return jsonify({'error': f'Error saving to database: {str(e)}'}), 500

        return jsonify({
            'results': results,
            'summary': summary,
            'result_file': result_file
        }), 200

    except Exception as e:
        print(f"Unexpected error in rerun: {traceback.format_exc()}")
        return jsonify({'error': f'Exception: {str(e)}'}), 500

@app.route('/delete/<int:id>', methods=['POST'])
def delete_test(id):
    try:
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401

        with sqlite3.connect('library.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT test_case_file, result_file
                FROM test_library
                WHERE id = ? AND username = ? AND project = ?
            ''', (id, session.get('username'), session.get('project')))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': f'Test case ID {id} not found'}), 404
            test_case_file, result_file = row

        try:
            if os.path.exists(test_case_file):
                os.remove(test_case_file)
            if os.path.exists(result_file):
                os.remove(result_file)
            print(f"Deleted files: {test_case_file}, {result_file}")
        except Exception as e:
            print(f"Error deleting files: {str(e)}")
            return jsonify({'error': f'Error deleting files: {str(e)}'}), 500

        try:
            with sqlite3.connect('library.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM test_library
                    WHERE id = ? AND username = ? AND project = ?
                ''', (id, session.get('username'), session.get('project')))
                conn.commit()
            print(f"Deleted test case ID {id} from database")
        except Exception as e:
            print(f"Error deleting from database: {str(e)}")
            return jsonify({'error': f'Error deleting from database: {str(e)}'}), 500

        return jsonify({'message': f'Test case ID {id} deleted successfully'}), 200

    except Exception as e:
        print(f"Unexpected error in delete: {traceback.format_exc()}")
        return jsonify({'error': f'Exception: {str(e)}'}), 500

@app.route('/download/<path:filename>')
def download_result(filename):
    try:
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401

        file_path = filename
        if os.path.exists(file_path):
            print(f"Downloading file: {file_path}")
            return send_file(file_path, as_attachment=True)
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        print(f"Error in download: {traceback.format_exc()}")
        return jsonify({'error': f'Exception: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)