# -*- coding: utf-8 -*-
"""
在线学习管理系统 - 课程数据爬虫插件
爬取公开课程数据并导入MySQL数据库
"""
import requests
import json
import pymysql
import random
import time
from datetime import datetime
from typing import List, Dict, Optional


class CourseSpider:
    """课程爬虫类"""
    
    def __init__(self, db_config: dict):
        """
        初始化爬虫
        :param db_config: 数据库配置
        """
        self.db_config = db_config
        self.conn = None
        self.cursor = None
        self._connect_db()
        
        # 模拟浏览器请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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
    
    def fetch_online_courses(self) -> List[Dict]:
        """
        从公开API获取课程数据（示例：使用模拟数据）
        实际使用时可替换为真实API
        """
        # 模拟爬取的数据，实际可替换为真实API请求
        courses = [
            {
                'name': 'Python入门到精通',
                'content': '<p>从零开始学习Python编程，包含基础语法、面向对象、文件操作等内容</p>',
                'type': 'VIDEO',
                'price': 99.0,
                'discount': 0.8,
                'img': 'https://example.com/python.jpg'
            },
            {
                'name': 'Java Web开发实战',
                'content': '<p>SpringBoot + Vue前后端分离项目实战开发</p>',
                'type': 'VIDEO',
                'price': 199.0,
                'discount': 1.0,
                'img': 'https://example.com/java.jpg'
            },
            {
                'name': 'MySQL数据库设计与优化',
                'content': '<p>数据库设计原则、SQL优化、索引原理等核心知识</p>',
                'type': 'TEXT',
                'price': 59.0,
                'discount': 0.9,
                'img': 'https://example.com/mysql.jpg'
            },
            {
                'name': '前端开发基础教程',
                'content': '<p>HTML、CSS、JavaScript基础入门</p>',
                'type': 'VIDEO',
                'price': 0.0,
                'discount': 1.0,
                'img': 'https://example.com/frontend.jpg'
            },
            {
                'name': '数据结构与算法',
                'content': '<p>常用数据结构、经典算法、LeetCode刷题技巧</p>',
                'type': 'VIDEO',
                'price': 149.0,
                'discount': 0.85,
                'img': 'https://example.com/algorithm.jpg'
            },
            {
                'name': 'Linux系统运维',
                'content': '<p>Linux常用命令、Shell脚本、服务器部署</p>',
                'type': 'TEXT',
                'price': 79.0,
                'discount': 1.0,
                'img': 'https://example.com/linux.jpg'
            },
            {
                'name': '人工智能入门',
                'content': '<p>机器学习基础、深度学习入门、TensorFlow实战</p>',
                'type': 'VIDEO',
                'price': 299.0,
                'discount': 0.75,
                'img': 'https://example.com/ai.jpg'
            },
            {
                'name': '微信小程序开发',
                'content': '<p>小程序框架、云开发、实战项目</p>',
                'type': 'VIDEO',
                'price': 129.0,
                'discount': 0.9,
                'img': 'https://example.com/wechat.jpg'
            }
        ]
        return courses
    
    def insert_course(self, course: Dict) -> bool:
        """
        插入单条课程数据到数据库
        :param course: 课程字典
        :return: 是否成功
        """
        sql = """
            INSERT INTO course (name, content, type, price, discount, img, time, recommend)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            recommend = random.choice(['是', '否'])
            
            self.cursor.execute(sql, (
                course['name'],
                course['content'],
                course['type'],
                course['price'],
                course['discount'],
                course['img'],
                current_time,
                recommend
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"插入课程失败 [{course['name']}]: {e}")
            self.conn.rollback()
            return False
    
    def run(self):
        """运行爬虫"""
        print("=" * 50)
        print("开始爬取课程数据...")
        print("=" * 50)
        
        courses = self.fetch_online_courses()
        success_count = 0
        fail_count = 0
        
        for i, course in enumerate(courses, 1):
            print(f"[{i}/{len(courses)}] 正在导入: {course['name']}")
            if self.insert_course(course):
                success_count += 1
                print(f"  ✓ 导入成功")
            else:
                fail_count += 1
                print(f"  ✗ 导入失败")
            time.sleep(0.5)  # 模拟爬取间隔
        
        print("=" * 50)
        print(f"爬取完成！成功: {success_count}, 失败: {fail_count}")
        print("=" * 50)


if __name__ == '__main__':
    # 数据库配置
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'database': 'manager',
        'charset': 'utf8mb4'
    }
    
    spider = CourseSpider(db_config)
    try:
        spider.run()
    finally:
        spider.close()
