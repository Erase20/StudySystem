# -*- coding: utf-8 -*-
"""
在线学习管理系统 - 真实数据爬虫
从公开API爬取真实的课程、资讯数据，并生成关联的用户/评论/订单数据
数据来源：
  - 课程：Bilibili搜索API + 网易云课堂 + 慕课网
  - 资讯：CSDN文章 + 开源中国资讯
  - 公告：系统生成真实风格公告
  - 用户/评论/订单：基于真实课程数据生成关联数据
"""
import requests
import pymysql
import random
import time
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

# 数据库配置
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'manager',
    'charset': 'utf8mb4'
}

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://www.bilibili.com/',
}


def get_db_conn():
    """获取数据库连接"""
    return pymysql.connect(**db_config)


def clear_old_spider_data():
    """清空旧爬虫数据（保留admin账号和test用户）"""
    conn = get_db_conn()
    cursor = conn.cursor()
    tables = ['comment', 'orders', 'scoreorder', 'fileorder', 'signin',
              'learning_record', 'learning_plan', 'note', 'recharge_record',
              'information', 'score', 'notice', 'course']
    # 用户表只删除模拟用户（保留admin和test）
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            conn.commit()
            print(f"  清空 {table}")
        except Exception as e:
            print(f"  清空 {table} 跳过: {e}")
    try:
        cursor.execute("DELETE FROM user WHERE username NOT IN ('admin', 'test')")
        conn.commit()
        print("  清空模拟用户（保留admin/test）")
    except Exception as e:
        print(f"  清空用户跳过: {e}")
    cursor.close()
    conn.close()


# ============================================================
# 课程爬虫 - Bilibili
# ============================================================
class BilibiliCourseSpider:
    """从B站爬取真实课程数据"""

    SEARCH_API = 'https://api.bilibili.com/x/web-interface/search/type'

    # 搜索关键词和分类映射
    KEYWORDS = [
        'Python教程', 'Java入门', 'Vue3教程', 'React教程',
        'SpringBoot实战', 'MySQL教程', 'Docker教程', 'Go语言',
        '数据结构与算法', 'Linux教程', 'Redis教程', '前端开发',
        '人工智能', '微信小程序', 'TypeScript教程', 'Node.js教程',
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        # 先访问B站首页获取cookie
        try:
            self.session.get('https://www.bilibili.com/', timeout=10)
        except:
            pass

    def search_courses(self, keyword: str, page: int = 1) -> List[Dict]:
        """搜索B站课程"""
        params = {
            'keyword': keyword,
            'search_type': 'video',
            'page': page,
            'page_size': 20,
            'order': 'click',  # 按播放量排序
        }
        courses = []
        try:
            resp = self.session.get(self.SEARCH_API, params=params, timeout=15)
            data = resp.json()
            if data.get('code') == 0:
                results = data.get('data', {}).get('result', [])
                for item in results:
                    # 清理标题中的HTML标签
                    title = re.sub(r'<[^>]+>', '', item.get('title', ''))
                    if not title:
                        continue
                    pic = item.get('pic', '')
                    if pic and pic.startswith('//'):
                        pic = 'https:' + pic

                    course = {
                        'name': title,
                        'content': f'<p>{item.get("description", "精彩课程内容")}</p>',
                        'type': 'VIDEO',
                        'price': random.choice([0, 0, 0, 0, 49, 69, 99, 129, 149, 199]),
                        'discount': random.choice([1.0, 1.0, 0.9, 0.85, 0.8]),
                        'img': pic or f'https://picsum.photos/seed/{random.randint(1,9999)}/300/200',
                        'author': item.get('author', ''),
                        'play': item.get('play', 0),
                        'bvid': item.get('bvid', ''),
                        'tag': item.get('tag', ''),
                    }
                    courses.append(course)
            else:
                print(f"  B站API返回: {data.get('message', 'unknown')}")
        except Exception as e:
            print(f"  B站请求失败: {e}")
        return courses

    def insert_course(self, course: Dict) -> bool:
        """插入课程到数据库"""
        conn = get_db_conn()
        cursor = conn.cursor()
        sql = """INSERT INTO course (name, content, type, price, discount, img, video, file, recommend, time)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        try:
            days_ago = random.randint(1, 180)
            create_time = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            cursor.execute(sql, (
                course['name'], course['content'], course['type'],
                course['price'], course['discount'], course['img'],
                None, None,  # video, file
                random.choices(['是', '否'], weights=[30, 70])[0],
                create_time
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"  插入课程失败: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def run(self, max_courses=60):
        """运行B站课程爬虫"""
        print(f"\n{'='*60}")
        print("  B站课程爬虫")
        print(f"{'='*60}")
        total = 0
        seen_names = set()

        for kw in self.KEYWORDS:
            if total >= max_courses:
                break
            print(f"\n  搜索: {kw}")
            for page in range(1, 3):
                if total >= max_courses:
                    break
                courses = self.search_courses(kw, page)
                for c in courses:
                    # 去重
                    if c['name'] in seen_names:
                        continue
                    seen_names.add(c['name'])
                    if self.insert_course(c):
                        total += 1
                        print(f"    [{total}] {c['name'][:30]}... (播放:{c['play']})")
                time.sleep(1.5)  # 避免请求过快

        print(f"\n  B站课程爬取完成，共导入 {total} 门课程")
        return total


# ============================================================
# 课程爬虫 - 慕课网 (免费课程API)
# ============================================================
class ImoocCourseSpider:
    """从慕课网爬取课程数据"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': HEADERS['User-Agent'],
            'Referer': 'https://www.imooc.com/',
        })

    def fetch_courses(self, page=1) -> List[Dict]:
        """获取慕课网课程列表"""
        url = f'https://www.imooc.com/api3/courselist'
        params = {
            'page': page,
            'c_type': 0,  # 全部
            'is_easy': 0,
        }
        courses = []
        try:
            resp = self.session.get(url, params=params, timeout=15)
            # 慕课网可能返回JSON或HTML
            text = resp.text
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    items = data.get('data', []) or data.get('list', [])
                    for item in items:
                        name = item.get('name', item.get('title', ''))
                        if not name:
                            continue
                        pic = item.get('pic', item.get('cover', ''))
                        if pic and not pic.startswith('http'):
                            pic = 'https://img.mukewang.com' + pic if pic.startswith('//') else pic
                        course = {
                            'name': name,
                            'content': f'<p>{item.get("description", item.get("short_description", "优质课程"))}</p>',
                            'type': 'VIDEO',
                            'price': item.get('price', random.choice([0, 99, 199, 299])),
                            'discount': random.choice([1.0, 1.0, 0.9, 0.8]),
                            'img': pic or f'https://picsum.photos/seed/{random.randint(1,9999)}/300/200',
                        }
                        courses.append(course)
                except json.JSONDecodeError:
                    # 解析HTML页面
                    soup = BeautifulSoup(text, 'html.parser')
                    items = soup.select('.course-item, .item, .course-card')
                    for item in items:
                        title_el = item.select_one('.title, .name, h3, a')
                        if not title_el:
                            continue
                        name = title_el.get_text(strip=True)
                        if not name:
                            continue
                        img_el = item.select_one('img')
                        img = img_el.get('src', '') if img_el else ''
                        if img and img.startswith('//'):
                            img = 'https:' + img
                        course = {
                            'name': name,
                            'content': '<p>优质实战课程</p>',
                            'type': 'VIDEO',
                            'price': random.choice([0, 99, 199]),
                            'discount': random.choice([1.0, 0.9, 0.8]),
                            'img': img or f'https://picsum.photos/seed/{random.randint(1,9999)}/300/200',
                        }
                        courses.append(course)
        except Exception as e:
            print(f"  慕课网请求失败: {e}")
        return courses

    def insert_course(self, course: Dict) -> bool:
        """插入课程到数据库"""
        conn = get_db_conn()
        cursor = conn.cursor()
        sql = """INSERT INTO course (name, content, type, price, discount, img, video, file, recommend, time)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        try:
            days_ago = random.randint(1, 180)
            create_time = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            cursor.execute(sql, (
                course['name'], course['content'], course['type'],
                course['price'], course['discount'], course['img'],
                None, None,
                random.choices(['是', '否'], weights=[30, 70])[0],
                create_time
            ))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def run(self, max_courses=30):
        """运行慕课网爬虫"""
        print(f"\n{'='*60}")
        print("  慕课网课程爬虫")
        print(f"{'='*60}")
        total = 0
        seen_names = set()

        for page in range(1, 5):
            if total >= max_courses:
                break
            print(f"  第 {page} 页...")
            courses = self.fetch_courses(page)
            for c in courses:
                if c['name'] in seen_names:
                    continue
                seen_names.add(c['name'])
                if self.insert_course(c):
                    total += 1
                    print(f"    [{total}] {c['name'][:30]}")
            time.sleep(2)

        print(f"\n  慕课网课程爬取完成，共导入 {total} 门课程")
        return total


# ============================================================
# 资讯爬虫 - 开源中国 & CSDN
# ============================================================
class TechArticleSpider:
    """爬取技术文章/资讯数据"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def fetch_oschina_articles(self) -> List[Dict]:
        """从开源中国获取资讯"""
        articles = []
        url = 'https://www.oschina.net/action/ajax/get_more_news_list'
        params = {
            'newsType': 'industry',  # 行业资讯
            'p': 1,
        }
        headers = {**HEADERS, 'Referer': 'https://www.oschina.net/news'}
        try:
            resp = self.session.get(url, params=params, headers=headers, timeout=15)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    items = data.get('newsList', data) if isinstance(data, dict) else data
                    if isinstance(items, list):
                        for item in items:
                            title = item.get('title', item.get('name', ''))
                            if not title:
                                continue
                            # 清理HTML标签
                            title = re.sub(r'<[^>]+>', '', title)
                            descr = item.get('description', item.get('summary', ''))
                            if descr:
                                descr = re.sub(r'<[^>]+>', '', descr)[:200]
                            img = item.get('cover', item.get('img', item.get('pic', '')))
                            if img and img.startswith('//'):
                                img = 'https:' + img
                            article = {
                                'name': title,
                                'content': f'<p>{descr or "技术资讯文章"}</p>',
                                'descr': descr or '技术资讯',
                                'img': img or f'https://picsum.photos/seed/{random.randint(1,9999)}/300/200',
                                'file': '',
                                'score': random.choice([0, 0, 5, 10, 15, 20]),
                                'status': '审核通过',
                            }
                            articles.append(article)
                except json.JSONDecodeError:
                    # HTML解析
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    items = soup.select('.item, .news-item, article')
                    for item in items:
                        title_el = item.select_one('.title, h2, h3, a')
                        if not title_el:
                            continue
                        title = title_el.get_text(strip=True)
                        if not title:
                            continue
                        descr_el = item.select_one('.description, .summary, p')
                        descr = descr_el.get_text(strip=True)[:200] if descr_el else ''
                        img_el = item.select_one('img')
                        img = img_el.get('src', '') if img_el else ''
                        article = {
                            'name': title,
                            'content': f'<p>{descr or "技术资讯文章"}</p>',
                            'descr': descr or '技术资讯',
                            'img': img or f'https://picsum.photos/seed/{random.randint(1,9999)}/300/200',
                            'file': '',
                            'score': random.choice([0, 5, 10, 15]),
                            'status': '审核通过',
                        }
                        articles.append(article)
        except Exception as e:
            print(f"  开源中国请求失败: {e}")
        return articles

    def fetch_csdn_articles(self) -> List[Dict]:
        """从CSDN获取技术文章"""
        articles = []
        # CSDN搜索API
        url = 'https://so.csdn.net/api/search'
        keywords = ['Java', 'Python', '前端', '微服务', 'Docker', 'AI']
        for kw in random.sample(keywords, min(3, len(keywords))):
            params = {
                'q': kw,
                't': 'blog',
                'p': 1,
                's': 'time',  # 按时间排序
            }
            try:
                resp = self.session.get(url, params=params, timeout=15)
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        items = data.get('result', data.get('data', []))
                        if isinstance(items, list):
                            for item in items:
                                title = item.get('title', '')
                                if not title:
                                    continue
                                title = re.sub(r'<[^>]+>', '', title)
                                descr = item.get('description', item.get('body', ''))[:200]
                                if descr:
                                    descr = re.sub(r'<[^>]+>', '', descr)
                                article = {
                                    'name': title,
                                    'content': f'<p>{descr or "技术文章分享"}</p>',
                                    'descr': descr or '技术文章',
                                    'img': f'https://picsum.photos/seed/{random.randint(1,9999)}/300/200',
                                    'file': '',
                                    'score': random.choice([0, 5, 10, 15, 20, 25]),
                                    'status': '审核通过',
                                }
                                articles.append(article)
                    except json.JSONDecodeError:
                        pass
            except Exception as e:
                print(f"  CSDN请求失败: {e}")
            time.sleep(1)
        return articles

    def generate_tech_articles(self) -> List[Dict]:
        """如果API都不可用，生成高质量的技术资讯（基于真实技术热点）"""
        articles_data = [
            {'name': 'Spring Boot 3.2新特性全面解析', 'descr': 'Spring Boot 3.2带来了对虚拟线程的支持、RestClient API、JdbcClient等新特性，本文全面解读这些变化。', 'score': 20},
            {'name': 'Vue 3.4 "Slam Dunk" 发布：性能提升30%', 'descr': 'Vue 3.4版本带来了v-model的改进、解析器性能优化、Hydration不匹配错误改进等重要更新。', 'score': 15},
            {'name': 'Rust 2024版正式发布：所有新特性一览', 'descr': 'Rust 2024版带来了gen块、生命周期捕获规则变更、unsafe块等关键特性。', 'score': 10},
            {'name': 'Go 1.22发布：革命性的循环变量变更', 'descr': 'Go 1.22修复了循环变量作用域问题，新增range over func、增强路由模式匹配等。', 'score': 15},
            {'name': 'Deno 2.0发布：全面兼容Node.js生态', 'descr': 'Deno 2.0实现了对npm包的完整兼容，支持package.json，引入私有注册表支持。', 'score': 10},
            {'name': 'MySQL 9.0 Innovation版本发布', 'descr': 'MySQL 9.0引入了支持JavaScript的MySQL Shell、性能模式增强、Explain分析改进。', 'score': 20},
            {'name': 'React 19正式发布：Server Components稳定', 'descr': 'React 19稳定了Server Components、Actions、use() Hook等核心特性，标志着React全栈时代的到来。', 'score': 25},
            {'name': 'Redis 8.0发布：多线程I/O读写性能翻倍', 'descr': 'Redis 8.0引入多线程I/O，读写性能翻倍；新增Function特性替代Lua脚本；ACL增强。', 'score': 15},
            {'name': 'Kubernetes 1.30：原生Sidecar容器支持', 'descr': 'K8s 1.30正式将Sidecar容器提升为GA，解决了Istio等服务网格长期以来的容器生命周期问题。', 'score': 10},
            {'name': 'TypeScript 5.5发布：推断类型守卫', 'descr': 'TypeScript 5.5新增推断类型守卫、配置文件继承、正则表达式语法检查等特性。', 'score': 15},
            {'name': 'Python 3.13发布：实验性JIT编译器', 'descr': 'Python 3.13引入实验性的JIT编译器、改进的交互解释器、实验性自由线程模式。', 'score': 20},
            {'name': 'Next.js 15发布：Turbopack稳定', 'descr': 'Next.js 15将Turbopack提升为稳定版，构建速度提升96.3%，改进了缓存策略和部分预渲染。', 'score': 15},
            {'name': 'PostgreSQL 17发布：逻辑复制重大改进', 'descr': 'PostgreSQL 17增强了逻辑复制功能，支持增量备份、SQL/JSON标准、性能提升显著。', 'score': 10},
            {'name': 'Java 22正式发布：未命名变量与模式', 'descr': 'Java 22引入未命名变量和模式、外部函数和内存API、流收集器预览等重要特性。', 'score': 20},
            {'name': 'Docker Compose v2全面取代v1', 'descr': 'Docker Compose v2使用Go重写，性能大幅提升，正式取代Python版本的v1。', 'score': 5},
            {'name': 'Linux内核6.8发布：FUSE直连支持', 'descr': 'Linux 6.8引入FUSE直连支持、tmpfs内存优化、bcachefs文件系统改进。', 'score': 10},
            {'name': 'Nginx 1.26稳定版发布', 'descr': 'Nginx 1.26稳定版包含了HTTP/2改进、TLS 1.3优化、负载均衡增强等新特性。', 'score': 5},
            {'name': 'Kafka 4.0发布：移除ZooKeeper依赖', 'descr': 'Kafka 4.0完全移除了ZooKeeper依赖，全面采用KRaft模式，架构更简洁、运维更简单。', 'score': 15},
            {'name': 'Elasticsearch 8.14：向量搜索性能优化', 'descr': 'Elasticsearch 8.14大幅优化了向量搜索性能，支持HNSW算法改进，适用于AI搜索场景。', 'score': 10},
            {'name': 'LangChain 0.2发布：大模型开发框架升级', 'descr': 'LangChain 0.2重构了核心架构，改进了Agent执行模型，增强了对OpenAI GPT-4o的支持。', 'score': 20},
        ]

        articles = []
        for a in articles_data:
            article = {
                'name': a['name'],
                'content': f'<p>{a["descr"]}</p>',
                'descr': a['descr'],
                'img': f'https://picsum.photos/seed/{random.randint(1,9999)}/300/200',
                'file': '',
                'score': a['score'],
                'status': '审核通过',
            }
            articles.append(article)
        return articles

    def insert_information(self, info: Dict) -> bool:
        """插入资讯数据"""
        conn = get_db_conn()
        cursor = conn.cursor()
        sql = """INSERT INTO information (name, content, descr, file, img, score, user_id, status, time, recommend)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        try:
            days_ago = random.randint(1, 90)
            create_time = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(sql, (
                info['name'], info['content'], info['descr'],
                info['file'], info['img'], info['score'],
                1,  # user_id 默认为admin
                info['status'], create_time,
                random.choices(['是', '否'], weights=[30, 70])[0]
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"  插入资讯失败: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def run(self, max_articles=25):
        """运行资讯爬虫"""
        print(f"\n{'='*60}")
        print("  技术资讯爬虫")
        print(f"{'='*60}")
        total = 0
        seen_names = set()

        # 尝试从开源中国爬取
        print("\n  尝试从开源中国获取资讯...")
        articles = self.fetch_oschina_articles()
        for a in articles:
            if a['name'] in seen_names or total >= max_articles:
                continue
            seen_names.add(a['name'])
            if self.insert_information(a):
                total += 1
                print(f"    [{total}] {a['name'][:30]}")
            time.sleep(0.3)

        # 尝试从CSDN爬取
        if total < max_articles:
            print("\n  尝试从CSDN获取资讯...")
            csdn_articles = self.fetch_csdn_articles()
            for a in csdn_articles:
                if a['name'] in seen_names or total >= max_articles:
                    continue
                seen_names.add(a['name'])
                if self.insert_information(a):
                    total += 1
                    print(f"    [{total}] {a['name'][:30]}")
                time.sleep(0.3)

        # 如果API数据不足，用高质量技术资讯补齐
        if total < max_articles:
            remaining = max_articles - total
            print(f"\n  API数据不足，补充 {remaining} 条技术资讯...")
            backup = self.generate_tech_articles()
            for a in backup:
                if a['name'] in seen_names or total >= max_articles:
                    continue
                seen_names.add(a['name'])
                if self.insert_information(a):
                    total += 1
                    print(f"    [{total}] {a['name'][:30]}")

        print(f"\n  资讯爬取完成，共导入 {total} 条")
        return total


# ============================================================
# 公告生成器 - 真实风格
# ============================================================
class NoticeGenerator:
    """生成真实风格的系统公告"""

    NOTICES = [
        {'title': '系统正式上线公告', 'content': '在线学习管理系统正式上线！平台提供丰富的编程课程、技术资讯和学习资料，欢迎注册体验。新用户注册即送100积分，可用于兑换学习资料。', 'days': 90},
        {'title': '2026年Q2课程更新计划', 'content': '本季度将新增AI大模型开发、Rust系统编程、云原生架构等前沿课程。每周更新2-3门新课程，敬请期待。', 'days': 60},
        {'title': 'Python课程限时优惠活动', 'content': 'Python全栈系列课程限时7折优惠，活动时间：即日起至本月底。涵盖基础入门、数据分析、Web开发、爬虫实战等方向。', 'days': 45},
        {'title': '系统升级维护通知', 'content': '系统将于本周日凌晨2:00-4:00进行升级维护，新增学习进度跟踪、智能推荐等功能。维护期间可能无法访问，请提前安排学习。', 'days': 30},
        {'title': '新增AI大模型应用开发课程', 'content': '响应技术趋势，平台新增LangChain实战、Prompt Engineering、RAG架构设计、GPT应用开发等AI大模型课程，欢迎选购学习！', 'days': 25},
        {'title': '学习打卡月活动开始', 'content': '每日签到可获得10积分奖励，连续签到7天额外赠送50积分，连续30天赠送200积分！快来参与学习打卡吧。', 'days': 20},
        {'title': '积分商城上线公告', 'content': '积分商城正式上线！用户可通过签到、评论、分享等方式获取积分，兑换优质学习资料和课程优惠券。', 'days': 15},
        {'title': 'Spring Boot 3.2专题课程发布', 'content': 'Spring Boot 3.2专题课程已上线，涵盖虚拟线程、GraalVM原生编译、Observability等新特性，资深架构师授课。', 'days': 10},
        {'title': '前端技术周报第三期', 'content': '本期聚焦：React 19新特性解析、Vue 3.4性能优化、Vite 6.0发布、Bun 1.1生态发展。每周为您精选前端技术动态。', 'days': 7},
        {'title': '用户反馈意见征集', 'content': '为持续改善学习体验，现面向所有用户征集功能建议和改进意见。反馈被采纳者将获得100积分奖励，欢迎在评论区留言！', 'days': 3},
        {'title': 'Java 22新特性专题直播预告', 'content': '本周六晚8点，特邀Java Champion直播解读Java 22新特性：未命名变量、外部函数API、流收集器等。免费参加，不见不散！', 'days': 1},
        {'title': '数据库性能优化大赛', 'content': '参与SQL优化挑战赛，提交你的优化方案。前三名将分别获得500、300、100积分奖励。活动截止：本月30日。', 'days': 0},
    ]

    def run(self):
        print(f"\n{'='*60}")
        print("  公告数据生成")
        print(f"{'='*60}")
        conn = get_db_conn()
        cursor = conn.cursor()
        total = 0
        for n in self.NOTICES:
            sql = "INSERT INTO notice (title, content, time, user) VALUES (%s, %s, %s, %s)"
            try:
                create_time = (datetime.now() - timedelta(days=n['days'])).strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(sql, (n['title'], n['content'], create_time, '管理员'))
                conn.commit()
                total += 1
                print(f"  [{total}] {n['title']}")
            except Exception as e:
                conn.rollback()
                print(f"  插入公告失败: {e}")
        cursor.close()
        conn.close()
        print(f"\n  公告生成完成，共 {total} 条")
        return total


# ============================================================
# 用户数据生成器 - 真实风格
# ============================================================
class UserDataGenerator:
    """生成真实风格的用户数据"""

    SURNAMES = ['张', '王', '李', '赵', '刘', '陈', '杨', '黄', '周', '吴', '徐', '孙', '马', '朱', '胡', '郭', '何', '林', '罗', '高',
                '郑', '梁', '谢', '宋', '唐', '许', '韩', '冯', '邓', '曹', '彭', '曾', '萧', '田', '董', '潘', '袁', '蔡', '蒋', '余']
    MALE_NAMES = ['伟', '强', '磊', '军', '勇', '杰', '涛', '明', '超', '华', '刚', '辉', '鹏', '斌', '宇', '浩', '凯', '俊', '建', '志',
                  '峰', '波', '平', '东', '健', '亮', '飞', '龙', '威', '毅', '昊', '然', '晨', '阳', '旭', '宁', '松', '海', '山', '博']
    FEMALE_NAMES = ['芳', '娜', '敏', '静', '丽', '艳', '燕', '玲', '婷', '霞', '雪', '梅', '红', '娟', '莉', '萍', '琳', '倩', '颖', '欣',
                    '洁', '慧', '莹', '璐', '薇', '妍', '蕾', '雯', '珊', '琪', '瑶', '怡', '悦', '佳', '媛', '蓉', '茜', '瑾', '萱', '彤']
    PHONE_PREFIXES = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
                      '150', '151', '152', '153', '155', '156', '157', '158', '159',
                      '170', '171', '172', '173', '175', '176', '177', '178',
                      '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']

    def generate_users(self, count=50):
        users = []
        for i in range(count):
            surname = random.choice(self.SURNAMES)
            gender = random.choice(['male', 'female'])
            name_pool = self.MALE_NAMES if gender == 'male' else self.FEMALE_NAMES
            if random.random() < 0.6:
                full_name = surname + random.choice(name_pool)
            else:
                full_name = surname + random.choice(name_pool) + random.choice(name_pool)

            uid = 20000 + i
            phone = random.choice(self.PHONE_PREFIXES) + ''.join([str(random.randint(0, 9)) for _ in range(8)])
            users.append({
                'username': f'user{uid}',
                'password': '123456',
                'name': full_name,
                'phone': phone,
                'email': f'user{uid}@qq.com',
                'avatar': f'https://api.dicebear.com/7.x/avataaars/svg?seed={uid}',
                'member': random.choices(['是', '否'], weights=[15, 85])[0],
                'score': random.randint(0, 3000),
                'account': round(random.uniform(0, 15000), 2),
                'role': 'USER'
            })
        return users

    def batch_insert(self, users):
        conn = get_db_conn()
        cursor = conn.cursor()
        sql = """INSERT INTO user (username, password, name, phone, email, avatar, member, score, account, role)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        success = 0
        for i in range(0, len(users), 200):
            batch = users[i:i+200]
            try:
                values = [(u['username'], u['password'], u['name'], u['phone'], u['email'],
                           u['avatar'], u['member'], u['score'], u['account'], u['role']) for u in batch]
                cursor.executemany(sql, values)
                conn.commit()
                success += len(batch)
                print(f"  进度: {success}/{len(users)}")
            except Exception as e:
                print(f"  批量插入失败: {e}")
                conn.rollback()
        cursor.close()
        conn.close()
        return success

    def run(self, count=50):
        print(f"\n{'='*60}")
        print(f"  用户数据生成 ({count}条)")
        print(f"{'='*60}")
        users = self.generate_users(count)
        success = self.batch_insert(users)
        print(f"\n  用户数据生成完成，成功: {success}/{count}")
        return success


# ============================================================
# 评论数据生成器 - 基于真实课程
# ============================================================
class CommentDataGenerator:
    """基于已导入的真实课程生成评论"""

    COMMENT_TEMPLATES = [
        '老师讲得很清晰，跟着做了一遍，很有收获！',
        '课程质量很高，内容由浅入深，非常适合入门。',
        '终于找到一门讲得明白的课程了，感谢老师！',
        '跟着学了一周，感觉进步很大，推荐给同事了。',
        '讲解很细致，每个知识点都有代码演示，好评！',
        '课程体系完整，从基础到进阶都有覆盖，物超所值。',
        '老师的项目经验很丰富，讲的都是实战中用到的。',
        '学完之后顺利通过了面试，感谢这门课！',
        '内容很新，涵盖了最新版本的特性，紧跟技术发展。',
        '视频画质清晰，代码可复制，学习体验很好。',
        '这个价格太值了，比线下培训强多了。',
        '课程节奏把握得很好，不会太快也不会太慢。',
        '配套的练习题很有帮助，巩固了学到的知识。',
        '已经二刷了，每次看都有新的收获。',
        '对新手非常友好，解释了很多底层原理。',
        '学完这个再去学高级课程，基础非常扎实。',
        '老师回答问题很及时，学习群氛围也好。',
        '强烈推荐！这门课让我从一个菜鸟变成了能独立开发的程序员。',
        '内容干货满满，没有一句废话，全是重点。',
        '之前看了很多教程都不懂，这个一讲就明白了。',
        '作为后端开发，这门课帮我补齐了前端短板。',
        '实战项目很有代表性，可以直接用在工作中。',
        '课程更新很及时，每次版本更新都会补充新内容。',
        '建议多加点面试题讲解，其他都很好。',
        '这是我买过的最值得的一门课，没有之一。',
    ]

    def run(self, count=100):
        print(f"\n{'='*60}")
        print(f"  评论数据生成 ({count}条)")
        print(f"{'='*60}")
        conn = get_db_conn()
        cursor = conn.cursor()

        # 获取课程ID和用户ID
        cursor.execute("SELECT id FROM course")
        course_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT id FROM user")
        user_ids = [row[0] for row in cursor.fetchall()]

        if not course_ids or not user_ids:
            print("  缺少课程或用户数据，跳过评论生成")
            cursor.close()
            conn.close()
            return 0

        sql = "INSERT INTO comment (user_id, course_id, content, time, parent_id) VALUES (%s, %s, %s, %s, %s)"
        success = 0
        for i in range(count):
            try:
                comment_time = (datetime.now() - timedelta(days=random.randint(1, 90),
                              hours=random.randint(0, 23))).strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(sql, (
                    random.choice(user_ids),
                    random.choice(course_ids),
                    random.choice(self.COMMENT_TEMPLATES),
                    comment_time,
                    0
                ))
                conn.commit()
                success += 1
            except Exception as e:
                conn.rollback()
        cursor.close()
        conn.close()
        print(f"\n  评论生成完成，成功: {success}/{count}")
        return success


# ============================================================
# 积分商品数据生成器
# ============================================================
class ScoreProductGenerator:
    """生成积分商品数据"""

    PRODUCTS = [
        {'name': '设计模式精讲', 'type': 'VIDEO', 'price': 200, 'descr': '23种设计模式详解与实战应用'},
        {'name': 'Git版本控制完全指南', 'type': 'TEXT', 'price': 100, 'descr': 'Git命令详解和团队协作流程'},
        {'name': 'Redis实战指南', 'type': 'VIDEO', 'price': 180, 'descr': 'Redis核心原理与缓存架构'},
        {'name': 'Nginx配置详解', 'type': 'TEXT', 'price': 80, 'descr': 'Nginx反向代理与负载均衡配置'},
        {'name': 'JVM调优指南', 'type': 'VIDEO', 'price': 300, 'descr': 'JVM原理分析与性能调优实战'},
        {'name': '并发编程实战', 'type': 'VIDEO', 'price': 280, 'descr': 'Java多线程与并发框架深入解析'},
        {'name': 'Python爬虫实战', 'type': 'VIDEO', 'price': 200, 'descr': '爬虫框架与反爬策略全攻略'},
        {'name': 'TypeScript进阶', 'type': 'VIDEO', 'price': 150, 'descr': 'TS高级类型与工程化实践'},
        {'name': '微服务架构设计', 'type': 'VIDEO', 'price': 350, 'descr': '微服务拆分、治理与最佳实践'},
        {'name': 'Elasticsearch实战', 'type': 'VIDEO', 'price': 220, 'descr': '搜索引擎原理与实战应用'},
        {'name': 'Kafka消息队列', 'type': 'VIDEO', 'price': 200, 'descr': '消息中间件原理与项目实战'},
        {'name': 'Netty网络编程', 'type': 'VIDEO', 'price': 260, 'descr': '高性能网络框架深入剖析'},
        {'name': 'SpringCloud实战', 'type': 'VIDEO', 'price': 320, 'descr': 'Spring Cloud Alibaba微服务全家桶'},
        {'name': 'RabbitMQ实战', 'type': 'VIDEO', 'price': 180, 'descr': '消息队列应用场景与最佳实践'},
        {'name': 'MongoDB实战指南', 'type': 'TEXT', 'price': 120, 'descr': 'NoSQL数据库应用与优化'},
    ]

    def run(self):
        print(f"\n{'='*60}")
        print("  积分商品数据生成")
        print(f"{'='*60}")
        conn = get_db_conn()
        cursor = conn.cursor()
        sql = """INSERT INTO score (name, content, type, price, img, recommend, time)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        success = 0
        for p in self.PRODUCTS:
            try:
                cursor.execute(sql, (
                    p['name'],
                    f'<p>{p["descr"]}</p>',
                    p['type'],
                    p['price'],
                    f'https://picsum.photos/seed/{random.randint(1,9999)}/300/200',
                    random.choice(['是', '否']),
                    datetime.now().strftime('%Y-%m-%d')
                ))
                conn.commit()
                success += 1
                print(f"  [{success}] {p['name']}")
            except Exception as e:
                conn.rollback()
                print(f"  插入失败: {e}")
        cursor.close()
        conn.close()
        print(f"\n  积分商品生成完成，共 {success} 条")
        return success


# ============================================================
# 订单数据生成器 - 基于真实课程和用户
# ============================================================
class OrderDataGenerator:
    """基于已有课程和用户生成订单数据"""

    def run(self, count=200):
        print(f"\n{'='*60}")
        print(f"  订单数据生成 ({count}条)")
        print(f"{'='*60}")
        conn = get_db_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT id, price, type FROM course")
        courses = cursor.fetchall()
        cursor.execute("SELECT id FROM user")
        users = [row[0] for row in cursor.fetchall()]

        if not courses or not users:
            print("  缺少课程或用户数据，跳过")
            cursor.close()
            conn.close()
            return 0

        sql = """INSERT INTO orders (course_id, price, order_id, time, user_id, course_type)
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        success = 0
        for i in range(count):
            try:
                course = random.choice(courses)
                order_time = (datetime.now() - timedelta(days=random.randint(1, 180),
                              hours=random.randint(0, 23))).strftime('%Y-%m-%d %H:%M:%S')
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                order_id = f'ORD{timestamp}{random.randint(100000, 999999)}'
                cursor.execute(sql, (
                    course[0],  # course_id
                    course[1] or 0,  # price
                    order_id,
                    order_time,
                    random.choice(users),
                    course[2] or 'VIDEO'  # type
                ))
                conn.commit()
                success += 1
            except Exception as e:
                conn.rollback()

        cursor.close()
        conn.close()
        print(f"\n  订单生成完成，成功: {success}/{count}")
        return success


# ============================================================
# 主入口
# ============================================================
def main():
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("\n" + "=" * 60)
    print("  在线学习管理系统 - 真实数据爬虫")
    print("=" * 60)
    print(f"  数据库: {db_config['database']}@{db_config['host']}:{db_config['port']}")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 询问是否清空旧数据
    print("\n[警告] 将清空旧爬虫数据并重新导入（保留admin/test账号）")
    confirm = input("确认继续？(y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return

    start_time = time.time()

    # 0. 清空旧数据
    print("\n[第0步] 清空旧数据...")
    clear_old_spider_data()

    # 1. 爬取B站课程
    print("\n[第1步] 爬取B站真实课程数据...")
    bili_spider = BilibiliCourseSpider()
    bili_count = bili_spider.run(max_courses=60)

    # 2. 补充慕课网课程
    print("\n[第2步] 补充慕课网课程数据...")
    imooc_spider = ImoocCourseSpider()
    imooc_count = imooc_spider.run(max_courses=30)

    # 3. 爬取技术资讯
    print("\n[第3步] 爬取技术资讯数据...")
    article_spider = TechArticleSpider()
    article_count = article_spider.run(max_articles=25)

    # 4. 生成公告
    print("\n[第4步] 生成系统公告...")
    notice_gen = NoticeGenerator()
    notice_count = notice_gen.run()

    # 5. 生成用户
    print("\n[第5步] 生成用户数据...")
    user_gen = UserDataGenerator()
    user_count = user_gen.run(count=50)

    # 6. 生成评论
    print("\n[第6步] 生成评论数据...")
    comment_gen = CommentDataGenerator()
    comment_count = comment_gen.run(count=150)

    # 7. 生成积分商品
    print("\n[第7步] 生成积分商品...")
    score_gen = ScoreProductGenerator()
    score_count = score_gen.run()

    # 8. 生成订单
    print("\n[第8步] 生成订单数据...")
    order_gen = OrderDataGenerator()
    order_count = order_gen.run(count=200)

    # 统计
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("  爬虫运行完成！")
    print("=" * 60)
    print(f"  B站课程: {bili_count} 门")
    print(f"  慕课网课程: {imooc_count} 门")
    print(f"  技术资讯: {article_count} 条")
    print(f"  系统公告: {notice_count} 条")
    print(f"  用户数据: {user_count} 个")
    print(f"  评论数据: {comment_count} 条")
    print(f"  积分商品: {score_count} 个")
    print(f"  订单数据: {order_count} 条")
    print(f"  总耗时: {elapsed:.1f}秒")
    print("=" * 60)

    # 打印数据库统计
    print("\n  数据库统计:")
    conn = get_db_conn()
    cursor = conn.cursor()
    for table in ['course', 'information', 'notice', 'user', 'comment', 'score', 'orders']:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"    {table}: {count} 条")
        except:
            pass
    cursor.close()
    conn.close()
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
    except Exception as e:
        print(f"\n运行出错: {e}")
        import traceback
        traceback.print_exc()
