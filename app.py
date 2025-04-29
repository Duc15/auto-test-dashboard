# from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for, session
# from main import main as run_tests
# import pandas as pd
# import os
# import traceback
# import json

# app = Flask(__name__)
# app.secret_key = 'your_secret_key_here'  # Bắt buộc cần secret key để dùng session

# # Đọc user từ file
# def load_users():
#     with open('users.json', 'r') as f:
#         return json.load(f)

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         users = load_users()
#         username = request.form['username']
#         password = request.form['password']

#         # Kiểm tra user/password
#         for user in users:
#             if user['username'] == username and user['password'] == password:
#                 session['username'] = user['username']
#                 session['project'] = user['project']
#                 return redirect(url_for('index'))

#         return render_template('login.html', error="Sai tên đăng nhập hoặc mật khẩu.")

#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('login'))

# @app.route('/')
# def index():
#     if 'username' not in session:
#         return redirect(url_for('login'))
#     return render_template('index.html', username=session.get('username'), project=session.get('project'))

# @app.route('/upload', methods=['POST'])
# def upload_excel():
#     try:
#         if 'username' not in session:
#             return redirect(url_for('login'))

#         if 'file' not in request.files:
#             return jsonify({'error': 'No file uploaded'}), 400
#         file = request.files['file']
#         if not file.filename.endswith('.xlsx'):
#             return jsonify({'error': 'File must be .xlsx'}), 400

#         # Nếu file cũ tồn tại thì xóa đi
#         if os.path.exists('test_cases.xlsx'):
#             os.remove('test_cases.xlsx')
#         file.save('test_cases.xlsx')

#         # Chạy kiểm thử
#         run_tests()

#         # Đọc kết quả
#         results_df = pd.read_excel('test_result.xlsx', sheet_name='Test Results')
#         summary_df = pd.read_excel('test_result.xlsx', sheet_name='Summary')

#         results_df = results_df.fillna('')
#         summary_df = summary_df.fillna('')

#         def safe_json_loads(x):
#             if isinstance(x, str) and x.strip():
#                 try:
#                     return json.loads(x)
#                 except Exception:
#                     return x
#             return x

#         for col in ['request_body', 'expected_response', 'actual_response']:
#             if col in results_df.columns:
#                 results_df[col] = results_df[col].apply(safe_json_loads)

#         results = results_df.to_dict(orient='records')
#         summary = summary_df.to_dict(orient='records')

#         return jsonify({
#             'results': results,
#             'summary': summary,
#             'result_file': 'test_result.xlsx'
#         }), 200

#     except Exception as e:
#         print(traceback.format_exc())
#         return jsonify({'error': f'Exception: {str(e)}'}), 500

# @app.route('/download')
# def download_result():
#     if 'username' not in session:
#         return redirect(url_for('login'))

#     file_path = 'test_result.xlsx'
#     if os.path.exists(file_path):
#         return send_file(file_path, as_attachment=True)
#     return jsonify({'error': 'Result file not found'}), 404

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5002, debug=True)
# from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for, session
# from main import main as run_tests
# import pandas as pd
# import os
# import traceback
# import json
# import sqlite3
# from datetime import datetime
# import shutil

# app = Flask(__name__)
# app.secret_key = 'your_secret_key_here'  # Bắt buộc cần secret key để dùng session

# # Đọc user từ file
# def load_users():
#     with open('users.json', 'r') as f:
#         return json.load(f)

# # Khởi tạo SQLite
# def init_db():
#     with sqlite3.connect('library.db') as conn:
#         cursor = conn.cursor()
#         # Thêm cột test_name vào bảng test_library
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS test_library (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 test_name TEXT,
#                 test_case_file TEXT,
#                 result_file TEXT,
#                 username TEXT,
#                 project TEXT,
#                 created_at TEXT
#             )
#         ''')
#         # Kiểm tra và thêm cột test_name nếu chưa có
#         cursor.execute("PRAGMA table_info(test_library)")
#         columns = [col[1] for col in cursor.fetchall()]
#         if 'test_name' not in columns:
#             cursor.execute('ALTER TABLE test_library ADD COLUMN test_name TEXT')
#         conn.commit()

# init_db()

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         users = load_users()
#         username = request.form['username']
#         password = request.form['password']

#         # Kiểm tra user/password
#         for user in users:
#             if user['username'] == username and user['password'] == password:
#                 session['username'] = user['username']
#                 session['project'] = user['project']
#                 return redirect(url_for('index'))

#         return render_template('login.html', error="Sai tên đăng nhập hoặc mật khẩu.")

#     return render_template('login.html')

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('login'))

# @app.route('/')
# def index():
#     if 'username' not in session:
#         return redirect(url_for('login'))
#     return render_template('index.html', username=session.get('username'), project=session.get('project'))

# @app.route('/upload', methods=['POST'])
# def upload_excel():
#     try:
#         if 'username' not in session:
#             return jsonify({'error': 'Unauthorized'}), 401

#         if 'file' not in request.files:
#             return jsonify({'error': 'No file uploaded'}), 400
#         file = request.files['file']
#         if not file.filename.endswith('.xlsx'):
#             return jsonify({'error': 'File must be .xlsx'}), 400

#         test_name = request.form.get('test_name', 'Unnamed Test')  # Lấy tên đợt test, mặc định là 'Unnamed Test'

#         # Tạo thư mục library
#         os.makedirs('library', exist_ok=True)
        
#         # Tạo tên file với timestamp
#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#         test_case_file = f'library/test_cases_{timestamp}.xlsx'
#         result_file = f'library/test_result_{timestamp}.xlsx'
        
#         # Lưu file test case
#         file.save(test_case_file)

#         # Nếu file cũ tồn tại thì xóa đi
#         if os.path.exists('test_cases.xlsx'):
#             os.remove('test_cases.xlsx')
#         shutil.copy(test_case_file, 'test_cases.xlsx')

#         # Chạy kiểm thử
#         run_tests()

#         # Kiểm tra và di chuyển file kết quả
#         if not os.path.exists('test_result.xlsx'):
#             return jsonify({'error': 'Test result file not generated'}), 500
#         shutil.move('test_result.xlsx', result_file)

#         # Đọc kết quả
#         results_df = pd.read_excel(result_file, sheet_name='Test Results')
#         summary_df = pd.read_excel(result_file, sheet_name='Summary')

#         results_df = results_df.fillna('')
#         summary_df = summary_df.fillna('')

#         def safe_json_loads(x):
#             if isinstance(x, str) and x.strip():
#                 try:
#                     return json.loads(x)
#                 except Exception:
#                     return x
#             return x

#         for col in ['request_body', 'expected_response', 'actual_response']:
#             if col in results_df.columns:
#                 results_df[col] = results_df[col].apply(safe_json_loads)

#         results = results_df.to_dict(orient='records')
#         summary = summary_df.to_dict(orient='records')

#         # Lưu vào thư viện
#         with sqlite3.connect('library.db') as conn:
#             cursor = conn.cursor()
#             cursor.execute('''
#                 INSERT INTO test_library (test_name, test_case_file, result_file, username, project, created_at)
#                 VALUES (?, ?, ?, ?, ?, ?)
#             ''', (test_name, test_case_file, result_file, session.get('username'), session.get('project'), timestamp))
#             conn.commit()

#         return jsonify({
#             'results': results,
#             'summary': summary,
#             'result_file': result_file
#         }), 200

#     except Exception as e:
#         print(traceback.format_exc())
#         return jsonify({'error': f'Exception: {str(e)}'}), 500

# @app.route('/library', methods=['GET'])
# def get_library():
#     try:
#         if 'username' not in session:
#             return jsonify({'error': 'Unauthorized'}), 401

#         with sqlite3.connect('library.db') as conn:
#             cursor = conn.cursor()
#             cursor.execute('SELECT id, test_name, test_case_file, result_file, username, project, created_at FROM test_library WHERE username = ? AND project = ? ORDER BY created_at DESC',
#                           (session.get('username'), session.get('project')))
#             library = [
#                 {
#                     'id': row[0],
#                     'test_name': row[1],
#                     'test_case_file': row[2],
#                     'result_file': row[3],
#                     'username': row[4],
#                     'project': row[5],
#                     'created_at': row[6]
#                 } for row in cursor.fetchall()
#             ]
#         return jsonify({'library': library}), 200
#     except Exception as e:
#         print(traceback.format_exc())
#         return jsonify({'error': f'Exception: {str(e)}'}), 500

# @app.route('/rerun/<int:id>', methods=['POST'])
# def rerun_test(id):
#     try:
#         if 'username' not in session:
#             return jsonify({'error': 'Unauthorized'}), 401

#         with sqlite3.connect('library.db') as conn:
#             cursor = conn.cursor()
#             cursor.execute('SELECT test_name, test_case_file FROM test_library WHERE id = ? AND username = ? AND project = ?',
#                           (id, session.get('username'), session.get('project')))
#             row = cursor.fetchone()
#             if not row:
#                 return jsonify({'error': f'Test case ID {id} not found'}), 404
#             test_name, test_case_file = row[0], row[1]

#         if not os.path.exists(test_case_file):
#             return jsonify({'error': f'Test case file {test_case_file} not found'}), 404

#         timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
#         result_file = f'library/test_result_{timestamp}.xlsx'

#         if os.path.exists('test_cases.xlsx'):
#             os.remove('test_cases.xlsx')
#         shutil.copy(test_case_file, 'test_cases.xlsx')

#         try:
#             run_tests()
#         except Exception as e:
#             return jsonify({'error': f'Error running test: {str(e)}'}), 500

#         if not os.path.exists('test_result.xlsx'):
#             return jsonify({'error': 'Test result file not generated'}), 500
#         shutil.move('test_result.xlsx', result_file)

#         try:
#             results_df = pd.read_excel(result_file, sheet_name='Test Results')
#             summary_df = pd.read_excel(result_file, sheet_name='Summary')
#         except Exception as e:
#             return jsonify({'error': f'Error reading result file: {str(e)}'}), 500

#         results_df = results_df.fillna('')
#         summary_df = summary_df.fillna('')

#         def safe_json_loads(x):
#             if isinstance(x, str) and x.strip():
#                 try:
#                     return json.loads(x)
#                 except Exception:
#                     return x
#             return x

#         for col in ['request_body', 'expected_response', 'actual_response']:
#             if col in results_df.columns:
#                 results_df[col] = results_df[col].apply(safe_json_loads)

#         results = results_df.to_dict(orient='records')
#         summary = summary_df.to_dict(orient='records')

#         with sqlite3.connect('library.db') as conn:
#             cursor = conn.cursor()
#             cursor.execute('''
#                 INSERT INTO test_library (test_name, test_case_file, result_file, username, project, created_at)
#                 VALUES (?, ?, ?, ?, ?, ?)
#             ''', (f"{test_name} (Rerun)", test_case_file, result_file, session.get('username'), session.get('project'), timestamp))
#             conn.commit()

#         return jsonify({
#             'results': results,
#             'summary': summary,
#             'result_file': result_file
#         }), 200

#     except Exception as e:
#         print(traceback.format_exc())
#         return jsonify({'error': f'Exception: {str(e)}'}), 500

# @app.route('/delete/<int:id>', methods=['POST'])
# def delete_test(id):
#     try:
#         if 'username' not in session:
#             return jsonify({'error': 'Unauthorized'}), 401

#         with sqlite3.connect('library.db') as conn:
#             cursor = conn.cursor()
#             cursor.execute('SELECT test_case_file, result_file FROM test_library WHERE id = ? AND username = ? AND project = ?',
#                           (id, session.get('username'), session.get('project')))
#             row = cursor.fetchone()
#             if not row:
#                 return jsonify({'error': f'Test case ID {id} not found'}), 404
#             test_case_file, result_file = row[0], row[1]

#         # Xóa file nếu tồn tại
#         if os.path.exists(test_case_file):
#             os.remove(test_case_file)
#         if os.path.exists(result_file):
#             os.remove(result_file)

#         # Xóa bản ghi trong SQLite
#         with sqlite3.connect('library.db') as conn:
#             cursor = conn.cursor()
#             cursor.execute('DELETE FROM test_library WHERE id = ? AND username = ? AND project = ?',
#                           (id, session.get('username'), session.get('project')))
#             conn.commit()

#         return jsonify({'message': f'Test case ID {id} deleted successfully'}), 200

#     except Exception as e:
#         print(traceback.format_exc())
#         return jsonify({'error': f'Exception: {str(e)}'}), 500

# @app.route('/download/<path:filename>')
# def download_result(filename):
#     if 'username' not in session:
#         return jsonify({'error': 'Unauthorized'}), 401

#     file_path = filename
#     if os.path.exists(file_path):
#         return send_file(file_path, as_attachment=True)
#     return jsonify({'error': 'File not found'}), 404

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5002, debug=True)
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
app.secret_key = 'your_secret_key_here'  # Bắt buộc cần secret key để dùng session

# Đọc user từ file
def load_users():
    with open('users.json', 'r') as f:
        return json.load(f)

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
                fail_count INTEGER
            )
        ''')
        # Kiểm tra và thêm cột nếu chưa có
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
        username = request.form['username']
        password = request.form['password']

        # Kiểm tra user/password
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

        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['file']
        if not file.filename.endswith('.xlsx'):
            return jsonify({'error': 'File must be .xlsx'}), 400

        test_name = request.form.get('test_name', 'Unnamed Test')  # Lấy tên đợt test

        # Tạo thư mục library
        os.makedirs('library', exist_ok=True)
        
        # Tạo tên file với timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        test_case_file = f'library/test_cases_{timestamp}.xlsx'
        result_file = f'library/test_result_{timestamp}.xlsx'
        
        # Lưu file test case
        file.save(test_case_file)

        # Nếu file cũ tồn tại thì xóa đi
        if os.path.exists('test_cases.xlsx'):
            os.remove('test_cases.xlsx')
        shutil.copy(test_case_file, 'test_cases.xlsx')

        # Chạy kiểm thử
        run_tests()

        # Kiểm tra và di chuyển file kết quả
        if not os.path.exists('test_result.xlsx'):
            return jsonify({'error': 'Test result file not generated'}), 500
        shutil.move('test_result.xlsx', result_file)

        # Đọc kết quả
        results_df = pd.read_excel(result_file, sheet_name='Test Results')
        summary_df = pd.read_excel(result_file, sheet_name='Summary')

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

        # Lấy thông tin summary
        total_tests = summary[0]['Total Tests'] if summary and 'Total Tests' in summary[0] else 0
        pass_count = summary[0]['Pass'] if summary and 'Pass' in summary[0] else 0
        fail_count = summary[0]['Fail'] if summary and 'Fail' in summary[0] else 0

        # Lưu vào thư viện
        with sqlite3.connect('library.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO test_library (test_name, test_case_file, result_file, username, project, created_at, total_tests, pass_count, fail_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (test_name, test_case_file, result_file, session.get('username'), session.get('project'), timestamp, total_tests, pass_count, fail_count))
            conn.commit()

        return jsonify({
            'results': results,
            'summary': summary,
            'result_file': result_file
        }), 200

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': f'Exception: {str(e)}'}), 500

@app.route('/library', methods=['GET'])
def get_library():
    try:
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401

        with sqlite3.connect('library.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, test_name, test_case_file, result_file, username, project, created_at, total_tests, pass_count, fail_count
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
                    'fail_count': row[9]
                } for row in cursor.fetchall()
            ]
        return jsonify({'library': library}), 200
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': f'Exception: {str(e)}'}), 500

@app.route('/rerun/<int:id>', methods=['POST'])
def rerun_test(id):
    try:
        if 'username' not in session:
            return jsonify({'error': 'Unauthorized'}), 401

        with sqlite3.connect('library.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT test_name, test_case_file
                FROM test_library
                WHERE id = ? AND username = ? AND project = ?
            ''', (id, session.get('username'), session.get('project')))
            row = cursor.fetchone()
            if not row:
                return jsonify({'error': f'Test case ID {id} not found'}), 404
            test_name, test_case_file = row[0], row[1]

        if not os.path.exists(test_case_file):
            return jsonify({'error': f'Test case file {test_case_file} not found'}), 404

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = f'library/test_result_{timestamp}.xlsx'

        if os.path.exists('test_cases.xlsx'):
            os.remove('test_cases.xlsx')
        shutil.copy(test_case_file, 'test_cases.xlsx')

        try:
            run_tests()
        except Exception as e:
            return jsonify({'error': f'Error running test: {str(e)}'}), 500

        if not os.path.exists('test_result.xlsx'):
            return jsonify({'error': 'Test result file not generated'}), 500
        shutil.move('test_result.xlsx', result_file)

        try:
            results_df = pd.read_excel(result_file, sheet_name='Test Results')
            summary_df = pd.read_excel(result_file, sheet_name='Summary')
        except Exception as e:
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

        # Lấy thông tin summary
        total_tests = summary[0]['Total Tests'] if summary and 'Total Tests' in summary[0] else 0
        pass_count = summary[0]['Pass'] if summary and 'Pass' in summary[0] else 0
        fail_count = summary[0]['Fail'] if summary and 'Fail' in summary[0] else 0

        with sqlite3.connect('library.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO test_library (test_name, test_case_file, result_file, username, project, created_at, total_tests, pass_count, fail_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (test_name, test_case_file, result_file, session.get('username'), session.get('project'), timestamp, total_tests, pass_count, fail_count))
            conn.commit()

        return jsonify({
            'results': results,
            'summary': summary,
            'result_file': result_file
        }), 200

    except Exception as e:
        print(traceback.format_exc())
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
            test_case_file, result_file = row[0], row[1]

        # Xóa file nếu tồn tại
        if os.path.exists(test_case_file):
            os.remove(test_case_file)
        if os.path.exists(result_file):
            os.remove(result_file)

        # Xóa bản ghi trong SQLite
        with sqlite3.connect('library.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM test_library
                WHERE id = ? AND username = ? AND project = ?
            ''', (id, session.get('username'), session.get('project')))
            conn.commit()

        return jsonify({'message': f'Test case ID {id} deleted successfully'}), 200

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': f'Exception: {str(e)}'}), 500

@app.route('/download/<path:filename>')
def download_result(filename):
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    file_path = filename
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)