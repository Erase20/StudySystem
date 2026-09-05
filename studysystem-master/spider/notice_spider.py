# -*- coding: utf-8 -*-
"""
在线学习管理系统 - 公告数据爬虫插件
爬取公告数据并导入MySQL数据库
"""
import pymysql
import time
from datetime import datetime, timedelta
from typing import List, Dict


class NoticeSpider:
    """公告爬虫类"""
    
    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.conn = None
        self.cursor = None
        self._connect_db()
    
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
    
    def fetch_notices(self) -> List[Dict]:
        """获取公告数据"""
        base_time = datetime.now()
        notices = [
            {
                'title': '系统正式上线公告',
                'content': '欢迎使用在线学习管理系统！系统已正式上线，提供丰富的课程资源和学习资料。',
                'user': '管理员',
                'time': (base_time - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'title': '新用户注册福利',
                'content': '新用户注册即送100积分，可用于兑换学习资料。快来注册体验吧！',
                'user': '管理员',
                'time': (base_time - timedelta(days=25)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'title': 'Python课程优惠活动',
                'content': 'Python系列课程限时8折优惠，活动时间：即日起至月底。',
                'user': '管理员',
                'time': (base_time - timedelta(days=20)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'title': '系统维护通知',
                'content': '系统将于本周日凌晨2:00-4:00进行维护升级，期间可能无法访问，请提前安排学习时间。',
                'user': '管理员',
                'time': (base_time - timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'title': '新增课程上线',
                'content': '新增《人工智能入门》《微信小程序开发》等热门课程，欢迎选购学习！',
                'user': '管理员',
                'time': (base_time - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'title': '会员权益升级',
                'content': '一次性充值满500元即可成为会员，享受全场课程9折优惠！',
                'user': '管理员',
                'time': (base_time - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'title': '学习打卡活动',
                'content': '每日签到可获得积分奖励，连续签到7天额外赠送50积分！',
                'user': '管理员',
                'time': (base_time - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'title': '资料分享活动',
                'content': '上传优质学习资料并通过审核，可获得丰厚积分奖励！',
                'user': '管理员',
                'time': base_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
        return notices
    
    def insert_notice(self, notice: Dict) -> bool:
        """插入公告数据"""
        sql = """
            INSERT INTO notice (title, content, user, time)
            VALUES (%s, %s, %s, %s)
        """
        try:
            self.cursor.execute(sql, (
                notice['title'],
                notice['content'],
                notice['user'],
                notice['time']
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"插入公告失败 [{notice['title']}]: {e}")
            self.conn.rollback()
            return False
    
    def run(self):
        """运行爬虫"""
        print("=" * 50)
        print("开始爬取公告数据...")
        print("=" * 50)
        
        notices = self.fetch_notices()
        success_count = 0
        fail_count = 0
        
        for i, notice in enumerate(notices, 1):
            print(f"[{i}/{len(notices)}] 正在导入: {notice['title']}")
            if self.insert_notice(notice):
                success_count += 1
                print(f"  ✓ 导入成功")
            else:
                fail_count += 1
                print(f"  ✗ 导入失败")
            time.sleep(0.2)
        
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
    
    spider = NoticeSpider(db_config)
    try:
        spider.run()
    finally:
        spider.close()
