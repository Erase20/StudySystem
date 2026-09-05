# -*- coding: utf-8 -*-
"""
在线学习管理系统 - 扩展爬虫模块
支持：真实API爬取、用户数据生成、积分商品、评论数据、JSON/CSV导入
"""
import requests
import pymysql
import random
import time
import json
import csv
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class BaseSpider:
    """爬虫基类"""
    
    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.conn = None
        self.cursor = None
        self._connect_db()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
    
    def _connect_db(self):
        """连接数据库"""
        try:
            self.conn = pymysql.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            print("数据库连接成功")
        except Exception as e:
            print(f"数据库连接失败: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("数据库连接已关闭")


class UserSpider(BaseSpider):
    """用户数据爬虫 - 生成模拟用户数据"""
    
    def generate_users(self, count: int = 50) -> List[Dict]:
        """生成模拟用户数据"""
        users = []
        # 预定义姓氏和名字，提高生成速度
        surnames = ['张', '王', '李', '赵', '刘', '陈', '杨', '黄', '周', '吴', '徐', '孙', '马', '朱', '胡', '郭', '何', '林', '罗', '高']
        male_names = ['伟', '强', '磊', '军', '勇', '杰', '涛', '明', '超', '华', '刚', '辉', '鹏', '斌', '宇', '浩', '凯', '俊', '建', '志']
        female_names = ['芳', '娜', '敏', '静', '丽', '艳', '燕', '玲', '婷', '霞', '雪', '梅', '红', '娟', '莉', '萍', '琳', '倩', '颖', '欣']
        
        for i in range(count):
            surname = random.choice(surnames)
            gender = random.choice(['male', 'female'])
            name_pool = male_names if gender == 'male' else female_names
            full_name = surname + random.choice(name_pool) + random.choice(['', random.choice(name_pool)])
            
            user = {
                'username': f'user{10000 + i}',
                'password': '123456',
                'name': full_name,
                'phone': f'1{random.choice(["3","5","7","8","9"])}{random.randint(100000000, 999999999)}',
                'email': f'user{10000 + i}@qq.com',
                'avatar': f'https://api.dicebear.com/7.x/avataaars/svg?seed={i}',
                'member': random.choices(['是', '否'], weights=[15, 85])[0],  # 15%概率是会员
                'score': random.randint(0, 2000),
                'account': round(random.uniform(0, 10000), 2),
                'role': 'USER'
            }
            users.append(user)
        return users
    
    def insert_user(self, user: Dict) -> bool:
        """插入用户数据"""
        sql = """
            INSERT INTO user (username, password, name, phone, email, avatar, member, score, account, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(sql, (
                user['username'], user['password'], user['name'],
                user['phone'], user['email'], user['avatar'],
                user['member'], user['score'], user['account'], user['role']
            ))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            return False
    
    def batch_insert_users(self, users: List[Dict], batch_size: int = 500) -> int:
        """批量插入用户数据，提高效率"""
        sql = """
            INSERT INTO user (username, password, name, phone, email, avatar, member, score, account, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        success = 0
        for i in range(0, len(users), batch_size):
            batch = users[i:i + batch_size]
            try:
                values = [(
                    u['username'], u['password'], u['name'],
                    u['phone'], u['email'], u['avatar'],
                    u['member'], u['score'], u['account'], u['role']
                ) for u in batch]
                self.cursor.executemany(sql, values)
                self.conn.commit()
                success += len(batch)
                print(f"  已导入 {success}/{len(users)} 条...")
            except Exception as e:
                print(f"  批量插入失败: {e}")
                self.conn.rollback()
        return success
    
    def run(self, count: int = 50, batch_mode: bool = True):
        """运行用户数据生成"""
        print(f"\n开始生成 {count} 条用户数据...")
        users = self.generate_users(count)
        
        if batch_mode and count > 100:
            success = self.batch_insert_users(users)
        else:
            success = 0
            for user in users:
                if self.insert_user(user):
                    success += 1
        print(f"用户数据生成完成，成功: {success}/{count}")


class ScoreProductSpider(BaseSpider):
    """积分商品爬虫"""
    
    def generate_score_products(self, count: int = 20) -> List[Dict]:
        """生成积分商品数据"""
        products = [
            {'name': '设计模式精讲', 'type': 'VIDEO', 'price': 200, 'descr': '23种设计模式详解'},
            {'name': 'Git版本控制', 'type': 'TEXT', 'price': 100, 'descr': 'Git使用技巧与团队协作'},
            {'name': 'Linux运维基础', 'type': 'TEXT', 'price': 150, 'descr': 'Linux常用命令与脚本'},
            {'name': 'Redis实战指南', 'type': 'VIDEO', 'price': 180, 'descr': 'Redis核心原理与应用'},
            {'name': 'Nginx配置详解', 'type': 'TEXT', 'price': 80, 'descr': 'Nginx反向代理与负载均衡'},
            {'name': 'Docker进阶实战', 'type': 'VIDEO', 'price': 250, 'descr': 'Docker高级特性与K8s入门'},
            {'name': 'JVM调优指南', 'type': 'VIDEO', 'price': 300, 'descr': 'JVM原理与性能调优'},
            {'name': '并发编程实战', 'type': 'VIDEO', 'price': 280, 'descr': 'Java多线程与并发'},
            {'name': '网络安全入门', 'type': 'TEXT', 'price': 120, 'descr': 'Web安全基础与防护'},
            {'name': 'Python爬虫实战', 'type': 'VIDEO', 'price': 200, 'descr': '爬虫框架与反爬策略'},
            {'name': 'TypeScript入门', 'type': 'VIDEO', 'price': 150, 'descr': 'TS基础与实战应用'},
            {'name': 'MongoDB实战', 'type': 'TEXT', 'price': 100, 'descr': 'NoSQL数据库应用'},
            {'name': 'GraphQL API设计', 'type': 'TEXT', 'price': 120, 'descr': 'GraphQL入门到精通'},
            {'name': '微服务架构设计', 'type': 'VIDEO', 'price': 350, 'descr': '微服务拆分与治理'},
            {'name': 'Elasticsearch实战', 'type': 'VIDEO', 'price': 220, 'descr': '搜索引擎原理与应用'},
            {'name': 'Kafka消息队列', 'type': 'VIDEO', 'price': 200, 'descr': '消息中间件实战'},
            {'name': 'Zookeeper原理', 'type': 'TEXT', 'price': 80, 'descr': '分布式协调服务'},
            {'name': 'Netty网络编程', 'type': 'VIDEO', 'price': 260, 'descr': '高性能网络框架'},
            {'name': 'SpringCloud实战', 'type': 'VIDEO', 'price': 320, 'descr': '微服务全家桶'},
            {'name': 'RabbitMQ实战', 'type': 'VIDEO', 'price': 180, 'descr': '消息队列应用'},
        ]
        
        result = []
        for p in products[:count]:
            result.append({
                'name': p['name'],
                'content': f'<p>{p["descr"]}</p>',
                'type': p['type'],
                'price': p['price'],
                'img': f'https://picsum.photos/300/200?random={random.randint(1,1000)}',
                'recommend': random.choice(['是', '否']),
                'time': datetime.now().strftime('%Y-%m-%d')
            })
        return result
    
    def insert_product(self, product: Dict) -> bool:
        """插入积分商品"""
        sql = """
            INSERT INTO score (name, content, type, price, img, recommend, time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(sql, (
                product['name'], product['content'], product['type'],
                product['price'], product['img'], product['recommend'], product['time']
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"插入积分商品失败: {e}")
            self.conn.rollback()
            return False
    
    def run(self, count: int = 20):
        """运行积分商品生成"""
        print(f"\n开始生成 {count} 条积分商品数据...")
        products = self.generate_score_products(count)
        success = 0
        for p in products:
            if self.insert_product(p):
                success += 1
        print(f"积分商品生成完成，成功: {success}/{count}")


class CommentSpider(BaseSpider):
    """评论数据爬虫"""
    
    def generate_comments(self, count: int = 100) -> List[Dict]:
        """生成评论数据"""
        comments_template = [
            '课程讲解非常清晰，受益匪浅！',
            '老师讲得很好，例子很生动',
            '内容很实用，学到了很多',
            '课程质量很高，推荐大家学习',
            '讲解深入浅出，适合入门',
            '干货满满，值得反复观看',
            '课程内容丰富，案例实用',
            '老师经验丰富，讲解到位',
            '学习后收获很大，感谢分享',
            '课程体系完整，循序渐进',
            '非常棒的课程，强烈推荐！',
            '学完感觉提升很大',
            '课程很系统，适合系统学习',
            '讲解细致，容易理解',
            '物超所值，非常满意',
        ]
        
        comments = []
        # 获取课程ID列表
        self.cursor.execute("SELECT id FROM course LIMIT 20")
        course_ids = [row[0] for row in self.cursor.fetchall()]
        
        # 获取用户ID列表
        self.cursor.execute("SELECT id FROM user LIMIT 30")
        user_ids = [row[0] for row in self.cursor.fetchall()]
        
        if not course_ids or not user_ids:
            print("缺少课程或用户数据，请先运行其他爬虫")
            return []
        
        for i in range(count):
            comment = {
                'user_id': random.choice(user_ids),
                'course_id': random.choice(course_ids),
                'content': random.choice(comments_template),
                'time': (datetime.now() - timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d %H:%M:%S'),
                'parent_id': 0
            }
            comments.append(comment)
        return comments
    
    def insert_comment(self, comment: Dict) -> bool:
        """插入评论"""
        sql = """
            INSERT INTO comment (user_id, course_id, content, time, parent_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(sql, (
                comment['user_id'], comment['course_id'],
                comment['content'], comment['time'], comment['parent_id']
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"插入评论失败: {e}")
            self.conn.rollback()
            return False
    
    def run(self, count: int = 100):
        """运行评论生成"""
        print(f"\n开始生成 {count} 条评论数据...")
        comments = self.generate_comments(count)
        if not comments:
            return
        success = 0
        for c in comments:
            if self.insert_comment(c):
                success += 1
        print(f"评论数据生成完成，成功: {success}/{count}")


class BilibiliSpider(BaseSpider):
    """B站课程爬虫 - 爬取B站公开课程数据"""
    
    def fetch_bilibili_courses(self, keyword: str = '编程', page: int = 1) -> List[Dict]:
        """
        从B站搜索课程
        注意：B站API可能有反爬限制，建议设置合理的请求间隔
        """
        url = 'https://api.bilibili.com/x/web-interface/search/type'
        params = {
            'keyword': keyword,
            'search_type': 'video',
            'page': page,
            'page_size': 20
        }
        
        courses = []
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            data = response.json()
            
            if data.get('code') == 0:
                results = data.get('data', {}).get('result', [])
                for item in results:
                    course = {
                        'name': item.get('title', '').replace('<em class="keyword">', '').replace('</em>', ''),
                        'content': f'<p>{item.get("description", "精彩课程内容")}</p>',
                        'type': 'VIDEO',
                        'price': random.choice([0, 0, 0, 99, 199, 299]),  # 大部分免费
                        'discount': round(random.uniform(0.7, 1.0), 2),
                        'img': item.get('pic', '').startswith('//') and f'https:{item.get("pic")}' or item.get('pic', ''),
                        'bvid': item.get('bvid', ''),
                        'author': item.get('author', ''),
                        'play': item.get('play', 0)
                    }
                    courses.append(course)
            else:
                print(f"B站API返回错误: {data.get('message')}")
                
        except Exception as e:
            print(f"爬取B站数据失败: {e}")
        
        return courses
    
    def insert_course(self, course: Dict) -> bool:
        """插入课程数据"""
        sql = """
            INSERT INTO course (name, content, type, price, discount, img, time, recommend)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(sql, (
                course['name'], course['content'], course['type'],
                course['price'], course['discount'], course['img'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                random.choice(['是', '否'])
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"插入课程失败: {e}")
            self.conn.rollback()
            return False
    
    def run(self, keywords: List[str] = None, pages: int = 2):
        """运行B站爬虫"""
        if keywords is None:
            keywords = ['Python编程', 'Java教程', '前端开发', 'MySQL数据库']
        
        print(f"\n开始从B站爬取课程数据...")
        total_success = 0
        
        for keyword in keywords:
            print(f"\n搜索关键词: {keyword}")
            for page in range(1, pages + 1):
                print(f"  第 {page} 页...")
                courses = self.fetch_bilibili_courses(keyword, page)
                for course in courses:
                    if self.insert_course(course):
                        total_success += 1
                time.sleep(1)  # 避免请求过快
        
        print(f"\nB站课程爬取完成，成功: {total_success}")


class JsonImportSpider(BaseSpider):
    """JSON文件导入爬虫"""
    
    def import_courses_from_json(self, file_path: str) -> int:
        """从JSON文件导入课程数据"""
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        courses = data if isinstance(data, list) else data.get('courses', [])
        success = 0
        
        for course in courses:
            sql = """
                INSERT INTO course (name, content, type, price, discount, img, time, recommend)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            try:
                self.cursor.execute(sql, (
                    course.get('name', '未命名课程'),
                    course.get('content', ''),
                    course.get('type', 'VIDEO'),
                    course.get('price', 0),
                    course.get('discount', 1.0),
                    course.get('img', ''),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    course.get('recommend', '否')
                ))
                self.conn.commit()
                success += 1
            except Exception as e:
                print(f"导入课程失败: {e}")
                self.conn.rollback()
        
        return success
    
    def import_users_from_json(self, file_path: str) -> int:
        """从JSON文件导入用户数据"""
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        if isinstance(users, dict):
            users = users.get('users', [])
        
        success = 0
        for user in users:
            sql = """
                INSERT INTO user (username, password, name, phone, email, member, score, account, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            try:
                self.cursor.execute(sql, (
                    user.get('username'),
                    user.get('password', '123456'),
                    user.get('name', ''),
                    user.get('phone', ''),
                    user.get('email', ''),
                    user.get('member', '否'),
                    user.get('score', 0),
                    user.get('account', 0),
                    user.get('role', 'USER')
                ))
                self.conn.commit()
                success += 1
            except Exception as e:
                print(f"导入用户失败: {e}")
                self.conn.rollback()
        
        return success


class CsvImportSpider(BaseSpider):
    """CSV文件导入爬虫"""
    
    def import_courses_from_csv(self, file_path: str) -> int:
        """从CSV文件导入课程数据"""
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return 0
        
        success = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sql = """
                    INSERT INTO course (name, content, type, price, discount, img, time, recommend)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                try:
                    self.cursor.execute(sql, (
                        row.get('name', ''),
                        row.get('content', ''),
                        row.get('type', 'VIDEO'),
                        float(row.get('price', 0)),
                        float(row.get('discount', 1.0)),
                        row.get('img', ''),
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        row.get('recommend', '否')
                    ))
                    self.conn.commit()
                    success += 1
                except Exception as e:
                    print(f"导入课程失败: {e}")
                    self.conn.rollback()
        
        return success


# ==================== 运行入口 ====================
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='扩展爬虫模块')
    parser.add_argument('--users', type=int, default=3000, help='生成用户数据数量，默认3000')
    parser.add_argument('--score', type=int, default=20, help='生成积分商品数量')
    parser.add_argument('--comments', type=int, default=100, help='生成评论数量')
    args = parser.parse_args()
    
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root',  # 请根据实际情况修改
        'database': 'manager',
        'charset': 'utf8mb4'
    }
    
    print("=" * 60)
    print("扩展爬虫模块")
    print("=" * 60)
    
    # 1. 生成用户数据
    user_spider = UserSpider(db_config)
    user_spider.run(count=args.users)
    user_spider.close()
    
    # 2. 生成积分商品
    score_spider = ScoreProductSpider(db_config)
    score_spider.run(count=args.score)
    score_spider.close()
    
    # 3. 生成评论数据
    comment_spider = CommentSpider(db_config)
    comment_spider.run(count=args.comments)
    comment_spider.close()
    
    print("\n所有爬虫运行完成！")
