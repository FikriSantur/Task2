from flask import Flask, request, render_template, redirect, url_for
import os
import shutil
from database import create_table, insert_file, clear_all_data
from file_utils import allowed_file, read_txt, read_docx, read_excel, read_pdf
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    conn = sqlite3.connect('files.db')
    cursor = conn.cursor()
    
    # Dosya sayısını al
    cursor.execute("SELECT COUNT(*) FROM dosyalar")
    file_count = cursor.fetchone()[0]
    
    files = []
    if file_count > 0:
        # Dosyalar varsa, dosyaları çek
        cursor.execute("SELECT * FROM dosyalar")
        files = cursor.fetchall()
    
    conn.close()
    
    return render_template('index.html', files=files, file_count=file_count, error_message=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return redirect(request.url)

    files = request.files.getlist('files[]') #elde edilen dosya werkzeug.datastructures.FileStorage nesnesidir
    error_message = None

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            if filename.endswith('.txt'):
                content = read_txt(file_path)
                yazar = 'Unknown'
                olusturma_tarihi = 'Unknown'
                sahibi = 'Unknown'
            elif filename.endswith('.docx'):
                content, yazar, olusturma_tarihi, sahibi = read_docx(file_path)
            elif filename.endswith('.xlsx'):
                content, yazar, olusturma_tarihi, sahibi = read_excel(file_path)
            elif filename.endswith('.pdf'):
                content, yazar, olusturma_tarihi, sahibi = read_pdf(file_path)

            insert_file(filename, yazar, olusturma_tarihi, sahibi)
        else:
            error_message = f"Invalid file type: {file.filename}. Only TXT, PDF, DOCX, and XLSX files are allowed."
            break

    if error_message:
        return redirect(url_for('index', error_message=error_message))

    return redirect(url_for('index'))

@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '').lower()
    if not keyword:
        return redirect(url_for('index'))

    results = []
    conn = sqlite3.connect('files.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM dosyalar")
    files = cursor.fetchall()

    for file_info in files:
        filename = file_info[1]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if filename.endswith('.txt'):
            content = read_txt(file_path)
        elif filename.endswith('.docx'):
            content, _, _, _ = read_docx(file_path)
        elif filename.endswith('.xlsx'):
            content, _, _, _ = read_excel(file_path)
        elif filename.endswith('.pdf'):
            content, _, _, _ = read_pdf(file_path)
        else:
            continue

        if keyword in content.lower():
            results.append(file_info)

    if not results:
        return render_template('index.html', error_message="No files match the search keyword.", files=files, file_count=len(files))

    return render_template('results.html', results=results)

@app.route('/clear', methods=['POST'])
def clear_data():
    clear_all_data()

    folder = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    create_table()
    app.run(debug=True)
