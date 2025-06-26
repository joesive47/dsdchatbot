from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session, send_file
from flask_cors import CORS
import sqlite3
import pandas as pd
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import io
import csv
from functools import wraps

app = Flask(__name__)
CORS(app)

# Configuration
app.secret_key = os.environ.get('SECRET_KEY', 'railway-dsd-chatbot-secret-key-2024')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB limit

# สร้างโฟลเดอร์ uploads ถ้าไม่มี
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database initialization
def init_db():
    """สร้างฐานข้อมูลและตารางเริ่มต้น"""
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    
    # สร้างตาราง categories
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # สร้างตาราง questions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    # เพิ่มหมวดหมู่เริ่มต้น
    default_categories = [
        'ทั่วไป',
        'คอร์สเรียน', 
        'ราคาและการชำระเงิน',
        'การติดต่อ',
        'ระบบและเทคนิค'
    ]
    
    for category in default_categories:
        cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
    
    # เพิ่มคำถามเริ่มต้น
    default_questions = [
        (1, 'สวัสดี', 'สวัสดีครับ! ยินดีต้อนรับสู่ระบบ DSD Chatbot ขับเคลื่อนโดย Railway! 🚂'),
        (1, 'hello', 'Hello! Welcome to DSD Chatbot powered by Railway! 🚀'),
        (2, 'คอร์สเรียนมีอะไรบ้าง', 'เรามีคอร์สเรียนหลากหลาย:\n- การเขียนโปรแกรม Python\n- การออกแบบ UI/UX\n- การวิเคราะห์ข้อมูล\n- การพัฒนาเว็บไซต์\n- การตลาดดิจิทัล'),
        (3, 'ราคาคอร์สเท่าไหร่', 'ราคาคอร์สแต่ละหลักสูตร:\n- คอร์สพื้นฐาน: 2,500-5,000 บาท\n- คอร์สขั้นกลาง: 5,000-8,000 บาท\n- คอร์สขั้นสูง: 8,000-12,000 บาท'),
        (2, 'วิธีการสมัครเรียน', 'การสมัครเรียนทำได้ง่ายๆ:\n1. เลือกคอร์สที่สนใจ\n2. กดปุ่ม "สมัครเรียน"\n3. กรอกข้อมูลส่วนตัว\n4. ชำระเงินค่าเรียน\n5. เริ่มเรียนได้ทันที'),
        (4, 'ติดต่อเจ้าหน้าที่', 'สามารถติดต่อเจ้าหน้าที่ได้หลายช่องทาง:\n📞 โทร: 02-123-4567\n📧 อีเมล: info@dsdchatbot.com\n💬 Line: @dsdsupport\n🕒 เวลาทำการ: จันทร์-ศุกร์ 9:00-18:00'),
        (5, 'railway ทดสอบ', 'ยอดเยี่ยม! Railway ทำงานได้ปกติ 🚂 ไม่มี cold start และตอบสนองเร็วมาก!'),
        (5, 'ทดสอบ railway', 'สวัสดีจาก Railway! 🚂 ระบบนี้:\n✅ ไม่มี cold start\n✅ ตอบสนองเร็ว\n✅ SSL ฟรี\n✅ Deploy ง่าย\n\nพร้อมให้บริการตลอด 24/7!'),
        (1, 'ขอบคุณ', 'ยินดีครับ! หากมีคำถามเพิ่มเติม สามารถสอบถามได้ตลอดเวลา 😊'),
        (1, 'thank you', 'You\'re welcome! Feel free to ask anytime! 😊')
    ]
    
    for question_data in default_questions:
        cursor.execute('''
            INSERT OR IGNORE INTO questions (category_id, question, answer) 
            VALUES (?, ?, ?)
        ''', question_data)
    
    conn.commit()
    conn.close()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Database helper functions
def get_db_connection():
    """สร้างการเชื่อมต่อฐานข้อมูล"""
    conn = sqlite3.connect('chatbot.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_all_categories():
    """ดึงข้อมูลหมวดหมู่ทั้งหมด"""
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories ORDER BY name').fetchall()
    conn.close()
    return categories

def get_all_questions(search=None, category_id=None):
    """ดึงข้อมูลคำถามทั้งหมด"""
    conn = get_db_connection()
    
    query = '''
        SELECT q.*, c.name as category_name 
        FROM questions q 
        JOIN categories c ON q.category_id = c.id 
    '''
    params = []
    conditions = []
    
    if search:
        conditions.append('(q.question LIKE ? OR q.answer LIKE ?)')
        params.extend([f'%{search}%', f'%{search}%'])
    
    if category_id and category_id != 'all':
        conditions.append('q.category_id = ?')
        params.append(category_id)
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' ORDER BY q.updated_at DESC'
    
    questions = conn.execute(query, params).fetchall()
    conn.close()
    return questions

def find_answer(user_input):
    """หาคำตอบจากฐานข้อมูล"""
    conn = get_db_connection()
    user_input_lower = user_input.lower()
    
    # ค้นหาคำตอบที่ตรงกันแน่นอน
    exact_match = conn.execute(
        'SELECT answer FROM questions WHERE LOWER(question) = ?', 
        (user_input_lower,)
    ).fetchone()
    
    if exact_match:
        conn.close()
        return exact_match['answer']
    
    # ค้นหาคำตอบที่มีคำสำคัญ
    keyword_match = conn.execute(
        'SELECT answer FROM questions WHERE LOWER(question) LIKE ? ORDER BY LENGTH(question) LIMIT 1', 
        (f'%{user_input_lower}%',)
    ).fetchone()
    
    if keyword_match:
        conn.close()
        return keyword_match['answer']
    
    # ค้นหาในคำตอบ
    answer_match = conn.execute(
        'SELECT answer FROM questions WHERE LOWER(answer) LIKE ? LIMIT 1', 
        (f'%{user_input_lower}%',)
    ).fetchone()
    
    if answer_match:
        conn.close()
        return answer_match['answer']
    
    conn.close()
    return 'ขออภัย ฉันไม่เข้าใจคำถามของคุณ 😅\n\nลองถามว่า:\n- "สวัสดี"\n- "คอร์สเรียนมีอะไรบ้าง"\n- "ราคาคอร์สเท่าไหร่"\n- "railway ทดสอบ"\n\n🚂 Powered by Railway'

# Routes

@app.route('/')
def home():
    """หน้าแรก - แสดงข้อมูล API"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """หน้าเข้าสู่ระบบ Admin"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # ตรวจสอบข้อมูลเข้าสู่ระบบ (สำหรับ demo)
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            session['username'] = username
            flash('เข้าสู่ระบบสำเร็จ!')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """ออกจากระบบ"""
    session.clear()
    flash('ออกจากระบบแล้ว')
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin_dashboard():
    """หน้า Dashboard Admin"""
    conn = get_db_connection()
    
    # นับจำนวนคำถามและหมวดหมู่
    total_questions = conn.execute('SELECT COUNT(*) as count FROM questions').fetchone()['count']
    total_categories = conn.execute('SELECT COUNT(*) as count FROM categories').fetchone()['count']
    
    # ดึงข้อมูลหมวดหมู่
    categories = get_all_categories()
    
    conn.close()
    
    return render_template('admin.html', 
                         total_questions=total_questions,
                         total_categories=total_categories,
                         categories=categories)

@app.route('/questions')
@login_required
def manage_questions():
    """หน้าจัดการคำถาม"""
    search = request.args.get('search', '')
    category_filter = request.args.get('category', 'all')
    
    questions = get_all_questions(search, category_filter if category_filter != 'all' else None)
    categories = get_all_categories()
    
    return render_template('questions.html', 
                         questions=questions, 
                         categories=categories,
                         search=search,
                         category_filter=category_filter)

@app.route('/add_category', methods=['POST'])
@login_required
def add_category():
    """เพิ่มหมวดหมู่ใหม่"""
    category_name = request.form.get('category_name', '').strip()
    
    if not category_name:
        flash('กรุณากรอกชื่อหมวดหมู่')
        return redirect(url_for('admin_dashboard'))
    
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO categories (name) VALUES (?)', (category_name,))
        conn.commit()
        conn.close()
        flash(f'เพิ่มหมวดหมู่ "{category_name}" สำเร็จ!')
    except sqlite3.IntegrityError:
        flash('หมวดหมู่นี้มีอยู่แล้ว')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/add_question', methods=['POST'])
@login_required
def add_question():
    """เพิ่มคำถามใหม่"""
    category_id = request.form.get('category_id')
    question = request.form.get('question', '').strip()
    answer = request.form.get('answer', '').strip()
    
    if not all([category_id, question, answer]):
        flash('กรุณากรอกข้อมูลให้ครบถ้วน')
        return redirect(url_for('admin_dashboard'))
    
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO questions (category_id, question, answer) 
            VALUES (?, ?, ?)
        ''', (category_id, question, answer))
        conn.commit()
        conn.close()
        flash('เพิ่มคำถามสำเร็จ!')
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_question/<int:question_id>')
@login_required
def edit_question(question_id):
    """หน้าแก้ไขคำถาม"""
    conn = get_db_connection()
    question = conn.execute('SELECT * FROM questions WHERE id = ?', (question_id,)).fetchone()
    categories = get_all_categories()
    conn.close()
    
    if not question:
        flash('ไม่พบคำถามที่ต้องการแก้ไข')
        return redirect(url_for('manage_questions'))
    
    return render_template('edit_questions.html', question=question, categories=categories)

@app.route('/edit_question/<int:question_id>', methods=['POST'])
@login_required
def update_question(question_id):
    """อัปเดตคำถาม"""
    category_id = request.form.get('category_id')
    question = request.form.get('question', '').strip()
    answer = request.form.get('answer', '').strip()
    
    if not all([category_id, question, answer]):
        flash('กรุณากรอกข้อมูลให้ครบถ้วน')
        return redirect(url_for('edit_question', question_id=question_id))
    
    try:
        conn = get_db_connection()
        conn.execute('''
            UPDATE questions 
            SET category_id = ?, question = ?, answer = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (category_id, question, answer, question_id))
        conn.commit()
        conn.close()
        flash('แก้ไขคำถามสำเร็จ!')
        return redirect(url_for('manage_questions'))
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}')
        return redirect(url_for('edit_question', question_id=question_id))

@app.route('/delete_question/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    """ลบคำถาม"""
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM questions WHERE id = ?', (question_id,))
        conn.commit()
        conn.close()
        flash('ลบคำถามสำเร็จ!')
    except Exception as e:
        flash(f'เกิดข้อผิดพลาด: {str(e)}')
    
    return redirect(url_for('manage_questions'))

@app.route('/upload_excel', methods=['GET', 'POST'])
@login_required
def upload_excel():
    """อัปโหลดไฟล์ Excel"""
    if request.method == 'GET':
        categories = get_all_categories()
        return render_template('upload_excel.html', categories=categories)
    
    # Handle POST request
    category_id = request.form.get('category_id')
    
    if 'file' not in request.files:
        flash('ไม่พบไฟล์ที่อัปโหลด')
        return redirect(url_for('upload_excel'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('ไม่ได้เลือกไฟล์')
        return redirect(url_for('upload_excel'))
    
    if not category_id:
        flash('กรุณาเลือกหมวดหมู่')
        return redirect(url_for('upload_excel'))
    
    try:
        # อ่านไฟล์ Excel
        df = pd.read_excel(file)
        
        # ตรวจสอบคอลัมน์ที่จำเป็น
        required_columns = ['question', 'answer']
        if not all(col in df.columns for col in required_columns):
            flash(f'ไฟล์ Excel ต้องมีคอลัมน์: {", ".join(required_columns)}')
            return redirect(url_for('upload_excel'))
        
        # ลบข้อมูลที่เป็นค่าว่าง
        df = df.dropna(subset=required_columns)
        
        if df.empty:
            flash('ไม่พบข้อมูลที่ถูกต้องในไฟล์')
            return redirect(url_for('upload_excel'))
        
        # บันทึกลงฐานข้อมูล
        conn = get_db_connection()
        added_count = 0
        
        for _, row in df.iterrows():
            try:
                conn.execute('''
                    INSERT INTO questions (category_id, question, answer) 
                    VALUES (?, ?, ?)
                ''', (category_id, str(row['question']).strip(), str(row['answer']).strip()))
                added_count += 1
            except Exception as e:
                print(f"Error adding question: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        flash(f'นำเข้าข้อมูลสำเร็จ! เพิ่มคำถาม {added_count} รายการ')
        
    except Exception as e:
        flash(f'เกิดข้อผิดพลาดในการนำเข้าข้อมูล: {str(e)}')
    
    return redirect(url_for('upload_excel'))

@app.route('/download_template')
@login_required
def download_template():
    """ดาวน์โหลดไฟล์ Template Excel"""
    # สร้างข้อมูลตัวอย่าง
    sample_data = {
        'question': [
            'สวัสดี',
            'คอร์สเรียนมีอะไรบ้าง',
            'ราคาคอร์สเท่าไหร่',
            'วิธีการสมัครเรียน'
        ],
        'answer': [
            'สวัสดีครับ! ยินดีต้อนรับสู่ระบบ',
            'เรามีคอร์สหลากหลาย เช่น Python, Web Development, Data Science',
            'ราคาเริ่มต้นที่ 2,500 บาท ขึ้นอยู่กับหลักสูตร',
            'สามารถสมัครได้ผ่านเว็บไซต์ หรือติดต่อเจ้าหน้าที่'
        ]
    }
    
    df = pd.DataFrame(sample_data)
    
    # สร้างไฟล์ Excel ใน memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Questions', index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name='chatbot_template.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/export_questions')
@login_required
def export_questions():
    """ส่งออกคำถามทั้งหมดเป็น CSV"""
    questions = get_all_questions()
    
    # สร้างไฟล์ CSV ใน memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # เขียน header
    writer.writerow(['ID', 'Category', 'Question', 'Answer', 'Created', 'Updated'])
    
    # เขียนข้อมูล
    for q in questions:
        writer.writerow([
            q['id'],
            q['category_name'],
            q['question'],
            q['answer'],
            q['created_at'],
            q['updated_at']
        ])
    
    output.seek(0)
    
    # สร้าง BytesIO จาก StringIO
    csv_output = io.BytesIO()
    csv_output.write(output.getvalue().encode('utf-8-sig'))  # เพิ่ม BOM สำหรับ UTF-8
    csv_output.seek(0)
    
    return send_file(
        csv_output,
        as_attachment=True,
        download_name=f'questions_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mimetype='text/csv'
    )

# API Routes

@app.route('/api/health', methods=['GET'])
def api_health():
    """API Health Check"""
    return jsonify({
        'status': 'healthy',
        'message': 'DSD Chatbot API is running on Railway! 🚂',
        'timestamp': datetime.now().isoformat(),
        'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'development'),
        'railway_info': {
            'deployment_id': os.environ.get('RAILWAY_DEPLOYMENT_ID', 'local'),
            'service_id': os.environ.get('RAILWAY_SERVICE_ID', 'local'),
            'no_cold_start': True
        },
        'features': [
            'No Cold Start',
            'Fast Response',
            'SSL/HTTPS',
            'Auto Deploy',
            'CORS Enabled',
            'Database Powered'
        ],
        'endpoints': ['/api/health', '/api/chat', '/api/stats', '/', '/admin']
    })

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API สำหรับการสนทนา"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'response': 'กรุณาส่งข้อมูล JSON',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        message = data.get('message', '').strip()
        user_id = data.get('user_id', 'anonymous')
        session_id = data.get('session_id', 'default')
        
        if not message:
            return jsonify({
                'error': 'Message is required',
                'response': 'กรุณาระบุข้อความที่ต้องการส่ง',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # ประมวลผลคำถาม
        start_time = datetime.now()
        response_text = find_answer(message)
        end_time = datetime.now()
        
        # คำนวณเวลาในการตอบ
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        return jsonify({
            'response': response_text,
            'html_response': bool('\n' in response_text),
            'user_id': user_id,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'processing_time_ms': round(processing_time, 2),
            'railway_info': {
                'deployment_id': os.environ.get('RAILWAY_DEPLOYMENT_ID', 'local'),
                'no_cold_start': True,
                'fast_response': True,
                'database_powered': True
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'response': 'ขออภัยครับ เกิดข้อผิดพลาดในระบบ Railway',
            'timestamp': datetime.now().isoformat(),
            'details': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """API สถิติ"""
    try:
        conn = get_db_connection()
        
        total_questions = conn.execute('SELECT COUNT(*) as count FROM questions').fetchone()['count']
        total_categories = conn.execute('SELECT COUNT(*) as count FROM categories').fetchone()['count']
        
        # สถิติเพิ่มเติม
        questions_by_category = conn.execute('''
            SELECT c.name, COUNT(q.id) as count 
            FROM categories c 
            LEFT JOIN questions q ON c.id = q.category_id 
            GROUP BY c.id, c.name
        ''').fetchall()
        
        conn.close()
        
        return jsonify({
            'total_questions': total_questions,
            'total_categories': total_categories,
            'questions_by_category': [dict(row) for row in questions_by_category],
            'timestamp': datetime.now().isoformat(),
            'railway_info': {
                'platform': 'Railway',
                'deployment_id': os.environ.get('RAILWAY_DEPLOYMENT_ID', 'local'),
                'uptime': '24/7',
                'cold_start': False,
                'database': 'SQLite'
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Database error',
            'timestamp': datetime.now().isoformat(),
            'details': str(e)
        }), 500

# Initialize database on startup
init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("🚂" + "="*60)
    print("🚂 DSD Chatbot Admin System Starting...")
    print(f"📡 Port: {port}")
    print(f"🌍 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'local')}")
    print("✅ No Cold Start")
    print("✅ Database Powered")
    print("✅ Admin Dashboard")
    print("✅ Excel Import/Export")
    print("✅ Full CRUD Operations")
    print("🚂" + "="*60)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )