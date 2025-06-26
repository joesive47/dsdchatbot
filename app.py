from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ข้อมูลคำถาม-คำตอบง่ายๆ
qa_data = {
    'สวัสดี': 'สวัสดีครับ! ยินดีต้อนรับสู่ระบบ LMS ขับเคลื่อนโดย Railway! 🚂',
    'hello': 'Hello! Welcome to Railway-powered LMS! 🚀',
    'คอร์สเรียนมีอะไรบ้าง': 'เรามีคอร์สเรียนหลากหลาย:\n- การเขียนโปรแกรม Python\n- การออกแบบ UI/UX\n- การวิเคราะห์ข้อมูล\n- การพัฒนาเว็บไซต์\n- การตลาดดิจิทัล',
    'ราคาคอร์สเท่าไหร่': 'ราคาคอร์สแต่ละหลักสูตร:\n- คอร์สพื้นฐาน: 2,500-5,000 บาท\n- คอร์สขั้นกลาง: 5,000-8,000 บาท\n- คอร์สขั้นสูง: 8,000-12,000 บาท',
    'วิธีการสมัครเรียน': 'การสมัครเรียนทำได้ง่ายๆ:\n1. เลือกคอร์สที่สนใจ\n2. กดปุ่ม "สมัครเรียน"\n3. กรอกข้อมูลส่วนตัว\n4. ชำระเงินค่าเรียน\n5. เริ่มเรียนได้ทันที',
    'ติดต่อเจ้าหน้าที่': 'สามารถติดต่อเจ้าหน้าที่ได้หลายช่องทาง:\n📞 โทร: 02-123-4567\n📧 อีเมล: info@lms.com\n💬 Line: @lmssupport\n🕒 เวลาทำการ: จันทร์-ศุกร์ 9:00-18:00',
    'railway ทดสอบ': 'ยอดเยี่ยม! Railway ทำงานได้ปกติ 🚂 ไม่มี cold start และตอบสนองเร็วมาก!',
    'ทดสอบ railway': 'สวัสดีจาก Railway! 🚂 ระบบนี้:\n✅ ไม่มี cold start\n✅ ตอบสนองเร็ว\n✅ SSL ฟรี\n✅ Deploy ง่าย\n\nพร้อมให้บริการตลอด 24/7!',
    'ขอบคุณ': 'ยินดีครับ! หากมีคำถามเพิ่มเติม สามารถสอบถามได้ตลอดเวลา 😊',
    'thank you': 'You\'re welcome! Feel free to ask anytime! 😊'
}

@app.route('/')
def home():
    railway_info = {
        'deployment_id': os.environ.get('RAILWAY_DEPLOYMENT_ID', 'local'),
        'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'development'),
        'service_id': os.environ.get('RAILWAY_SERVICE_ID', 'local')
    }
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚂 Railway Flask Chatbot</title>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .success {{ color: #28a745; }}
            .info {{ background: #f0f8ff; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .endpoints {{ background: #f8f9fa; padding: 15px; border-radius: 5px; }}
            pre {{ background: #e9ecef; padding: 10px; border-radius: 3px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚂 Railway Flask Chatbot API</h1>
            <p class="success">✅ ระบบทำงานปกติบน Railway!</p>
        </div>
        
        <div class="info">
            <h3>📊 Railway Information:</h3>
            <ul>
                <li><strong>Deployment ID:</strong> {railway_info['deployment_id']}</li>
                <li><strong>Environment:</strong> {railway_info['environment']}</li>
                <li><strong>Service ID:</strong> {railway_info['service_id']}</li>
                <li><strong>No Cold Start:</strong> ✅ Yes</li>
                <li><strong>SSL/HTTPS:</strong> ✅ Enabled</li>
            </ul>
        </div>
        
        <div class="endpoints">
            <h3>🔗 Available Endpoints:</h3>
            <ul>
                <li><a href="/api/health">GET /api/health</a> - Health check</li>
                <li><strong>POST /api/chat</strong> - Chat endpoint</li>
                <li><a href="/api/stats">GET /api/stats</a> - Statistics</li>
            </ul>
        </div>
        
        <div class="info">
            <h3>💬 Test Chat API:</h3>
            <p>ส่ง POST request ไปที่ <code>/api/chat</code> ด้วย JSON:</p>
            <pre>{{"message": "สวัสดี", "user_id": "test", "session_id": "test_session"}}</pre>
            
            <h4>คำถามตัวอย่าง:</h4>
            <ul>
                <li>"สวัสดี" - ทักทาย</li>
                <li>"คอร์สเรียนมีอะไรบ้าง" - ดูคอร์ส</li>
                <li>"ราคาคอร์สเท่าไหร่" - ดูราคา</li>
                <li>"railway ทดสอบ" - ทดสอบ Railway</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <p>🚂 Powered by Railway - No Cold Start, Always Fast!</p>
        </div>
    </body>
    </html>
    '''

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'Railway Flask Chatbot is running! 🚂',
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
            'CORS Enabled'
        ],
        'endpoints': ['/api/health', '/api/chat', '/api/stats', '/']
    })

@app.route('/api/chat', methods=['POST'])
def chat():
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
        
        # ตรวจสอบว่าเป็น HTML response หรือไม่
        is_html = bool('\n' in response_text)
        
        return jsonify({
            'response': response_text,
            'html_response': is_html,
            'user_id': user_id,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'processing_time_ms': round(processing_time, 2),
            'railway_info': {
                'deployment_id': os.environ.get('RAILWAY_DEPLOYMENT_ID', 'local'),
                'no_cold_start': True,
                'fast_response': True
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
def stats():
    return jsonify({
        'total_questions': len(qa_data),
        'available_keywords': list(qa_data.keys()),
        'timestamp': datetime.now().isoformat(),
        'railway_info': {
            'platform': 'Railway',
            'deployment_id': os.environ.get('RAILWAY_DEPLOYMENT_ID', 'local'),
            'uptime': '24/7',
            'cold_start': False
        }
    })

def find_answer(user_input):
    """หาคำตอบจากคำถาม"""
    user_input_lower = user_input.lower()
    
    # ตรวจสอบคำตอบที่ตรงกันแน่นอน
    for question, answer in qa_data.items():
        if question.lower() in user_input_lower:
            return answer
    
    # ตรวจสอบคำสำคัญ
    if 'คอร์ส' in user_input or 'เรียน' in user_input:
        return qa_data['คอร์สเรียนมีอะไรบ้าง']
    elif 'ราคา' in user_input or 'เท่าไหร่' in user_input:
        return qa_data['ราคาคอร์สเท่าไหร่']
    elif 'สมัคร' in user_input:
        return qa_data['วิธีการสมัครเรียน']
    elif 'ติดต่อ' in user_input:
        return qa_data['ติดต่อเจ้าหน้าที่']
    elif 'railway' in user_input_lower or 'ทดสอบ' in user_input:
        return qa_data['railway ทดสอบ']
    else:
        return 'ขออภัย ฉันไม่เข้าใจคำถามของคุณ 😅\n\nลองถามว่า:\n- "สวัสดี"\n- "คอร์สเรียนมีอะไรบ้าง"\n- "ราคาคอร์สเท่าไหร่"\n- "railway ทดสอบ"\n\n🚂 Powered by Railway'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("🚂" + "="*50)
    print("🚂 Starting Railway Flask Chatbot...")
    print(f"📡 Port: {port}")
    print(f"🌍 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'local')}")
    print("✅ No Cold Start")
    print("✅ Fast Response")
    print("✅ CORS Enabled")
    print("🚂" + "="*50)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )