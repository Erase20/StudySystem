# -*- coding: utf-8 -*-
"""
订单数据生成脚本
每次运行生成10000条订单数据并导入MySQL数据库
"""
import pymysql
import random
import time
import uuid
from datetime import datetime, timedelta

# 数据库配置
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',  # 请根据实际情况修改
    'database': 'manager',
    'charset': 'utf8mb4'
}


def get_user_ids():
    """获取所有用户ID"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM user")
    user_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return user_ids


def get_courses():
    """获取所有课程ID和价格"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT id, price, type FROM course")
    courses = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return courses


def generate_order_id():
    """生成订单号：时间戳+随机数"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_num = random.randint(100000, 999999)
    return f'ORD{timestamp}{random_num}'


def generate_orders(count: int, user_ids: list, courses: list):
    """生成订单数据"""
    orders = []
    
    for i in range(count):
        # 随机选择用户和课程
        user_id = random.choice(user_ids)
        course = random.choice(courses)
        course_id = course[0]
        original_price = course[1] or 0
        course_type = course[2] or 'VIDEO'
        
        # 计算实际价格（考虑折扣）
        discount = random.choice([1.0, 1.0, 0.9, 0.85, 0.8, 0.75])
        price = round(original_price * discount, 2)
        
        # 生成订单号
        order_id = generate_order_id()
        
        # 生成订单时间（最近一年内）
        days_ago = random.randint(1, 365)
        order_time = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        order = (
            course_id,       # course_id
            price,           # price
            order_id,        # order_id
            order_time,      # time
            user_id,         # user_id
            course_type      # course_type
        )
        orders.append(order)
    
    return orders


def batch_insert_orders(orders, batch_size=500):
    """批量插入订单数据"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    sql = """
        INSERT INTO orders (course_id, price, order_id, time, user_id, course_type)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    success = 0
    total = len(orders)
    
    for i in range(0, total, batch_size):
        batch = orders[i:i + batch_size]
        try:
            cursor.executemany(sql, batch)
            conn.commit()
            success += len(batch)
            print(f"  进度: {success}/{total} ({success*100//total}%)")
        except Exception as e:
            print(f"  批量插入失败: {e}")
            conn.rollback()
    
    cursor.close()
    conn.close()
    return success


def get_order_count():
    """获取当前订单数量"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM orders")
        result = cursor.fetchone()
        count = result[0] if result else 0
    except:
        count = 0
    cursor.close()
    conn.close()
    return count


def main():
    count = 10000  # 每次生成10000条
    
    print("=" * 50)
    print("订单数据生成器")
    print("=" * 50)
    
    # 获取用户和课程数据
    print("\n正在获取用户和课程数据...")
    user_ids = get_user_ids()
    courses = get_courses()
    
    if not user_ids:
        print("错误：没有用户数据，请先运行 gen_users.py")
        return
    if not courses:
        print("错误：没有课程数据，请先运行 gen_courses.py")
        return
    
    print(f"用户数量: {len(user_ids)}")
    print(f"课程数量: {len(courses)}")
    
    # 获取当前订单数量
    current_count = get_order_count()
    print(f"\n当前订单数量: {current_count}")
    print(f"本次生成数量: {count}")
    
    # 生成数据
    print(f"\n正在生成 {count} 条订单数据...")
    start_time = time.time()
    orders = generate_orders(count, user_ids, courses)
    gen_time = time.time() - start_time
    print(f"数据生成完成，耗时: {gen_time:.2f}秒")
    
    # 批量插入
    print(f"\n正在导入数据库...")
    start_time = time.time()
    success = batch_insert_orders(orders)
    insert_time = time.time() - start_time
    
    print(f"\n导入完成，耗时: {insert_time:.2f}秒")
    print(f"成功: {success}/{count}")
    print(f"当前总订单数: {current_count + success}")
    print("=" * 50)


if __name__ == '__main__':
    main()
