# -*- coding: utf-8 -*-
"""
管理员账号演示数据生成脚本
为admin账号生成完整的学习记录、计划、笔记等数据
"""
import pymysql
import random
from datetime import datetime, timedelta

# 数据库配置
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'manager',
    'charset': 'utf8mb4'
}

# 学习记录模板
LEARNING_TEMPLATES = [
    {'course': 'Python入门到精通', 'type': 'VIDEO', 'duration': 45, 'progress': 100},
    {'course': 'Java基础入门', 'type': 'VIDEO', 'duration': 30, 'progress': 85},
    {'course': 'Vue.js实战开发', 'type': 'VIDEO', 'duration': 60, 'progress': 72},
    {'course': 'MySQL数据库基础', 'type': 'VIDEO', 'duration': 25, 'progress': 60},
    {'course': 'SpringBoot框架实战', 'type': 'VIDEO', 'duration': 50, 'progress': 45},
    {'course': 'Docker容器技术', 'type': 'TEXT', 'duration': 20, 'progress': 100},
    {'course': 'Linux命令大全', 'type': 'TEXT', 'duration': 15, 'progress': 80},
    {'course': 'React前端框架', 'type': 'VIDEO', 'duration': 55, 'progress': 30},
]

# 学习计划模板
PLAN_TEMPLATES = [
    {'title': 'Python全栈学习计划', 'content': '系统学习Python基础、Web开发、数据分析，预计3个月完成', 'daily': 60, 'progress': 75},
    {'title': '前端技能提升计划', 'content': '掌握Vue3、React、TypeScript，完成3个实战项目', 'daily': 45, 'progress': 45},
    {'title': '数据库进阶学习', 'content': '深入学习MySQL优化、Redis缓存、MongoDB，掌握高并发处理', 'daily': 30, 'progress': 20},
]

# 笔记模板
NOTE_TEMPLATES = [
    {'title': 'Python装饰器详解', 'content': '装饰器是Python的重要特性，可以在不修改原函数代码的情况下扩展功能。常见用途包括：日志记录、性能统计、权限校验等。', 'course': 'Python入门到精通'},
    {'title': 'Vue组件通信方式总结', 'content': 'Vue中组件间通信有多种方式：1. Props/$emit 父子通信 2. $parent/$children 直接访问 3. $refs 引用访问 4. EventBus 事件总线 5. Vuex/Pinia 状态管理', 'course': 'Vue.js实战开发'},
    {'title': 'MySQL索引优化原则', 'content': '索引优化是提高查询效率的关键：1. 最左前缀原则 2. 避免在索引列上使用函数 3. 选择性低的列不适合建索引 4. 联合索引注意列顺序', 'course': 'MySQL数据库基础'},
    {'title': 'Docker常用命令速查', 'content': 'docker run 运行容器 | docker ps 查看运行中 | docker stop/start 启停 | docker rm 删除 | docker images 镜像列表 | docker exec 进入容器', 'course': 'Docker容器技术'},
    {'title': 'SpringBoot自动配置原理', 'content': 'SpringBoot通过@EnableAutoConfiguration实现自动配置，根据classpath中的依赖自动装配Bean，可以通过application.yml进行自定义配置。', 'course': 'SpringBoot框架实战'},
]


def get_admin_id():
    """获取admin用户ID"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM user WHERE username = 'admin' LIMIT 1")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None


def get_courses():
    """获取课程列表"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, type FROM course LIMIT 20")
    courses = {row[1]: {'id': row[0], 'name': row[1], 'type': row[2]} for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    return courses


def clear_admin_data(admin_id):
    """清空admin现有数据"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    tables = ['learning_record', 'learning_plan', 'note']
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table} WHERE user_id = %s", (admin_id,))
        except:
            pass
    conn.commit()
    cursor.close()
    conn.close()


def generate_learning_records(admin_id, courses):
    """生成学习记录"""
    records = []
    for template in LEARNING_TEMPLATES:
        course = courses.get(template['course'], {'id': 1, 'name': template['course'], 'type': template['type']})
        for i in range(random.randint(2, 5)):
            days_ago = random.randint(1, 30)
            create_time = (datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))).strftime('%Y-%m-%d %H:%M:%S')
            update_time = create_time
            last_position = '05:' + str(random.randint(10, 59))
            records.append((admin_id, course['id'], course['name'], course['type'], template['duration'], template['progress'], last_position, create_time, update_time))
    return records


def generate_learning_plans(admin_id, courses):
    """生成学习计划"""
    plans = []
    for template in PLAN_TEMPLATES:
        course = random.choice(list(courses.values())) if courses else {'id': 1, 'name': 'Python入门'}
        start_date = (datetime.now() - timedelta(days=random.randint(5, 15))).strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        status = '进行中' if template['progress'] < 100 else '已完成'
        plans.append((template['title'], template['content'], start_date, end_date, template['daily'], template['progress'], status, admin_id, course['id'], course['name']))
    return plans


def generate_notes(admin_id, courses):
    """生成笔记"""
    notes = []
    for template in NOTE_TEMPLATES:
        course = courses.get(template['course'], {'id': 1, 'name': template['course']})
        days_ago = random.randint(1, 20)
        create_time = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        notes.append((template['title'], template['content'], create_time, admin_id, course['id'], course['name'], '05:' + str(random.randint(10, 59))))
    return notes


def batch_insert(sql, data):
    """批量插入"""
    if not data:
        return 0
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    try:
        cursor.executemany(sql, data)
        conn.commit()
        return len(data)
    except Exception as e:
        print(f"插入失败: {e}")
        conn.rollback()
        return 0
    finally:
        cursor.close()
        conn.close()


def generate_orders(admin_id, courses):
    """生成订单数据"""
    orders = []
    course_list = list(courses.values())[:8]  # 取前8门课程
    
    for i, course in enumerate(course_list):
        days_ago = random.randint(1, 60)
        order_time = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        price = random.choice([0, 29.9, 49.9, 99.0, 199.0])
        status = '已支付'
        order_no = f'ORD{datetime.now().strftime("%Y%m%d%H%M%S")}{i}'
        
        orders.append((order_no, course['id'], course['name'], price, status, order_time, admin_id))
    return orders


def clear_orders(admin_id):
    """清空admin订单"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM orders WHERE user_id = %s", (admin_id,))
        conn.commit()
    except:
        pass
    cursor.close()
    conn.close()


def main():
    print("=" * 50)
    print("管理员演示数据生成")
    print("=" * 50)
    
    admin_id = get_admin_id()
    if not admin_id:
        print("错误：未找到admin账号")
        return
    
    print(f"Admin ID: {admin_id}")
    
    courses = get_courses()
    print(f"课程数量: {len(courses)}")
    
    print("\n清空现有数据...")
    clear_admin_data(admin_id)
    clear_orders(admin_id)
    
    print("\n生成订单数据...")
    orders = generate_orders(admin_id, courses)
    sql = "INSERT INTO orders (order_no, course_id, course_name, price, status, time, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    count = batch_insert(sql, orders)
    print(f"  订单: {count}条")
    
    print("\n生成学习记录...")
    records = generate_learning_records(admin_id, courses)
    sql = "INSERT INTO learning_record (user_id, course_id, course_name, course_type, duration, progress, last_position, create_time, update_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    count = batch_insert(sql, records)
    print(f"  学习记录: {count}条")
    
    print("\n生成学习计划...")
    plans = generate_learning_plans(admin_id, courses)
    sql = "INSERT INTO learning_plan (title, content, start_date, end_date, daily_goal, progress, status, user_id, target_course_id, course_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    count = batch_insert(sql, plans)
    print(f"  学习计划: {count}条")
    
    print("\n生成笔记...")
    notes = generate_notes(admin_id, courses)
    sql = "INSERT INTO note (title, content, create_time, user_id, course_id, course_name, video_time) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    count = batch_insert(sql, notes)
    print(f"  笔记: {count}条")
    
    print("\n" + "=" * 50)
    print("演示数据生成完成！")
    print("=" * 50)
    print("\n使用admin账号登录后可查看：")
    print("  - 学习中心：学习记录、计划、笔记")
    print("  - 智能分析：用户画像、RFM分析、学习进度、智能推荐")


if __name__ == '__main__':
    main()
