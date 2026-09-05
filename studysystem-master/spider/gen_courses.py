# -*- coding: utf-8 -*-
"""
课程数据生成脚本
每次运行生成100条课程数据并导入MySQL数据库
课程图片使用在线图片服务 picsum.photos
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
    'password': 'root',  # 请根据实际情况修改
    'database': 'manager',
    'charset': 'utf8mb4'
}

# 课程名称模板
COURSE_TEMPLATES = [
    # 编程语言
    {'prefix': 'Python', 'names': ['入门到精通', '数据分析实战', 'Web开发', '自动化脚本', '爬虫开发', '机器学习入门', '深度学习基础', 'Flask框架', 'Django实战', '数据分析与可视化']},
    {'prefix': 'Java', 'names': ['基础入门', '面向对象编程', 'Web开发实战', 'SpringBoot框架', '微服务架构', '并发编程', 'JVM调优', '设计模式', 'MyBatis实战', 'SpringCloud']},
    {'prefix': 'JavaScript', 'names': ['基础语法', 'DOM操作', 'ES6新特性', 'Node.js开发', 'Vue.js实战', 'React框架', 'TypeScript入门', '前端工程化', '性能优化', '前端安全']},
    {'prefix': 'Go语言', 'names': ['编程入门', 'Web开发', '并发编程', '微服务实战', '云原生开发', '区块链开发', '网络编程', '系统编程', '性能调优', '项目实战']},
    {'prefix': 'C++', 'names': ['基础入门', 'STL标准库', '数据结构实现', '算法实战', '游戏开发', '嵌入式开发', '系统编程', '网络编程', '性能优化', '项目实战']},
    # 数据库
    {'prefix': 'MySQL', 'names': ['基础入门', '高级查询', '性能优化', '主从复制', '分库分表', '高可用架构', '备份恢复', '安全管理', '运维实战', '案例分析']},
    {'prefix': 'Redis', 'names': ['基础入门', '数据结构', '缓存策略', '分布式锁', '集群部署', '持久化机制', '性能调优', '应用场景', '高可用方案', '项目实战']},
    {'prefix': 'MongoDB', 'names': ['基础入门', '数据建模', '聚合框架', '索引优化', '分片集群', '备份恢复', '性能监控', '安全配置', '运维管理', '项目实战']},
    # 前端框架
    {'prefix': 'Vue', 'names': ['基础入门', '组件开发', 'Vuex状态管理', 'Vue Router', 'Element UI', '项目实战', '性能优化', 'SSR服务端渲染', 'Vue3新特性', 'TypeScript整合']},
    {'prefix': 'React', 'names': ['基础入门', 'Hooks实战', 'Redux状态管理', 'React Router', 'Ant Design', 'Next.js', '性能优化', '服务端渲染', '移动端开发', '项目实战']},
    # 运维与云原生
    {'prefix': 'Docker', 'names': ['基础入门', '镜像制作', '容器编排', '网络配置', '数据管理', '安全实践', 'CI/CD集成', 'Kubernetes入门', '微服务部署', '生产环境实战']},
    {'prefix': 'Linux', 'names': ['基础命令', 'Shell脚本', '系统管理', '网络配置', '安全加固', '性能监控', '自动化运维', '故障排查', '服务部署', '项目实战']},
    # 大数据与AI
    {'prefix': 'Hadoop', 'names': ['基础入门', 'HDFS存储', 'MapReduce', 'Hive数据仓库', 'Spark计算', 'Flink实时计算', 'Kafka消息队列', '数据采集', '集群部署', '项目实战']},
    {'prefix': 'TensorFlow', 'names': ['基础入门', '神经网络', 'CNN图像识别', 'RNN序列模型', 'NLP自然语言', '模型部署', 'TensorBoard', 'TF Serving', '项目实战', '高级应用']},
    # 其他热门
    {'prefix': '微信小程序', 'names': ['基础入门', '组件开发', 'API调用', '云开发', '支付功能', '用户授权', '性能优化', '发布上线', '项目实战', '高级技巧']},
    {'prefix': 'Flutter', 'names': ['基础入门', 'Widget组件', '状态管理', '网络请求', '本地存储', '动画效果', '平台交互', '打包发布', '项目实战', '高级应用']},
]

# 课程描述模板
DESCRIPTIONS = [
    '本课程从零基础开始，循序渐进讲解核心知识点，适合初学者快速入门。',
    '深入浅出讲解核心技术原理，配合大量实战案例，帮助学员快速掌握。',
    '系统全面的知识体系，从基础到进阶，适合有一定基础的开发者。',
    '实战驱动教学，通过真实项目案例，让学员在实践中掌握技能。',
    '名师授课，讲解清晰易懂，配套资料齐全，学习效果显著。',
    '最新技术版本讲解，紧跟行业发展趋势，让学员掌握前沿技术。',
    '企业级项目实战，模拟真实开发场景，提升实际工作能力。',
    '源码级深度解析，理解底层原理，提升技术深度。',
    '面试重点全覆盖，高频考点详解，助力求职成功。',
    '配套练习题和项目作业，巩固所学知识，检验学习成果。',
]


def generate_courses(count: int):
    """生成课程数据"""
    courses = []
    
    for i in range(count):
        # 随机选择课程模板
        template = random.choice(COURSE_TEMPLATES)
        course_name = f'{template["prefix"]}{random.choice(template["names"])}'
        
        # 生成唯一课程名（添加序号避免重复）
        unique_name = f'{course_name} #{i + 1}'
        
        # 课程类型：视频课程为主
        course_type = random.choices(['VIDEO', 'TEXT'], weights=[70, 30])[0]
        
        # 价格：大部分收费，部分免费
        if random.random() < 0.2:  # 20%免费
            price = 0
            discount = 1.0
        else:
            price = random.choice([49, 59, 69, 79, 89, 99, 129, 149, 199, 249, 299, 399])
            discount = random.choice([1.0, 1.0, 0.9, 0.85, 0.8, 0.75])
        
        # 图片URL：使用picsum.photos随机图片
        img_id = random.randint(1, 10000)
        img = f'https://picsum.photos/seed/{img_id}/300/200'
        
        # 课程描述
        content = f'<p>{random.choice(DESCRIPTIONS)}</p>'
        
        # 推荐状态
        recommend = random.choices(['是', '否'], weights=[25, 75])[0]
        
        # 发布时间（最近一年内）
        days_ago = random.randint(1, 365)
        create_time = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        course = (
            unique_name,      # name
            content,          # content
            course_type,      # type
            price,            # price
            discount,         # discount
            img,              # img
            None,             # video
            None,             # file
            recommend,        # recommend
            create_time       # time
        )
        courses.append(course)
    
    return courses


def batch_insert_courses(courses, batch_size=50):
    """批量插入课程数据"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    
    sql = """
        INSERT INTO course (name, content, type, price, discount, img, video, file, recommend, time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    success = 0
    total = len(courses)
    
    for i in range(0, total, batch_size):
        batch = courses[i:i + batch_size]
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


def get_course_count():
    """获取当前课程数量"""
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM course")
        result = cursor.fetchone()
        count = result[0] if result else 0
    except:
        count = 0
    cursor.close()
    conn.close()
    return count


def main():
    count = 100  # 每次生成100条
    
    print("=" * 50)
    print("课程数据生成器")
    print("=" * 50)
    
    # 获取当前课程数量
    current_count = get_course_count()
    print(f"\n当前课程数量: {current_count}")
    print(f"本次生成数量: {count}")
    
    # 生成数据
    print(f"\n正在生成 {count} 条课程数据...")
    start_time = time.time()
    courses = generate_courses(count)
    gen_time = time.time() - start_time
    print(f"数据生成完成，耗时: {gen_time:.2f}秒")
    
    # 批量插入
    print(f"\n正在导入数据库...")
    start_time = time.time()
    success = batch_insert_courses(courses)
    insert_time = time.time() - start_time
    
    print(f"\n导入完成，耗时: {insert_time:.2f}秒")
    print(f"成功: {success}/{count}")
    print(f"当前总课程数: {current_count + success}")
    print("=" * 50)


if __name__ == '__main__':
    main()
