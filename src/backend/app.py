from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import uuid

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://zhucan.xyz"}}, supports_credentials=True)

db_config = {
    "host": "localhost",  # 或者改成你数据库实际主机名
    "user": "junxibao",
    "password": "Bjx81402",
    "database": "health"
}

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        # ✅ 尝试读取 JSON（加 force=True 以确保 Flask 不依赖 headers 判断）
        data = request.get_json(force=True)
        print("收到的数据：", data)

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"success": False, "message": "缺少用户名或密码"}), 400

        # ✅ 连接数据库
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            return jsonify({"success": True, "userId": user["user_id"]})
        else:
            return jsonify({"success": False, "message": "用户名或密码错误"}), 401

    except Exception as e:
        print("❌ 错误：", e)
        return jsonify({"success": False, "message": "服务器错误", "error": str(e)}), 500

@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json(force=True)
        print("注册收到的数据：", data)

        username = data.get("username")
        password = data.get("password")
        age = data.get("age")
        try:
            age = int(age)
            if age < 1 or age > 120:
                return jsonify({"success": False, "message": "年龄必须是1-120之间的整数"}), 400
        except (TypeError, ValueError):
            return jsonify({"success": False, "message": "年龄格式不正确"}), 400

        if not username or not password or age is None:
            return jsonify({"success": False, "message": "缺少用户名、密码或年龄"}), 400

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "用户名已存在"}), 409

        user_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO users (user_id, username, password, age) VALUES (%s, %s, %s, %s)",
            (user_id, username, password, age)
        )
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "注册成功"})

    except Exception as e:
        print("❌ 注册错误：", e)
        return jsonify({"success": False, "message": "服务器错误", "error": str(e)}), 500

@app.route('/readdata', methods=['POST', 'OPTIONS'])
def readdata():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.get_json(force=True)
        print("读取数据收到的请求：", data)

        # 获取前端传递的参数
        table_name = data.get("table_name")
        user_id = data.get("user_id")
        username = data.get("username")
        
        # 参数校验
        if not table_name:
            return jsonify({"success": False, "message": "缺少表名参数"}), 400

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # 构建查询条件
        query = f"SELECT * FROM {table_name}"
        params = []
        
        if user_id:
            query += " WHERE user_id = %s"
            params.append(user_id)
        elif username:
            query += " WHERE username = %s"
            params.append(username)
        
        print(f"执行查询: {query} 参数: {params}")
        
        cursor.execute(query, params)
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "success": True, 
            "message": "数据读取成功",
            "data": results,
            "count": len(results)
        })

    except Exception as e:
        print("❌ 读取数据错误：", e)
        return jsonify({"success": False, "message": "服务器错误", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(
    host='0.0.0.0',
    port=5000,
    ssl_context=(
        '/etc/letsencrypt/live/zhucan.xyz/fullchain.pem',
        '/etc/letsencrypt/live/zhucan.xyz/privkey.pem'
    )
)