from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import bcrypt
import jwt
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

DATABASE_URL = "postgresql://ayupilot_user:J0ONf89tkE82JITlILk8eHdPf53a5L2E@dpg-d7i8ghgsfn5c73e5ka4g-a.ohio-postgres.render.com/ayupilot"
SECRET_KEY = "your-secret-key"

def get_db():
    return psycopg2.connect(DATABASE_URL)

@app.route('/health/', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'ayupilot-backend',
        'version': '1.0.0'
    })

@app.route('/api/v1/login/', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("SELECT id, password, \"firstName\", \"lastName\", email FROM users WHERE email = %s AND is_verified = true", (email,))
        user = cur.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            token = jwt.encode({
                'user_id': str(user[0]),
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, SECRET_KEY, algorithm='HS256')
            
            return jsonify({
                'access': token,
                'refresh': token,
                'userId': str(user[0]),
                'firstName': user[2],
                'lastName': user[3],
                'email': user[4]
            })
        
        return jsonify({'detail': 'Invalid credentials'}), 400
        
    except Exception as e:
        return jsonify({'detail': str(e)}), 500

@app.route('/api/v1/register/', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        firstName = data.get('firstName')
        lastName = data.get('lastName')
        phone = data.get('phone')
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO users (email, password, "firstName", "lastName", phone, is_active, is_verified, level)
            VALUES (%s, %s, %s, %s, %s, true, true, 1)
            RETURNING id, "firstName", "lastName", email
        """, (email, hashed.decode('utf-8'), firstName, lastName, phone))
        
        user = cur.fetchone()
        conn.commit()
        
        token = jwt.encode({
            'user_id': str(user[0]),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'access': token,
            'refresh': token,
            'userId': str(user[0]),
            'firstName': user[1],
            'lastName': user[2],
            'email': user[3]
        }), 201
        
    except Exception as e:
        return jsonify({'detail': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)