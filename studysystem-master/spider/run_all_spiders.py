# -*- coding: utf-8 -*-
"""
在线学习管理系统 - 爬虫插件统一运行入口
一键运行所有爬虫，导入示例数据到MySQL数据库
"""
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from course_spider import CourseSpider
from information_spider import InformationSpider
from notice_spider import NoticeSpider
from extended_spider import UserSpider, ScoreProductSpider, CommentSpider, BilibiliSpider, JsonImportSpider, CsvImportSpider


# 数据库配置
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',  # 请根据实际情况修改
    'database': 'manager',
    'charset': 'utf8mb4'
}


def run_all_spiders():
    """运行所有爬虫"""
    print("\n" + "=" * 60)
    print("在线学习管理系统 - 数据爬虫插件")
    print("=" * 60 + "\n")
    
    total_success = 0
    total_fail = 0
    
    # 1. 爬取课程数据
    print("\n【第一步】爬取课程数据")
    print("-" * 60)
    course_spider = CourseSpider(db_config)
    try:
        courses = course_spider.fetch_online_courses()
        for i, course in enumerate(courses, 1):
            print(f"[{i}/{len(courses)}] 正在导入: {course['name']}")
            if course_spider.insert_course(course):
                total_success += 1
                print(f"  ✓ 导入成功")
            else:
                total_fail += 1
                print(f"  ✗ 导入失败")
    finally:
        course_spider.close()
    
    # 2. 爬取资讯数据
    print("\n【第二步】爬取资讯/资料数据")
    print("-" * 60)
    info_spider = InformationSpider(db_config)
    try:
        informations = info_spider.fetch_online_information()
        for i, info in enumerate(informations, 1):
            print(f"[{i}/{len(informations)}] 正在导入: {info['name']}")
            if info_spider.insert_information(info):
                total_success += 1
                print(f"  ✓ 导入成功")
            else:
                total_fail += 1
                print(f"  ✗ 导入失败")
    finally:
        info_spider.close()
    
    # 3. 爬取公告数据
    print("\n【第三步】爬取公告数据")
    print("-" * 60)
    notice_spider = NoticeSpider(db_config)
    try:
        notices = notice_spider.fetch_notices()
        for i, notice in enumerate(notices, 1):
            print(f"[{i}/{len(notices)}] 正在导入: {notice['title']}")
            if notice_spider.insert_notice(notice):
                total_success += 1
                print(f"  ✓ 导入成功")
            else:
                total_fail += 1
                print(f"  ✗ 导入失败")
    finally:
        notice_spider.close()
    
    # 4. 生成用户数据（扩展）
    print("\n【第四步】生成用户数据")
    print("-" * 60)
    user_spider = UserSpider(db_config)
    try:
        users = user_spider.generate_users(30)
        for i, user in enumerate(users, 1):
            print(f"[{i}/{len(users)}] 正在导入: {user['name']}")
            if user_spider.insert_user(user):
                total_success += 1
                print(f"  ✓ 导入成功")
            else:
                total_fail += 1
                print(f"  ✗ 导入失败")
    finally:
        user_spider.close()
    
    # 5. 生成积分商品数据（扩展）
    print("\n【第五步】生成积分商品数据")
    print("-" * 60)
    score_spider = ScoreProductSpider(db_config)
    try:
        products = score_spider.generate_score_products(15)
        for i, product in enumerate(products, 1):
            print(f"[{i}/{len(products)}] 正在导入: {product['name']}")
            if score_spider.insert_product(product):
                total_success += 1
                print(f"  ✓ 导入成功")
            else:
                total_fail += 1
                print(f"  ✗ 导入失败")
    finally:
        score_spider.close()
    
    # 6. 生成评论数据（扩展）
    print("\n【第六步】生成评论数据")
    print("-" * 60)
    comment_spider = CommentSpider(db_config)
    try:
        comments = comment_spider.generate_comments(50)
        for i, comment in enumerate(comments, 1):
            if comment_spider.insert_comment(comment):
                total_success += 1
            else:
                total_fail += 1
        print(f"评论数据导入完成: 成功 {total_success} 条")
    finally:
        comment_spider.close()
    
    # 统计结果
    print("\n" + "=" * 60)
    print("爬虫运行完成！")
    print("=" * 60)
    print(f"总成功数: {total_success}")
    print(f"总失败数: {total_fail}")
    print(f"数据已导入到数据库: {db_config['database']}")
    print("=" * 60 + "\n")


def run_bilibili_spider(keywords=None, pages=1):
    """单独运行B站爬虫"""
    if keywords is None:
        keywords = ['Python编程', 'Java教程', '前端开发']
    
    print("\n" + "=" * 60)
    print("B站课程爬虫")
    print("=" * 60 + "\n")
    
    bili_spider = BilibiliSpider(db_config)
    try:
        bili_spider.run(keywords=keywords, pages=pages)
    finally:
        bili_spider.close()


def import_from_json(json_file: str, data_type: str = 'course'):
    """从JSON文件导入数据"""
    print(f"\n从JSON文件导入{data_type}数据: {json_file}")
    importer = JsonImportSpider(db_config)
    try:
        if data_type == 'course':
            count = importer.import_courses_from_json(json_file)
        elif data_type == 'user':
            count = importer.import_users_from_json(json_file)
        else:
            print(f"不支持的数据类型: {data_type}")
            return
        print(f"导入完成，成功 {count} 条")
    finally:
        importer.close()


def import_from_csv(csv_file: str):
    """从CSV文件导入课程数据"""
    print(f"\n从CSV文件导入课程数据: {csv_file}")
    importer = CsvImportSpider(db_config)
    try:
        count = importer.import_courses_from_csv(csv_file)
        print(f"导入完成，成功 {count} 条")
    finally:
        importer.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='在线学习系统数据爬虫')
    parser.add_argument('--bili', action='store_true', help='运行B站爬虫')
    parser.add_argument('--json', type=str, help='JSON文件路径')
    parser.add_argument('--csv', type=str, help='CSV文件路径')
    parser.add_argument('--type', type=str, default='course', help='数据类型(course/user)')
    args = parser.parse_args()
    
    try:
        if args.bili:
            run_bilibili_spider()
        elif args.json:
            import_from_json(args.json, args.type)
        elif args.csv:
            import_from_csv(args.csv)
        else:
            run_all_spiders()
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
    except Exception as e:
        print(f"\n运行出错: {e}")
        import traceback
        traceback.print_exc()
