# -*- coding: utf-8 -*-
"""
用户聚类数据生成脚本（500用户以内）
生成具有明显聚类特征的用户数据，同时联动生成关联表数据
支持 K-Means / DBSCAN 等聚类算法

用户聚类群体设计（5类）：
  1. 高价值会员用户 (~60人)：高积分、高余额、会员、高频签到、多订单
  2. 活跃免费用户  (~100人)：中等积分、低余额、非会员、活跃签到、少订单
  3. 沉默付费用户  (~80人)：低积分、高余额、非会员、几乎不签到、有大额订单
  4. 新手用户     (~150人)：极低积分、极低余额、非会员、几乎无活动
  5. 忠实老用户   (~110人)：中高积分、中高余额、部分会员、高频签到、多评论
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

# 预定义姓名
SURNAMES = ['张', '王', '李', '赵', '刘', '陈', '杨', '黄', '周', '吴', '徐', '孙',
            '马', '朱', '胡', '郭', '何', '林', '罗', '高', '郑', '梁', '谢', '宋',
            '唐', '许', '韩', '冯', '邓', '曹', '彭', '曾', '萧', '田', '董', '潘']
MALE_NAMES = ['伟', '强', '磊', '军', '勇', '杰', '涛', '明', '超', '华', '刚', '辉',
              '鹏', '斌', '宇', '浩', '凯', '俊', '建', '志', '峰', '波', '飞', '龙']
FEMALE_NAMES = ['芳', '娜', '敏', '静', '丽', '燕', '玲', '婷', '霞', '雪', '梅', '莉',
                '萍', '琳', '倩', '颖', '欣', '洁', '慧', '莹', '薇', '妍', '雯', '琪']

# 评论内容模板
COMMENT_TEMPLATES = [
    '讲得很好，受益匪浅', '课程内容很实用', '老师讲解清晰', '希望能出更多类似的课',
    '入门必学', '内容很充实', '性价比很高', '学到了很多新知识',
    '讲解深入浅出', '推荐给大家', '课程质量不错', '适合初学者',
    '干货满满', '通俗易懂', '很有帮助', '非常实用的课程',
    '学完之后收获很大', '内容详细', '老师很专业', '好评',
]

# 课程名称模板（用于learning_record）
COURSE_NAMES = ['Java基础入门', 'Python数据分析', 'Vue全套教程', 'Spring Boot实战', 'MySQL优化',
                '前端开发入门', '数据结构与算法', '设计模式', '微服务架构', 'Linux运维',
                'Redis缓存实战', 'Docker容器技术', 'React框架入门', '大数据入门', '机器学习基础']


def generate_name():
    """生成随机中文姓名"""
    surname = random.choice(SURNAMES)
    gender = random.choice(['男', '女'])
    name_pool = MALE_NAMES if gender == '男' else FEMALE_NAMES
    if random.random() < 0.55:
        full_name = surname + random.choice(name_pool)
    else:
        full_name = surname + random.choice(name_pool) + random.choice(name_pool)
    return full_name


def generate_phone():
    """生成随机手机号"""
    prefixes = ['130', '131', '133', '135', '136', '137', '138', '139',
                '150', '151', '152', '153', '155', '156', '157', '158',
                '180', '181', '182', '183', '185', '186', '187', '188']
    return random.choice(prefixes) + ''.join([str(random.randint(0, 9)) for _ in range(8)])


def random_date_in_range(start_str, end_str):
    """生成范围内随机日期字符串"""
    start = datetime.strptime(start_str, '%Y-%m-%d')
    end = datetime.strptime(end_str, '%Y-%m-%d')
    delta = (end - start).days
    if delta <= 0:
        delta = 1
    random_days = random.randint(0, delta)
    return (start + timedelta(days=random_days)).strftime('%Y-%m-%d')


def generate_cluster_users(course_ids):
    """
    按聚类生成500个用户，返回：
      users           -> user表数据
      orders_list     -> orders表数据
      signins         -> signin表数据
      comments        -> comment表数据
      learning_records -> learning_record表数据
    course_ids: 数据库中实际存在的课程ID列表
    """
    users = []
    orders_list = []
    signins = []
    comments = []
    learning_records = []

    uid = 1  # 起始用户ID（配合清空后AUTO_INCREMENT=1）

    # ===================== 演示用户（role=ADMIN，可访问全部功能） =====================
    # 从实际课程ID中随机选5个作为演示用户的课程
    demo_cids = random.sample(course_ids, min(5, len(course_ids)))
    users.append({
        'id': uid, 'username': 'demo', 'password': '123456',
        'name': '演示用户', 'phone': '13800000001',
        'email': 'demo@learn.com',
        'avatar': 'https://api.dicebear.com/7.x/avataaars/svg?seed=demo',
        'member': '是', 'score': 2500, 'account': 15000.00, 'role': 'ADMIN'
    })
    # 演示用户签到: 60天
    base_date = datetime(2024, 1, 1)
    for d in random.sample(range(365), 60):
        day_str = (base_date + timedelta(days=d)).strftime('%Y-%m-%d')
        signins.append({'user_id': uid, 'time': day_str + ' 08:00:00', 'day': day_str})
    # 演示用户订单: 5个不同课程
    for cid in demo_cids:
        orders_list.append({
            'course_id': cid, 'price': round(random.uniform(50, 200), 2),
            'order_id': f'ORD_DEMO_{cid}',
            'time': random_date_in_range('2024-01-01', '2024-12-31'),
            'user_id': uid, 'course_type': random.choice(['视频课程', '实战课程'])
        })
    # 演示用户评论: 5条
    for cid in demo_cids:
        comments.append({
            'user_id': uid, 'course_id': cid,
            'time': random_date_in_range('2024-03-01', '2024-12-31') + ' 20:00:00',
            'content': random.choice(COMMENT_TEMPLATES), 'parent_id': 0
        })
    # 演示用户学习记录: 5门课，高进度
    for cid in demo_cids:
        learning_records.append({
            'user_id': uid, 'course_id': cid,
            'course_name': COURSE_NAMES[cid % len(COURSE_NAMES)],
            'course_type': random.choice(['视频课程', '实战课程']),
            'duration': random.randint(300, 800),
            'progress': random.randint(60, 100),
            'create_time': random_date_in_range('2024-01-01', '2024-06-30'),
            'update_time': random_date_in_range('2024-07-01', '2024-12-31')
        })
    uid += 1

    # ===================== 群体1: 高价值会员用户 (~60人) =====================
    for _ in range(60):
        score = random.randint(1500, 3000)
        account = round(random.uniform(8000, 20000), 2)
        member = '是'
        users.append({
            'id': uid, 'username': f'user{uid}', 'password': '123456',
            'name': generate_name(), 'phone': generate_phone(),
            'email': f'user{uid}@qq.com',
            'avatar': f'https://api.dicebear.com/7.x/avataaars/svg?seed={uid}',
            'member': member, 'score': score, 'account': account, 'role': 'USER'
        })
        # 高频签到: 30~90天
        sign_count = random.randint(30, 90)
        base_date = datetime(2024, 1, 1)
        for d in random.sample(range(365), min(sign_count, 365)):
            day_str = (base_date + timedelta(days=d)).strftime('%Y-%m-%d')
            signins.append({'user_id': uid, 'time': day_str + ' 08:30:00', 'day': day_str})
        # 多订单: 3~8个
        for _ in range(random.randint(3, 8)):
            course_id = random.choice(course_ids)
            price = round(random.uniform(50, 300), 2)
            t = random_date_in_range('2024-01-01', '2024-12-31')
            orders_list.append({
                'course_id': course_id, 'price': price,
                'order_id': f'ORD{uid}{random.randint(1000,9999)}',
                'time': t, 'user_id': uid, 'course_type': random.choice(['视频课程', '实战课程'])
            })
        # 多评论: 2~5条
        for _ in range(random.randint(2, 5)):
            t = random_date_in_range('2024-03-01', '2024-12-31')
            comments.append({
                'user_id': uid, 'course_id': random.choice(course_ids),
                'time': t + ' 20:00:00',
                'content': random.choice(COMMENT_TEMPLATES), 'parent_id': 0
            })
        # 学习记录: 3~6门课，高时长，高进度
        for _ in range(random.randint(3, 6)):
            cid = random.choice(course_ids)
            learning_records.append({
                'user_id': uid, 'course_id': cid,
                'course_name': random.choice(COURSE_NAMES),
                'course_type': random.choice(['视频课程', '实战课程']),
                'duration': random.randint(300, 800),
                'progress': random.randint(65, 100),
                'create_time': random_date_in_range('2024-01-01', '2024-06-30'),
                'update_time': random_date_in_range('2024-07-01', '2024-12-31')
            })
        uid += 1

    # ===================== 群体2: 活跃免费用户 (~100人) =====================
    for _ in range(100):
        score = random.randint(500, 1500)
        account = round(random.uniform(100, 2000), 2)
        member = '否'
        users.append({
            'id': uid, 'username': f'user{uid}', 'password': '123456',
            'name': generate_name(), 'phone': generate_phone(),
            'email': f'user{uid}@163.com',
            'avatar': f'https://api.dicebear.com/7.x/avataaars/svg?seed={uid}',
            'member': member, 'score': score, 'account': account, 'role': 'USER'
        })
        # 高频签到: 40~120天（比会员还活跃）
        sign_count = random.randint(40, 120)
        base_date = datetime(2024, 1, 1)
        for d in random.sample(range(365), min(sign_count, 365)):
            day_str = (base_date + timedelta(days=d)).strftime('%Y-%m-%d')
            signins.append({'user_id': uid, 'time': day_str + ' 09:00:00', 'day': day_str})
        # 极少订单: 0~1个
        if random.random() < 0.3:
            course_id = random.choice(course_ids)
            t = random_date_in_range('2024-06-01', '2024-12-31')
            orders_list.append({
                'course_id': course_id, 'price': round(random.uniform(10, 80), 2),
                'order_id': f'ORD{uid}{random.randint(1000,9999)}',
                'time': t, 'user_id': uid, 'course_type': '视频课程'
            })
        # 少量评论: 0~2条
        for _ in range(random.randint(0, 2)):
            t = random_date_in_range('2024-06-01', '2024-12-31')
            comments.append({
                'user_id': uid, 'course_id': random.choice(course_ids),
                'time': t + ' 19:00:00',
                'content': random.choice(COMMENT_TEMPLATES), 'parent_id': 0
            })
        # 学习记录: 2~4门课，中等时长，中等进度
        for _ in range(random.randint(2, 4)):
            cid = random.choice(course_ids)
            learning_records.append({
                'user_id': uid, 'course_id': cid,
                'course_name': random.choice(COURSE_NAMES),
                'course_type': '视频课程',
                'duration': random.randint(100, 400),
                'progress': random.randint(30, 70),
                'create_time': random_date_in_range('2024-04-01', '2024-09-30'),
                'update_time': random_date_in_range('2024-10-01', '2024-12-31')
            })
        uid += 1

    # ===================== 群体3: 沉默付费用户 (~80人) =====================
    for _ in range(80):
        score = random.randint(100, 500)
        account = round(random.uniform(5000, 15000), 2)
        member = '否'
        users.append({
            'id': uid, 'username': f'user{uid}', 'password': '123456',
            'name': generate_name(), 'phone': generate_phone(),
            'email': f'user{uid}@gmail.com',
            'avatar': f'https://api.dicebear.com/7.x/avataaars/svg?seed={uid}',
            'member': member, 'score': score, 'account': account, 'role': 'USER'
        })
        # 极少签到: 0~5天
        base_date = datetime(2024, 1, 1)
        for d in random.sample(range(365), random.randint(0, 5)):
            day_str = (base_date + timedelta(days=d)).strftime('%Y-%m-%d')
            signins.append({'user_id': uid, 'time': day_str + ' 22:00:00', 'day': day_str})
        # 大额订单: 1~3个，单价高
        for _ in range(random.randint(1, 3)):
            course_id = random.choice(course_ids)
            price = round(random.uniform(200, 500), 2)
            t = random_date_in_range('2024-01-01', '2024-12-31')
            orders_list.append({
                'course_id': course_id, 'price': price,
                'order_id': f'ORD{uid}{random.randint(1000,9999)}',
                'time': t, 'user_id': uid, 'course_type': '实战课程'
            })
        # 几乎不评论
        # 学习记录: 0~1门课，极低时长
        if random.random() < 0.4:
            cid = random.choice(course_ids)
            learning_records.append({
                'user_id': uid, 'course_id': cid,
                'course_name': random.choice(COURSE_NAMES),
                'course_type': '实战课程',
                'duration': random.randint(10, 60),
                'progress': random.randint(5, 25),
                'create_time': random_date_in_range('2024-06-01', '2024-12-31'),
                'update_time': random_date_in_range('2024-06-01', '2024-12-31')
            })
        uid += 1

    # ===================== 群体4: 新手用户 (~150人) =====================
    for _ in range(150):
        score = random.randint(0, 200)
        account = round(random.uniform(0, 500), 2)
        member = '否'
        users.append({
            'id': uid, 'username': f'user{uid}', 'password': '123456',
            'name': generate_name(), 'phone': generate_phone(),
            'email': f'user{uid}@qq.com',
            'avatar': f'https://api.dicebear.com/7.x/avataaars/svg?seed={uid}',
            'member': member, 'score': score, 'account': account, 'role': 'USER'
        })
        # 极少签到: 0~3天
        base_date = datetime(2024, 9, 1)
        for d in random.sample(range(120), random.randint(0, 3)):
            day_str = (base_date + timedelta(days=d)).strftime('%Y-%m-%d')
            signins.append({'user_id': uid, 'time': day_str + ' 21:00:00', 'day': day_str})
        # 无订单，无评论
        # 学习记录: 0~1门课，极低时长，极低进度
        if random.random() < 0.15:
            cid = random.choice(course_ids)
            learning_records.append({
                'user_id': uid, 'course_id': cid,
                'course_name': random.choice(COURSE_NAMES),
                'course_type': '视频课程',
                'duration': random.randint(5, 30),
                'progress': random.randint(0, 10),
                'create_time': random_date_in_range('2024-10-01', '2024-12-31'),
                'update_time': random_date_in_range('2024-10-01', '2024-12-31')
            })
        uid += 1

    # ===================== 群体5: 忠实老用户 (~110人) =====================
    for _ in range(110):
        score = random.randint(800, 2500)
        account = round(random.uniform(3000, 8000), 2)
        member = random.choices(['是', '否'], weights=[45, 55])[0]  # 45%会员
        users.append({
            'id': uid, 'username': f'user{uid}', 'password': '123456',
            'name': generate_name(), 'phone': generate_phone(),
            'email': f'user{uid}@126.com',
            'avatar': f'https://api.dicebear.com/7.x/avataaars/svg?seed={uid}',
            'member': member, 'score': score, 'account': account, 'role': 'USER'
        })
        # 高频签到: 50~150天
        sign_count = random.randint(50, 150)
        base_date = datetime(2023, 6, 1)
        days_total = (datetime(2024, 12, 31) - base_date).days
        for d in random.sample(range(days_total), min(sign_count, days_total)):
            day_str = (base_date + timedelta(days=d)).strftime('%Y-%m-%d')
            signins.append({'user_id': uid, 'time': day_str + ' 07:30:00', 'day': day_str})
        # 中等订单: 2~5个
        for _ in range(random.randint(2, 5)):
            course_id = random.choice(course_ids)
            price = round(random.uniform(30, 200), 2)
            t = random_date_in_range('2023-06-01', '2024-12-31')
            orders_list.append({
                'course_id': course_id, 'price': price,
                'order_id': f'ORD{uid}{random.randint(1000,9999)}',
                'time': t, 'user_id': uid, 'course_type': random.choice(['视频课程', '实战课程'])
            })
        # 多评论: 1~4条
        for _ in range(random.randint(1, 4)):
            t = random_date_in_range('2023-09-01', '2024-12-31')
            comments.append({
                'user_id': uid, 'course_id': random.choice(course_ids),
                'time': t + ' 21:30:00',
                'content': random.choice(COMMENT_TEMPLATES), 'parent_id': 0
            })
        # 学习记录: 2~5门课，高时长，高进度
        for _ in range(random.randint(2, 5)):
            cid = random.choice(course_ids)
            learning_records.append({
                'user_id': uid, 'course_id': cid,
                'course_name': random.choice(COURSE_NAMES),
                'course_type': random.choice(['视频课程', '实战课程']),
                'duration': random.randint(200, 700),
                'progress': random.randint(50, 95),
                'create_time': random_date_in_range('2023-06-01', '2024-06-30'),
                'update_time': random_date_in_range('2024-07-01', '2024-12-31')
            })
        uid += 1

    return users, orders_list, signins, comments, learning_records


def main():
    print("=" * 60)
    print("  用户聚类数据生成器（500用户，5类聚类群体）")
    print("=" * 60)

    # 连接数据库
    print("\n[1/4] 连接数据库...")
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    # 查询实际存在的课程ID（确保评论/订单/学习记录引用有效课程）
    cursor.execute("SELECT id FROM course")
    course_ids = [row[0] for row in cursor.fetchall()]
    if not course_ids:
        print("  [错误] 课程表为空，请先导入课程数据！")
        cursor.close()
        conn.close()
        return
    print(f"  检测到 {len(course_ids)} 门课程，ID范围: {min(course_ids)}~{max(course_ids)}")

    # 生成数据
    print("\n[2/4] 生成聚类用户数据...")
    t0 = time.time()
    users, orders_list, signins, comments, learning_records = generate_cluster_users(course_ids)
    print(f"  用户数: {len(users)}")
    print(f"  订单数: {len(orders_list)}")
    print(f"  签到数: {len(signins)}")
    print(f"  评论数: {len(comments)}")
    print(f"  学习记录数: {len(learning_records)}")
    print(f"  生成耗时: {time.time()-t0:.2f}s")

    # 清空整张用户表及所有关联数据
    print("\n[3/4] 清空用户表及关联数据...")
    cursor.execute("SELECT COUNT(*) FROM user")
    old_count = cursor.fetchone()[0]
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM signin")
    cursor.execute("DELETE FROM comment")
    cursor.execute("DELETE FROM scoreorder")
    cursor.execute("DELETE FROM fileorder")
    cursor.execute("DELETE FROM recharge_record")
    cursor.execute("DELETE FROM user_cluster")
    cursor.execute("DELETE FROM learning_record")
    cursor.execute("DELETE FROM learning_plan")
    cursor.execute("DELETE FROM note")
    cursor.execute("DELETE FROM user")
    # 重置自增ID，让新用户从1开始
    cursor.execute("ALTER TABLE user AUTO_INCREMENT = 1")
    conn.commit()
    print(f"  已清空 {old_count} 条用户及全部关联数据，ID已重置")

    # 插入新数据
    print("\n[4/4] 插入新聚类用户数据...")

    # 插入用户（显式指定id，确保关联数据匹配）
    user_sql = """INSERT INTO user (id, username, password, name, phone, email, avatar, member, score, account, role)
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    user_rows = [(u['id'], u['username'], u['password'], u['name'], u['phone'], u['email'],
                  u['avatar'], u['member'], u['score'], u['account'], u['role']) for u in users]
    cursor.executemany(user_sql, user_rows)
    conn.commit()
    print(f"  用户插入: {len(users)} 条 [OK]")

    # 插入订单
    if orders_list:
        order_sql = """INSERT INTO orders (course_id, price, order_id, time, user_id, course_type)
                       VALUES (%s, %s, %s, %s, %s, %s)"""
        order_rows = [(o['course_id'], o['price'], o['order_id'], o['time'], o['user_id'], o['course_type'])
                      for o in orders_list]
        cursor.executemany(order_sql, order_rows)
        conn.commit()
        print(f"  订单插入: {len(orders_list)} 条 [OK]")

    # 插入签到（批量）
    if signins:
        signin_sql = """INSERT INTO signin (user_id, time, day) VALUES (%s, %s, %s)"""
        signin_rows = [(s['user_id'], s['time'], s['day']) for s in signins]
        batch = 500
        for i in range(0, len(signin_rows), batch):
            cursor.executemany(signin_sql, signin_rows[i:i+batch])
            conn.commit()
        print(f"  签到插入: {len(signins)} 条 [OK]")

    # 插入评论
    if comments:
        comment_sql = """INSERT INTO comment (user_id, course_id, time, content, parent_id)
                         VALUES (%s, %s, %s, %s, %s)"""
        comment_rows = [(c['user_id'], c['course_id'], c['time'], c['content'], c['parent_id'])
                        for c in comments]
        cursor.executemany(comment_sql, comment_rows)
        conn.commit()
        print(f"  评论插入: {len(comments)} 条 [OK]")

    # 插入学习记录
    if learning_records:
        lr_sql = """INSERT INTO learning_record (user_id, course_id, course_name, course_type,
                    duration, progress, create_time, update_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        lr_rows = [(r['user_id'], r['course_id'], r['course_name'], r['course_type'],
                    r['duration'], r['progress'], r['create_time'], r['update_time'])
                   for r in learning_records]
        cursor.executemany(lr_sql, lr_rows)
        conn.commit()
        print(f"  学习记录插入: {len(learning_records)} 条 [OK]")

    cursor.close()
    conn.close()

    print("\n" + "=" * 60)
    print("  数据生成完成！")
    print("=" * 60)
    print("\n聚类群体分布：")
    print("  群体1 - 高价值会员:  60人 (高积分/高余额/会员/高频签到/多订单/高学习时长)")
    print("  群体2 - 活跃免费用户: 100人 (中积分/低余额/非会员/高频签到/少订单/中等学习)")
    print("  群体3 - 沉默付费用户:  80人 (低积分/高余额/非会员/极少签到/大额订单/极低学习)")
    print("  群体4 - 新手用户:    150人 (极低积分/极低余额/非会员/几乎无活动/几乎无学习)")
    print("  群体5 - 忠实老用户:  110人 (中高积分/中高余额/部分会员/高频签到/多评论/高学习时长)")
    print("\n聚类6维特征: 购买数/总消费/学习时长/平均进度/签到天数/评论数")
    print("  演示用户: demo/123456 (role=ADMIN, 可访问全部前后台功能)")
    print("=" * 60)


if __name__ == '__main__':
    main()
