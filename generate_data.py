import pymysql
from faker import Faker
import random
from datetime import datetime, timedelta

# 初始化 Faker 生成中文数据
fake = Faker('zh_CN')

# --- MySQL 数据库连接配置 ---
# 【修改点】去掉了 database 参数，先连接到 MySQL 服务器本身
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3307,             
    "user": "root",
    "password": "example",
    "charset": "utf8mb4"
}

def create_database_and_tables(cursor):
    """在 MySQL 中创建数据库和表结构"""
    # 1. 自动创建数据库并切换
    cursor.execute("CREATE DATABASE IF NOT EXISTS testdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cursor.execute("USE testdb;")
    print("数据库 testdb 准备就绪！")

    # 2. 创建表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50),
            city VARCHAR(50),
            reg_date DATETIME
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            product_category VARCHAR(50),
            amount DECIMAL(10, 2),
            order_time DATETIME
        )
    """)
    print("表结构创建成功！")

def generate_and_insert_data(conn, cursor):
    """生成并批量插入测试数据"""
    print("开始生成 20,000 条用户数据...")
    users_data = []
    for _ in range(20000):
        reg_date = datetime.now() - timedelta(days=random.randint(0, 730))
        users_data.append((fake.name(), fake.city_name(), reg_date.strftime('%Y-%m-%d %H:%M:%S')))
    
    # MySQL 的批量插入使用 executemany
    cursor.executemany("INSERT INTO users (name, city, reg_date) VALUES (%s, %s, %s)", users_data)
    conn.commit()
    print("用户数据插入完成！")

    print("开始生成 100,000 条订单数据...")
    orders_data = []
    categories = ['3C数码', '美妆护肤', '家居生活', '生鲜食品', '服饰鞋包']
    
    for _ in range(100000):
        user_id = random.randint(1, 20000)
        category = random.choice(categories)
        amount = round(random.uniform(10.0, 5000.0), 2)
        order_time = datetime.now() - timedelta(days=random.randint(0, 365), hours=random.randint(0, 24))
        orders_data.append((user_id, category, amount, order_time.strftime('%Y-%m-%d %H:%M:%S')))

    # 分批插入防止内存溢出
    page_size = 10000
    for i in range(0, len(orders_data), page_size):
        batch = orders_data[i:i + page_size]
        cursor.executemany("INSERT INTO orders (user_id, product_category, amount, order_time) VALUES (%s, %s, %s, %s)", batch)
        conn.commit()
        print(f"   -> 已插入订单数据: {i + len(batch)} / 100000")

    print("所有测试数据生成并落库完毕！")

if __name__ == "__main__":
    try:
        # 连接数据库
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        create_database_and_tables(cursor)
        generate_and_insert_data(conn, cursor)
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"运行失败，报错信息: {e}")