from flask import Flask, jsonify
import os, time
import pymysql

app = Flask(__name__)

DB_HOST = os.getenv("MYSQL_HOST", "db")
DB_USER = os.getenv("MYSQL_USER", "appuser")
DB_PASS = os.getenv("MYSQL_PASSWORD", "apppass")
DB_NAME = os.getenv("MYSQL_DATABASE", "appdb")

for _ in range(30):
    try:
        conn = pymysql.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASS,
            database=DB_NAME, autocommit=True
        )
        break
    except:
        time.sleep(1)
else:
    raise RuntimeError("MySQL not reachable")

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/")
def index():
    with conn.cursor() as cur:
        cur.execute("INSERT INTO visits VALUES (NULL, NOW())")
        cur.execute("SELECT COUNT(*) FROM visits")
        (count,) = cur.fetchone()
    return jsonify(message="Hello from Flask + MySQL", visits=count)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
