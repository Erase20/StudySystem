# -*- coding: utf-8 -*-
"""
演示数据生成脚本
为学习平台和智能分析功能生成完整的演示数据
"""
import pymysql
import random
import time
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

# 学习记录数据模板
LEARNING_RECORDS = [
    {'courseName': 'Python入门到精通', 'courseType': 'VIDEO', 'duration': 45, 'progress': 100},
    {'courseName': 'Java基础入门', 'courseType': 'VIDEO', 'duration': 30, 'progress': 85},
    {'courseName': 'Vue.js实战', 'courseType': 'VIDEO', 'duration': 60, 'progress': 60},
    {'courseName': 'MySQL基础入门', 'courseType': 'VIDEO', 'duration': 25, 'progress': 40},
    {'courseName': 'Docker基础', 'courseType': 'TEXT', 'duration': 15, 'progress': 100},
    {'courseName': 'Linux命令大全', 'courseType': 'TEXT', 'duration': 20, 'progress': 75},
    {'courseName': 'SpringBoot框架', 'courseType': 'VIDEO', 'duration': 50, 'progress': 30},
    {'courseName': 'React框架入门', 'courseType': 'VIDEO', 'duration': 35, 'progress': 90},
]

# 学习计划数据模板
LEARNING_PLANS = [
    {'title': 'Python学习计划', 'content': '每天学习1小时，完成Python基础课程', 'dailyGoal': 60, 'progress': 75},
    {'title': '前端技能提升', 'content': '掌握Vue和React框架，完成实战项目', 'dailyGoal': 45, 'progress': 45},
    {'title': '数据库进阶', 'content': '深入学习MySQL和Redis，掌握优化技巧', 'dailyGoal': 30, 'progress': 20},
]

# 笔记数据模板
NOTES = [
    {'title': 'Python列表推导式', 'content': '列表推导式是Python中非常强大的特性，可以用一行代码实现循环和条件判断...', 'courseName': 'Python入门到精通'},
    {'title': 'Vue组件通信', 'content': 'Vue中组件通信有多种方式：props/$emit、$parent/$children、$refs、事件总线...', 'courseName': 'Vue.js实战'},
    {'title': 'MySQL索引优化', 'content': '索引是提高查询效率的关键，需要注意索引的选择性和最左前缀原则...', 'courseName': 'MySQL基础入门'},
    {'title': 'Docker容器管理', 'content': 'Docker容器生命周期管理：创建、启动、停止、删除、查看日志...', 'courseName': 'Docker基础'},
]


def get_user_ids():
    """获取用户ID列表"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM user LIMIT 20")
    user_ids = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return user_ids


def get_courses():
    """获取课程列表"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, type FROM course LIMIT 50")
    courses = [{'id': row[0], 'name': row[1], 'type': row[2]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return courses


def generate_learning_records(user_ids, courses):
    """生成学习记录"""
    records = []
    for user_id in user_ids[:5]:  # 为前5个用户生成记录
        for _ in range(random.randint(3, 8)):
            template = random.choice(LEARNING_RECORDS)
            course = random.choice(courses) if courses else {'id': 1, 'name': template['courseName'], 'type': template['courseType']}
            
            days_ago = random.randint(1, 30)
            record_time = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
            
            record = (
                user_id,
                course['id'],
                course['name'],
                course['type'],
                template['duration'],
                template['progress'],
                record_time
            )
            records.append(record)
    return records


def generate_learning_plans(user_ids, courses):
    """生成学习计划"""
    plans = []
    for user_id in user_ids[:3]:  # 为前3个用户生成计划
        for template in LEARNING_PLANS:
            course = random.choice(courses) if courses else {'id': 1, 'name': 'Python入门'}
            
            days_ago = random.randint(1, 10)
            start_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            status = random.choice(['进行中', '进行中', '已完成'])
            
            plan = (
                template['title'],
                template['content'],
                start_date,
                end_date,
                template['dailyGoal'],
                template['progress'],
                status,
                user_id,
                course['id'],
                course['name']
            )
            plans.append(plan)
    return plans


def generate_notes(user_ids, courses):
    """生成笔记"""
    notes = []
    for user_id in user_ids[:5]:
        for template in NOTES:
            course = random.choice(courses) if courses else {'id': 1, 'name': template['courseName']}
            
            days_ago = random.randint(1, 20)
            create_time = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
            
            note = (
                template['title'],
                template['content'],
                create_time,
                user_id,
                course['id'],
                course['name'],
                '05:' + str(random.randint(10, 59))
            )
            notes.append(note)
    return notes


def batch_insert(sql, data, batch_size=50):
    """批量插入数据"""
    if not data:
        return 0
    
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    success = 0
    total = len(data)
    
    for i in range(0, total, batch_size):
        batch = data[i:i + batch_size]
        try:
            cursor.executemany(sql, batch)
            conn.commit()
            success += len(batch)
        except Exception as e:
            print(f"  插入失败: {e}")
            conn.rollback()
    
    cursor.close()
    conn.close()
    return success


def clear_existing_data():
    """清空现有演示数据"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    tables = ['learning_record', 'learning_plan', 'note']
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            conn.commit()
            print(f"  清空 {table}")
        except:
            pass
    
    cursor.close()
    conn.close()


def main():
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 50)
    print("演示数据生成器")
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
    
    # 清空现有数据
    print("\n清空现有演示数据...")
    clear_existing_data()
    
    # 生成学习记录
    print("\n生成学习记录...")
    records = generate_learning_records(user_ids, courses)
    sql = """
        INSERT INTO learning_record (user_id, course_id, course_name, course_type, duration, progress, time)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    success = batch_insert(sql, records)
    print(f"  成功: {success}/{len(records)}")
    
    # 生成学习计划
    print("\n生成学习计划...")
    plans = generate_learning_plans(user_ids, courses)
    sql = """
        INSERT INTO learning_plan (title, content, start_date, end_date, daily_goal, progress, status, user_id, target_course_id, course_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    success = batch_insert(sql, plans)
    print(f"  成功: {success}/{len(plans)}")
    
    # 生成笔记
    print("\n生成笔记...")
    notes = generate_notes(user_ids, courses)
    sql = """
        INSERT INTO note (title, content, create_time, user_id, course_id, course_name, video_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    success = batch_insert(sql, notes)
    print(f"  成功: {success}/{len(notes)}")
    
    print("\n" + "=" * 50)
    print("演示数据生成完成！")
    print("=" * 50)
    print("\n现在可以演示：")
    print("  1. 学习中心 - 查看学习记录、计划、笔记")
    print("  2. 智能分析 - 查看用户画像、学习进度、推荐")


if __name__ == '__main__':
    main()
