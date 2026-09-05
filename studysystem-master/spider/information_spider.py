# -*- coding: utf-8 -*-
"""
在线学习管理系统 - 资讯/资料数据爬虫插件
爬取学习资料数据并导入MySQL数据库
"""
import requests
import pymysql
import random
import time
from datetime import datetime
from typing import List, Dict


class InformationSpider:
    """资讯/资料爬虫类"""
    
    def __init__(self, db_config: dict):
        """
        初始化爬虫
        :param db_config: 数据库配置
        """
        self.db_config = db_config
        self.conn = None
        self.cursor = None
        self._connect_db()
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
    
    def fetch_online_information(self) -> List[Dict]:
        """
        获取资讯/资料数据
        """
        informations = [
            {
                'name': 'Python学习路线图.pdf',
                'content': '<p>详细的Python学习路线，从入门到进阶</p>',
                'descr': '包含基础语法、Web开发、数据分析、机器学习等方向',
                'file': 'python_roadmap.pdf',
                'img': 'https://example.com/info_python.jpg',
                'score': 10,
                'user_id': 1,
                'status': '审核通过'
            },
            {
                'name': 'Java面试题汇总2024',
                'content': '<p>精选Java面试题，涵盖基础、框架、分布式等</p>',
                'descr': '包含Java基础、Spring、Redis、MySQL、微服务等面试题',
                'file': 'java_interview.pdf',
                'img': 'https://example.com/info_java.jpg',
                'score': 20,
                'user_id': 1,
                'status': '审核通过'
            },
            {
                'name': '前端开发规范手册',
                'content': '<p>前端开发最佳实践和代码规范</p>',
                'descr': 'HTML/CSS规范、JavaScript规范、Vue/React开发规范',
                'file': 'frontend_standard.pdf',
                'img': 'https://example.com/info_frontend.jpg',
                'score': 0,
                'user_id': 1,
                'status': '审核通过'
            },
            {
                'name': 'MySQL性能优化指南',
                'content': '<p>MySQL数据库性能优化实战指南</p>',
                'descr': '索引优化、SQL优化、配置优化、分库分表策略',
                'file': 'mysql_optimize.pdf',
                'img': 'https://example.com/info_mysql.jpg',
                'score': 15,
                'user_id': 1,
                'status': '审核通过'
            },
            {
                'name': 'Docker容器化部署教程',
                'content': '<p>Docker从入门到实战，容器化部署应用</p>',
                'descr': 'Docker基础、镜像制作、容器编排、CI/CD集成',
                'file': 'docker_tutorial.pdf',
                'img': 'https://example.com/info_docker.jpg',
                'score': 10,
                'user_id': 1,
                'status': '审核通过'
            },
            {
                'name': 'Git版本控制完全指南',
                'content': '<p>Git命令详解和团队协作流程</p>',
                'descr': 'Git基础、分支管理、冲突解决、GitFlow工作流',
                'file': 'git_guide.pdf',
                'img': 'https://example.com/info_git.jpg',
                'score': 0,
                'user_id': 1,
                'status': '审核通过'
            },
            {
                'name': 'Linux命令大全',
                'content': '<p>常用Linux命令速查手册</p>',
                'descr': '文件操作、系统管理、网络配置、Shell脚本',
                'file': 'linux_commands.pdf',
                'img': 'https://example.com/info_linux.jpg',
                'score': 5,
                'user_id': 1,
                'status': '审核通过'
            },
            {
                'name': '算法与数据结构笔记',
                'content': '<p>经典算法和数据结构详解</p>',
                'descr': '数组、链表、树、图、排序、查找、动态规划',
                'file': 'algorithm_notes.pdf',
                'img': 'https://example.com/info_algorithm.jpg',
                'score': 25,
                'user_id': 1,
                'status': '审核通过'
            }
        ]
        return informations
    
    def insert_information(self, info: Dict) -> bool:
        """
        插入资讯数据到数据库
        """
        sql = """
            INSERT INTO information (name, content, descr, file, img, score, user_id, status, time, recommend)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            recommend = random.choice(['是', '否'])
            
            self.cursor.execute(sql, (
                info['name'],
                info['content'],
                info['descr'],
                info['file'],
                info['img'],
                info['score'],
                info['user_id'],
                info['status'],
                current_time,
                recommend
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"插入资讯失败 [{info['name']}]: {e}")
            self.conn.rollback()
            return False
    
    def run(self):
        """运行爬虫"""
        print("=" * 50)
        print("开始爬取资讯/资料数据...")
        print("=" * 50)
        
        informations = self.fetch_online_information()
        success_count = 0
        fail_count = 0
        
        for i, info in enumerate(informations, 1):
            print(f"[{i}/{len(informations)}] 正在导入: {info['name']}")
            if self.insert_information(info):
                success_count += 1
                print(f"  ✓ 导入成功")
            else:
                fail_count += 1
                print(f"  ✗ 导入失败")
            time.sleep(0.3)
        
        print("=" * 50)
        print(f"爬取完成！成功: {success_count}, 失败: {fail_count}")
        print("=" * 50)


if __name__ == '__main__':
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'database': 'manager',
        'charset': 'utf8mb4'
    }
    
    spider = InformationSpider(db_config)
    try:
        spider.run()
    finally:
        spider.close()
