# -*- coding: utf-8 -*-
"""
在线学习管理系统 - 项目文档生成器（增强版）
生成内容涵盖：项目概述、技术架构、功能模块、数据库设计、API接口、核心算法、项目结构、部署指南
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import parse_xml


def set_cell_border(cell, **kwargs):
    """设置单元格边框"""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = tcPr.first_child_found_in("w:tcBorders")
    if tcBorders is None:
        tcBorders = parse_xml(
            r'<w:tcBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'
        )
        tcPr.append(tcBorders)

    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        if edge in kwargs:
            edge_obj = tcBorders.find(qn('w:{}'.format(edge)))
            if edge_obj is None:
                edge_obj = parse_xml(
                    r'<w:{} xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'.format(edge)
                )
                tcBorders.append(edge_obj)
            edge_obj.set(qn('w:val'), kwargs[edge].get('val', 'single'))
            edge_obj.set(qn('w:sz'), str(kwargs[edge].get('sz', 4)))
            edge_obj.set(qn('w:color'), kwargs[edge].get('color', '000000'))


def add_heading_custom(doc, text, level=1):
    """添加自定义标题"""
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.name = '微软雅黑'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
    return heading


def add_paragraph_custom(doc, text, bold=False, size=10.5, alignment=WD_ALIGN_PARAGRAPH.LEFT, first_line_indent=0):
    """添加自定义段落"""
    p = doc.add_paragraph()
    p.alignment = alignment
    if first_line_indent:
        p.paragraph_format.first_line_indent = Cm(first_line_indent)
    run = p.add_run(text)
    run.font.name = '宋体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.size = Pt(size)
    run.font.bold = bold
    return p


def add_bullet_paragraph(doc, text, size=10.5, indent_level=0):
    """添加带项目符号的段落"""
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent = Cm(0.5 + indent_level * 0.5)
    run = p.add_run(text)
    run.font.name = '宋体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.size = Pt(size)
    return p


def add_number_paragraph(doc, text, size=10.5, indent_level=0):
    """添加带编号步骤的段落"""
    p = doc.add_paragraph(style='List Number')
    p.paragraph_format.left_indent = Cm(0.5 + indent_level * 0.5)
    run = p.add_run(text)
    run.font.name = '宋体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.size = Pt(size)
    return p


def create_table_with_header(doc, headers, rows_data, style='Light Grid Accent 1'):
    """创建带表头的表格"""
    table = doc.add_table(rows=1 + len(rows_data), cols=len(headers))
    table.style = style
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # 表头
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                run.font.bold = True
                run.font.name = '微软雅黑'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
                run.font.size = Pt(10)
    # 数据行
    for row_idx, row_data in enumerate(rows_data, 1):
        for col_idx, cell_text in enumerate(row_data):
            cell = table.rows[row_idx].cells[col_idx]
            cell.text = str(cell_text)
            for paragraph in cell.paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in paragraph.runs:
                    run.font.name = '宋体'
                    run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                    run.font.size = Pt(10)
    return table


def create_db_table(doc, table_name, table_desc, columns):
    """创建数据库表设计段落和表格"""
    add_heading_custom(doc, f'{table_desc}（{table_name}）', level=3)
    add_paragraph_custom(doc, f'表名：{table_name}，功能：{table_desc}')
    headers = ['字段名', '数据类型', '说明']
    create_table_with_header(doc, headers, columns)
    doc.add_paragraph()


def create_project_document():
    doc = Document()

    # 设置默认字体
    style = doc.styles['Normal']
    style.font.name = '宋体'
    style._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    style.font.size = Pt(10.5)

    # ========== 封面 ==========
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run('\n\n\n\n在线学习管理系统\n项目开发文档')
    run.font.name = '微软雅黑'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '微软雅黑')
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0, 51, 102)

    doc.add_paragraph('\n\n\n')

    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = info.add_run('文档版本：V2.0\n编制日期：2026年5月\n编制人：项目开发组')
    run.font.name = '宋体'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    run.font.size = Pt(12)

    doc.add_page_break()

    # ========== 目录 ==========
    add_heading_custom(doc, '目录', level=1)
    toc_items = [
        '1. 项目概述',
        '2. 技术架构',
        '3. 功能模块',
        '4. 数据库设计',
        '5. API接口文档',
        '6. 核心算法设计',
        '7. 项目结构',
        '8. 系统部署指南'
    ]
    for item in toc_items:
        add_paragraph_custom(doc, item, size=12)

    doc.add_page_break()

    # ========== 1. 项目概述 ==========
    add_heading_custom(doc, '1. 项目概述', level=1)

    add_heading_custom(doc, '1.1 项目背景', level=2)
    add_paragraph_custom(doc,
        '随着互联网技术的飞速发展和教育数字化转型的深入推进，在线教育已成为现代教育体系中不可或缺的重要组成部分。'
        '传统教育模式受到时间和空间的限制，无法满足人们碎片化、个性化的学习需求。'
        '本项目旨在构建一个功能完善、性能稳定、用户体验良好的在线学习管理平台，'
        '为用户提供高质量的课程内容、便捷的学习工具以及丰富的互动体验，同时为平台运营方提供高效的内容管理和数据分析能力。')

    add_heading_custom(doc, '1.2 项目目标', level=2)
    goals = [
        '构建前后端分离的在线学习平台，支持课程展示、用户学习、积分兑换等核心功能',
        '实现用户注册、登录、个人信息管理及基于角色的权限控制（ADMIN/USER）',
        '提供课程购买、学习记录追踪、学习笔记、每日签到等学习服务体系',
        '支持支付宝在线支付，完成课程和资料的付费交易闭环',
        '实现基于协同过滤的个性化课程推荐和基于K-Means的用户行为聚类分析',
        '集成评论情感分析、用户画像构建、RFM分层等数据分析功能',
        '提供完善的后台运营管理功能，包括公告、资讯、订单、文件等模块的管理'
    ]
    for goal in goals:
        add_bullet_paragraph(doc, goal)

    add_heading_custom(doc, '1.3 系统架构', level=2)
    add_paragraph_custom(doc,
        '本系统采用经典的前后端分离B/S架构，前端使用Vue 2.6构建用户界面，后端采用SpringBoot 2.5.9提供RESTful API服务，'
        '数据持久化层使用MySQL数据库，通过MyBatis实现对象关系映射。')
    add_paragraph_custom(doc,
        '系统整体架构分为三个层次：前端展示层负责用户交互和界面渲染，后端服务层负责业务逻辑处理和权限认证，数据持久层负责数据存储和查询。'
        '前后端通过HTTP/REST API进行数据交互，采用JWT实现无状态认证。')

    add_heading_custom(doc, '1.4 核心功能概览', level=2)
    overview_data = [
        ['课程展示', '课程列表、课程详情、章节管理、视频/资料资源播放与下载'],
        ['用户学习', '学习计划制定、学习记录追踪、课堂笔记、每日签到打卡'],
        ['积分兑换', '积分商品浏览、积分兑换、积分订单管理'],
        ['支付宝支付', '课程/资料在线购买、支付回调、订单状态管理'],
        ['数据分析', '情感分析、用户聚类、学习成效分析、用户画像、RFM分层']
    ]
    create_table_with_header(doc, ['功能领域', '功能描述'], overview_data)

    doc.add_page_break()

    # ========== 2. 技术架构 ==========
    add_heading_custom(doc, '2. 技术架构', level=1)

    add_heading_custom(doc, '2.1 系统架构图', level=2)
    add_paragraph_custom(doc, '系统采用前后端分离的B/S三层架构，具体结构如下：')
    arch_lines = [
        '┌─────────────────────────────────────────────────────────────┐',
        '│                       前端展示层 (Vue 2.6)                   │',
        '│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │',
        '│  │ 用户前台 │  │ 管理后台 │  │ ElementUI│  │  ECharts │   │',
        '│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │',
        '└─────────────────────────────────────────────────────────────┘',
        '                              ↕ HTTP/REST API + JWT Token',
        '┌─────────────────────────────────────────────────────────────┐',
        '│                      后端服务层 (SpringBoot)                 │',
        '│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │',
        '│  │Controller│  │  Service │  │   Mapper │  │  算法引擎 │   │',
        '│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │',
        '│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │',
        '│  │ JWT认证  │  │ 支付宝SDK│  │PageHelper│  │  Hutool  │   │',
        '│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │',
        '└─────────────────────────────────────────────────────────────┘',
        '                              ↕ MyBatis ORM',
        '┌─────────────────────────────────────────────────────────────┐',
        '│                      数据持久层 (MySQL)                      │',
        '│         业务数据表（15张）+ 缓存 + 文件存储                   │',
        '└─────────────────────────────────────────────────────────────┘'
    ]
    for line in arch_lines:
        p = add_paragraph_custom(doc, line, size=9)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_heading_custom(doc, '2.2 技术栈详情', level=2)

    add_heading_custom(doc, '2.2.1 前端技术栈', level=3)
    frontend_tech = [
        ('Vue 2.6.14', '渐进式JavaScript框架，采用组件化开发模式构建用户界面'),
        ('Vue Router 3.5.1', '官方路由管理器，实现单页应用（SPA）的页面切换和导航守卫'),
        ('Vuex 3.6.2', '集中式状态管理，统一管理用户信息、购物车等全局状态'),
        ('Element UI 2.15.14', '基于Vue的组件库，提供表格、表单、对话框等丰富的UI组件'),
        ('Axios 1.5.1', 'HTTP客户端，用于前后端数据交互，支持请求拦截和响应处理'),
        ('ECharts 5.5.0', '开源可视化库，用于数据图表展示，支持折线图、饼图、雷达图等'),
        ('WangEditor 4.7.15', '富文本编辑器，用于公告、资讯等内容的编辑和发布')
    ]
    for tech, desc in frontend_tech:
        add_bullet_paragraph(doc, f'{tech}：{desc}')

    add_heading_custom(doc, '2.2.2 后端技术栈', level=3)
    backend_tech = [
        ('SpringBoot 2.5.9', '简化Spring应用开发的框架，内置Tomcat容器，开箱即用'),
        ('MyBatis 2.2.1', '持久层框架，通过XML或注解实现对象关系映射（ORM）'),
        ('PageHelper 1.4.6', 'MyBatis分页插件，支持物理分页和多种数据库方言'),
        ('JWT 4.3.0', 'JSON Web Token，实现无状态用户认证和权限校验'),
        ('Hutool 5.8.18', 'Java工具类库，提供日期处理、文件操作、加密解密等工具'),
        ('支付宝SDK 4.35.79', '官方支付SDK，实现订单创建、支付唤起、回调验签等功能')
    ]
    for tech, desc in backend_tech:
        add_bullet_paragraph(doc, f'{tech}：{desc}')

    add_heading_custom(doc, '2.2.3 数据库', level=3)
    add_bullet_paragraph(doc, 'MySQL 5.7+：关系型数据库，使用InnoDB存储引擎，支持事务和行级锁')
    add_bullet_paragraph(doc, '字符集：utf8mb4，支持完整的Unicode字符（包括Emoji）')
    add_bullet_paragraph(doc, '数据库名称：manager，共包含15张业务数据表')

    doc.add_page_break()

    # ========== 3. 功能模块 ==========
    add_heading_custom(doc, '3. 功能模块', level=1)

    add_heading_custom(doc, '3.1 用户体系', level=2)
    user_modules = [
        ('注册/登录', '支持用户账号密码注册和登录，密码采用MD5加密存储，JWT Token实现会话管理'),
        ('个人信息管理', '用户可以修改头像、昵称、手机号、邮箱等个人信息'),
        ('角色权限控制', '系统支持ADMIN（管理员）和USER（普通用户）两种角色，通过JWT载荷中的role字段进行权限区分')
    ]
    for name, desc in user_modules:
        add_bullet_paragraph(doc, f'{name}：{desc}')

    add_heading_custom(doc, '3.2 课程管理', level=2)
    course_modules = [
        ('课程展示', '前台以卡片列表形式展示课程，支持按分类筛选、排序和分页'),
        ('课程详情', '展示课程封面、简介、价格、章节列表、评论等信息'),
        ('章节管理', '每门课程包含多个章节，支持视频和图文两种内容形式'),
        ('视频/资料资源', '课程支持视频播放和资料文件下载，资源文件通过独立接口上传和管理')
    ]
    for name, desc in course_modules:
        add_bullet_paragraph(doc, f'{name}：{desc}')

    add_heading_custom(doc, '3.3 学习服务', level=2)
    learning_modules = [
        ('学习计划', '用户可制定个性化学习计划，设置目标课程、每日学习时长、起止日期等'),
        ('学习记录', '系统自动记录用户的学习时长、学习进度、上次观看位置等信息'),
        ('学习笔记', '用户在观看课程视频时可随时记录笔记，笔记关联到具体视频时间点'),
        ('每日签到', '用户每日签到可获得积分奖励，系统记录连续签到天数')
    ]
    for name, desc in learning_modules:
        add_bullet_paragraph(doc, f'{name}：{desc}')

    add_heading_custom(doc, '3.4 互动评价', level=2)
    interact_modules = [
        ('课程评论', '用户可对课程发表评论，支持回复他人的评论，形成讨论区'),
        ('评分打分', '用户可对已购课程进行评分，评分数据用于课程热度排序'),
        ('订单交易', '支持课程购买和资料兑换两种交易类型，订单记录包含订单号、金额、时间等信息')
    ]
    for name, desc in interact_modules:
        add_bullet_paragraph(doc, f'{name}：{desc}')

    add_heading_custom(doc, '3.5 运营管理', level=2)
    admin_modules = [
        ('公告管理', '管理员可发布、编辑、删除系统公告，公告会在前台首页展示'),
        ('资讯发布', '管理员可发布学习资讯和资料，支持富文本编辑和文件上传'),
        ('文件管理', '提供统一的文件上传和下载接口，支持图片、视频、文档等多种文件类型'),
        ('订单管理', '管理员可查看所有课程订单和资料订单，支持分页查询和状态管理')
    ]
    for name, desc in admin_modules:
        add_bullet_paragraph(doc, f'{name}：{desc}')

    add_heading_custom(doc, '3.6 数据分析', level=2)
    data_modules = [
        ('情感分析', '基于情感词典对课程评论进行正向/负向情感分类，生成情感趋势报告'),
        ('用户行为聚类', '使用K-Means算法对用户6维行为特征进行聚类，划分为4个用户群体'),
        ('学习成效分析', '分析用户的学习时长、完成率、笔记数量等指标，评估学习效果'),
        ('用户画像', '基于用户行为数据构建多维用户画像，包含学习偏好、消费能力等标签'),
        ('RFM分层', '根据用户的最近消费时间（Recency）、消费频率（Frequency）、消费金额（Monetary）进行用户价值分层')
    ]
    for name, desc in data_modules:
        add_bullet_paragraph(doc, f'{name}：{desc}')

    add_heading_custom(doc, '3.7 功能流程图', level=2)
    add_paragraph_custom(doc, '用户购课流程：', bold=True)
    add_paragraph_custom(doc,
        '浏览课程 → 查看详情 → 立即购买 → 创建订单 → 支付宝支付 → 异步回调验签 → 更新订单状态 → 获得课程访问权限 → 开始学习')
    add_paragraph_custom(doc, '用户学习流程：', bold=True)
    add_paragraph_custom(doc,
        '登录系统 → 进入学习中心 → 制定学习计划 → 选择课程 → 观看视频/阅读图文 → 记录学习进度 → 记笔记 → 完成学习')
    add_paragraph_custom(doc, '积分兑换流程：', bold=True)
    add_paragraph_custom(doc,
        '浏览积分商品 → 选择商品 → 确认兑换 → 扣除积分 → 生成积分订单 → 获得资料下载权限')

    doc.add_page_break()

    # ========== 4. 数据库设计 ==========
    add_heading_custom(doc, '4. 数据库设计', level=1)

    add_heading_custom(doc, '4.1 数据库概述', level=2)
    add_bullet_paragraph(doc, '数据库名称：manager')
    add_bullet_paragraph(doc, '字符集：utf8mb4')
    add_bullet_paragraph(doc, '存储引擎：InnoDB')
    add_bullet_paragraph(doc, '总表数：15张业务数据表')

    add_heading_custom(doc, '4.2 数据表结构', level=2)

    # 1. admin 表
    create_db_table(doc, 'admin', '管理员信息表', [
        ('id', 'int', '主键，自增'),
        ('username', 'varchar(255)', '用户名'),
        ('password', 'varchar(255)', '密码（MD5加密）'),
        ('name', 'varchar(255)', '姓名'),
        ('phone', 'varchar(255)', '电话'),
        ('email', 'varchar(255)', '邮箱'),
        ('avatar', 'varchar(255)', '头像URL'),
        ('role', 'varchar(255)', '角色（ADMIN）')
    ])

    # 2. user 表
    create_db_table(doc, 'user', '用户信息表', [
        ('id', 'int', '主键，自增'),
        ('username', 'varchar(255)', '用户名'),
        ('password', 'varchar(255)', '密码（MD5加密）'),
        ('name', 'varchar(255)', '姓名/昵称'),
        ('avatar', 'varchar(255)', '头像URL'),
        ('role', 'varchar(255)', '角色（ADMIN/USER）'),
        ('phone', 'varchar(255)', '电话'),
        ('email', 'varchar(255)', '邮箱'),
        ('member', 'varchar(255)', '会员状态'),
        ('score', 'int', '积分余额'),
        ('account', 'double', '账户余额')
    ])

    # 3. course 表
    create_db_table(doc, 'course', '课程信息表', [
        ('id', 'int', '主键，自增'),
        ('img', 'varchar(255)', '封面图片URL'),
        ('name', 'varchar(255)', '课程名称'),
        ('content', 'text', '课程内容描述'),
        ('type', 'varchar(255)', '类型（VIDEO/TEXT）'),
        ('price', 'double', '课程价格'),
        ('video', 'varchar(255)', '视频文件URL'),
        ('file', 'varchar(255)', '资料文件URL'),
        ('discount', 'double', '折扣价格'),
        ('recommend', 'varchar(255)', '是否推荐（是/否）'),
        ('time', 'varchar(255)', '发布时间')
    ])

    # 4. orders 表
    create_db_table(doc, 'orders', '课程订单表', [
        ('id', 'int', '主键，自增'),
        ('course_id', 'int', '课程ID'),
        ('price', 'double', '订单金额'),
        ('order_id', 'varchar(255)', '订单编号'),
        ('time', 'varchar(255)', '下单时间'),
        ('user_id', 'int', '用户ID'),
        ('course_type', 'varchar(255)', '课程类型')
    ])

    # 5. score 表
    create_db_table(doc, 'score', '积分商品表', [
        ('id', 'int', '主键，自增'),
        ('img', 'varchar(255)', '封面图片URL'),
        ('name', 'varchar(255)', '商品名称'),
        ('content', 'text', '商品内容描述'),
        ('type', 'varchar(255)', '商品类型'),
        ('price', 'int', '所需积分'),
        ('video', 'varchar(255)', '视频文件URL'),
        ('file', 'varchar(255)', '资料文件URL'),
        ('recommend', 'varchar(255)', '是否推荐（是/否）'),
        ('time', 'varchar(255)', '发布时间')
    ])

    # 6. scoreorder 表
    create_db_table(doc, 'scoreorder', '积分兑换记录表', [
        ('id', 'int', '主键，自增'),
        ('score_id', 'int', '积分商品ID'),
        ('score', 'int', '消耗积分'),
        ('order_id', 'varchar(255)', '订单编号'),
        ('time', 'varchar(255)', '兑换时间'),
        ('user_id', 'int', '用户ID')
    ])

    # 7. fileorder 表
    create_db_table(doc, 'fileorder', '资料订单表', [
        ('id', 'int', '主键，自增'),
        ('file_id', 'int', '资料ID'),
        ('score', 'int', '消耗积分'),
        ('order_id', 'varchar(255)', '订单编号'),
        ('time', 'varchar(255)', '兑换时间'),
        ('user_id', 'int', '用户ID')
    ])

    # 8. comment 表
    create_db_table(doc, 'comment', '评论表', [
        ('id', 'int', '主键，自增'),
        ('user_id', 'int', '用户ID'),
        ('course_id', 'int', '课程ID'),
        ('time', 'varchar(255)', '评论时间'),
        ('content', 'text', '评论内容'),
        ('parent_id', 'int', '父评论ID，支持回复')
    ])

    # 9. notice 表
    create_db_table(doc, 'notice', '公告表', [
        ('id', 'int', '主键，自增'),
        ('title', 'varchar(255)', '公告标题'),
        ('content', 'text', '公告内容'),
        ('time', 'varchar(255)', '发布时间'),
        ('user', 'varchar(255)', '发布人')
    ])

    # 10. information 表
    create_db_table(doc, 'information', '资讯/资料表', [
        ('id', 'int', '主键，自增'),
        ('name', 'varchar(255)', '资料名称'),
        ('content', 'text', '资料内容'),
        ('file', 'varchar(255)', '文件URL'),
        ('img', 'varchar(255)', '封面图片URL'),
        ('score', 'int', '所需积分'),
        ('time', 'varchar(255)', '发布时间'),
        ('recommend', 'varchar(255)', '是否推荐'),
        ('user_id', 'int', '上传用户ID'),
        ('status', 'varchar(255)', '审核状态'),
        ('descr', 'varchar(255)', '描述')
    ])

    # 11. signin 表
    create_db_table(doc, 'signin', '签到记录表', [
        ('id', 'int', '主键，自增'),
        ('user_id', 'int', '用户ID'),
        ('time', 'varchar(255)', '签到时间'),
        ('day', 'varchar(255)', '连续签到天数')
    ])

    # 12. recharge_record 表
    create_db_table(doc, 'recharge_record', '充值记录表', [
        ('id', 'int', '主键，自增'),
        ('recordid', 'varchar(255)', '记录编号'),
        ('price', 'double', '充值金额'),
        ('time', 'varchar(255)', '充值时间'),
        ('user_id', 'int', '用户ID'),
        ('method', 'varchar(255)', '支付方式')
    ])

    # 13. learning_record 表
    create_db_table(doc, 'learning_record', '学习记录表', [
        ('id', 'int', '主键，自增'),
        ('user_id', 'int', '用户ID'),
        ('course_id', 'int', '课程ID'),
        ('course_name', 'varchar(255)', '课程名称'),
        ('course_type', 'varchar(255)', '课程类型'),
        ('duration', 'int', '学习时长（分钟）'),
        ('progress', 'double', '学习进度（0-100%）'),
        ('last_position', 'varchar(255)', '上次观看位置'),
        ('create_time', 'varchar(255)', '创建时间'),
        ('update_time', 'varchar(255)', '更新时间')
    ])

    # 14. learning_plan 表
    create_db_table(doc, 'learning_plan', '学习计划表', [
        ('id', 'int', '主键，自增'),
        ('user_id', 'int', '用户ID'),
        ('title', 'varchar(255)', '计划标题'),
        ('content', 'text', '计划内容'),
        ('target_course_id', 'int', '目标课程ID'),
        ('daily_goal', 'int', '每日目标（分钟）'),
        ('start_date', 'varchar(255)', '开始日期'),
        ('end_date', 'varchar(255)', '结束日期'),
        ('status', 'varchar(255)', '计划状态'),
        ('progress', 'double', '完成进度（0-100%）'),
        ('create_time', 'varchar(255)', '创建时间'),
        ('update_time', 'varchar(255)', '更新时间')
    ])

    # 15. note 表
    create_db_table(doc, 'note', '课堂笔记表', [
        ('id', 'int', '主键，自增'),
        ('user_id', 'int', '用户ID'),
        ('course_id', 'int', '课程ID'),
        ('course_name', 'varchar(255)', '课程名称'),
        ('title', 'varchar(255)', '笔记标题'),
        ('content', 'text', '笔记内容'),
        ('video_time', 'varchar(255)', '视频时间点'),
        ('create_time', 'varchar(255)', '创建时间'),
        ('update_time', 'varchar(255)', '更新时间')
    ])

    doc.add_page_break()

    # ========== 5. API接口文档 ==========
    add_heading_custom(doc, '5. API接口文档', level=1)

    add_heading_custom(doc, '5.1 接口规范', level=2)
    add_bullet_paragraph(doc, '接口协议：HTTP/HTTPS')
    add_bullet_paragraph(doc, '数据格式：JSON')
    add_bullet_paragraph(doc, '请求方式：GET、POST、PUT、DELETE')
    add_bullet_paragraph(doc, '统一响应格式：{ code: "200", msg: "", data: {} }')
    add_bullet_paragraph(doc, '认证方式：JWT Token，通过请求头 Authorization 传递')
    add_bullet_paragraph(doc, '后端服务地址：http://localhost:9090')
    add_bullet_paragraph(doc, '前端访问地址：http://localhost:8080')

    add_heading_custom(doc, '5.2 接口列表', level=2)

    # WebController
    add_heading_custom(doc, '5.2.1 WebController（认证接口）', level=3)
    web_apis = [
        ('POST /login', '用户登录', 'username, password'),
        ('POST /register', '用户注册', 'username, password, name, role'),
        ('PUT /updatePassword', '修改密码', 'username, oldPassword, newPassword'),
        ('GET /logout', '退出登录', 'Token')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], web_apis)
    doc.add_paragraph()

    # UserController
    add_heading_custom(doc, '5.2.2 UserController（用户管理）', level=3)
    user_apis = [
        ('POST /user/add', '添加用户', '用户信息'),
        ('PUT /user/update', '修改用户', '用户信息'),
        ('DELETE /user/delete/{id}', '删除用户', '用户ID'),
        ('GET /user/selectPage', '分页查询用户', 'pageNum, pageSize, name'),
        ('GET /user/{id}', '根据ID查询用户', '用户ID'),
        ('GET /user/scoreRank', '积分排行榜', '无'),
        ('GET /user/myInfo', '获取当前用户信息', 'Token')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], user_apis)
    doc.add_paragraph()

    # AdminController
    add_heading_custom(doc, '5.2.3 AdminController（管理员管理）', level=3)
    admin_apis = [
        ('POST /admin/add', '添加管理员', '管理员信息'),
        ('PUT /admin/update', '修改管理员', '管理员信息'),
        ('DELETE /admin/delete/{id}', '删除管理员', '管理员ID'),
        ('GET /admin/selectPage', '分页查询管理员', 'pageNum, pageSize, name')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], admin_apis)
    doc.add_paragraph()

    # CourseController
    add_heading_custom(doc, '5.2.4 CourseController（课程管理）', level=3)
    course_apis = [
        ('POST /course/add', '添加课程', '课程信息'),
        ('PUT /course/update', '修改课程', '课程信息'),
        ('DELETE /course/delete/{id}', '删除课程', '课程ID'),
        ('GET /course/selectPage', '分页查询课程', 'pageNum, pageSize, name'),
        ('GET /course/{id}', '根据ID查询课程', '课程ID'),
        ('GET /course/recommend', '获取推荐课程', '无'),
        ('GET /course/hot', '获取热门课程', '无'),
        ('GET /course/search', '搜索课程', 'name')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], course_apis)
    doc.add_paragraph()

    # OrdersController
    add_heading_custom(doc, '5.2.5 OrdersController（课程订单管理）', level=3)
    orders_apis = [
        ('POST /orders/add', '创建订单', '订单信息'),
        ('GET /orders/selectPage', '分页查询订单', 'pageNum, pageSize, userId'),
        ('GET /orders/{id}', '根据ID查询订单', '订单ID'),
        ('DELETE /orders/{id}', '删除订单', '订单ID')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], orders_apis)
    doc.add_paragraph()

    # AliPayController
    add_heading_custom(doc, '5.2.6 AliPayController（支付宝支付）', level=3)
    alipay_apis = [
        ('GET /alipay/pay', '发起支付', 'orderId, amount'),
        ('POST /alipay/notify', '支付异步回调', '支付宝回调参数'),
        ('GET /alipay/return', '支付同步返回', '支付宝返回参数')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], alipay_apis)
    doc.add_paragraph()

    # ScoreController
    add_heading_custom(doc, '5.2.7 ScoreController（积分商品管理）', level=3)
    score_apis = [
        ('POST /score/add', '添加积分商品', '商品信息'),
        ('PUT /score/update', '修改积分商品', '商品信息'),
        ('DELETE /score/delete/{id}', '删除积分商品', '商品ID'),
        ('GET /score/selectPage', '分页查询积分商品', 'pageNum, pageSize, name'),
        ('GET /score/recommend', '获取推荐积分商品', '无')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], score_apis)
    doc.add_paragraph()

    # ScoreorderController
    add_heading_custom(doc, '5.2.8 ScoreorderController（积分兑换管理）', level=3)
    scoreorder_apis = [
        ('POST /scoreorder/add', '创建积分兑换订单', '兑换信息'),
        ('GET /scoreorder/selectPage', '分页查询积分订单', 'pageNum, pageSize, userId')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], scoreorder_apis)
    doc.add_paragraph()

    # CommentController
    add_heading_custom(doc, '5.2.9 CommentController（评论管理）', level=3)
    comment_apis = [
        ('POST /comment/add', '发表评论', '评论信息'),
        ('GET /comment/selectAll', '查询所有评论', 'courseId'),
        ('DELETE /comment/delete/{id}', '删除评论', '评论ID'),
        ('PUT /comment/update', '修改评论', '评论信息')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], comment_apis)
    doc.add_paragraph()

    # SigninController
    add_heading_custom(doc, '5.2.10 SigninController（签到管理）', level=3)
    signin_apis = [
        ('POST /signin/add', '用户签到', '用户ID'),
        ('GET /signin/selectPage', '分页查询签到记录', 'pageNum, pageSize, userId'),
        ('GET /signin/continuousDays', '获取连续签到天数', '用户ID')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], signin_apis)
    doc.add_paragraph()

    # LearningRecordController
    add_heading_custom(doc, '5.2.11 LearningRecordController（学习记录管理）', level=3)
    lr_apis = [
        ('POST /learningRecord/add', '添加学习记录', '学习记录信息'),
        ('PUT /learningRecord/update', '更新学习记录', '学习记录信息'),
        ('GET /learningRecord/selectPage', '分页查询学习记录', 'pageNum, pageSize, userId')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], lr_apis)
    doc.add_paragraph()

    # LearningPlanController
    add_heading_custom(doc, '5.2.12 LearningPlanController（学习计划管理）', level=3)
    lp_apis = [
        ('POST /learningPlan/add', '添加学习计划', '学习计划信息'),
        ('PUT /learningPlan/update', '更新学习计划', '学习计划信息'),
        ('GET /learningPlan/selectPage', '分页查询学习计划', 'pageNum, pageSize, userId')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], lp_apis)
    doc.add_paragraph()

    # NoteController
    add_heading_custom(doc, '5.2.13 NoteController（笔记管理）', level=3)
    note_apis = [
        ('POST /note/add', '添加笔记', '笔记信息'),
        ('PUT /note/update', '更新笔记', '笔记信息'),
        ('GET /note/selectPage', '分页查询笔记', 'pageNum, pageSize, userId'),
        ('DELETE /note/delete/{id}', '删除笔记', '笔记ID')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], note_apis)
    doc.add_paragraph()

    # NoticeController
    add_heading_custom(doc, '5.2.14 NoticeController（公告管理）', level=3)
    notice_apis = [
        ('POST /notice/add', '添加公告', '公告信息'),
        ('PUT /notice/update', '更新公告', '公告信息'),
        ('DELETE /notice/delete/{id}', '删除公告', '公告ID'),
        ('GET /notice/selectPage', '分页查询公告', 'pageNum, pageSize, title')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], notice_apis)
    doc.add_paragraph()

    # InformationController
    add_heading_custom(doc, '5.2.15 InformationController（资讯管理）', level=3)
    info_apis = [
        ('POST /information/add', '添加资讯', '资讯信息'),
        ('PUT /information/update', '更新资讯', '资讯信息'),
        ('DELETE /information/delete/{id}', '删除资讯', '资讯ID'),
        ('GET /information/selectPage', '分页查询资讯', 'pageNum, pageSize, name')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], info_apis)
    doc.add_paragraph()

    # FileController
    add_heading_custom(doc, '5.2.16 FileController（文件管理）', level=3)
    file_apis = [
        ('POST /file/upload', '文件上传', 'file'),
        ('GET /file/download/{fileName}', '文件下载', 'fileName')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], file_apis)
    doc.add_paragraph()

    # DataAnalysisController
    add_heading_custom(doc, '5.2.17 DataAnalysisController（数据分析）', level=3)
    da_apis = [
        ('GET /analysis/userProfile/{userId}', '获取用户画像', '用户ID'),
        ('GET /analysis/rfmSegment', 'RFM用户分层', '无'),
        ('GET /analysis/learningProgress', '学习进度分析', '无'),
        ('GET /analysis/overallStatistics', '整体统计', '无'),
        ('GET /analysis/coursePopularity', '课程热度分析', '无'),
        ('POST /analysis/clustering', '执行聚类分析', '聚类参数'),
        ('GET /analysis/clustering/result', '获取聚类结果', '无')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], da_apis)
    doc.add_paragraph()

    # UserClusterController
    add_heading_custom(doc, '5.2.18 UserClusterController（用户聚类）', level=3)
    uc_apis = [
        ('POST /cluster/perform', '执行用户聚类', '聚类参数'),
        ('GET /cluster/result', '获取聚类结果', '无'),
        ('GET /cluster/segmentAnalysis', '获取群体分析', '无')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], uc_apis)
    doc.add_paragraph()

    # SentimentController
    add_heading_custom(doc, '5.2.19 SentimentController（情感分析）', level=3)
    sentiment_apis = [
        ('POST /sentiment/analyze', '执行情感分析', '评论内容'),
        ('GET /sentiment/report', '获取情感分析报告', '无'),
        ('GET /sentiment/trend', '获取情感趋势', 'courseId')
    ]
    create_table_with_header(doc, ['接口', '说明', '主要参数'], sentiment_apis)
    doc.add_paragraph()

    # ChapterController
    add_heading_custom(doc, '5.2.20 ChapterController（章节管理）', level=3)
    add_paragraph_custom(doc, '提供课程章节的增删改查接口，支持视频和图文两种内容类型的章节管理。')

    # FileorderController
    add_heading_custom(doc, '5.2.21 FileorderController（资料订单管理）', level=3)
    add_paragraph_custom(doc, '提供资料兑换订单的创建、查询、删除等接口，支持积分兑换资料的订单管理。')

    # ProxyController
    add_heading_custom(doc, '5.2.22 ProxyController（代理服务）', level=3)
    add_paragraph_custom(doc, '提供代理转发服务，用于处理外部资源请求和跨域接口转发。')

    # RecordController
    add_heading_custom(doc, '5.2.23 RecordController（记录管理）', level=3)
    add_paragraph_custom(doc, '提供各类业务记录（如充值记录等）的查询和管理接口。')

    doc.add_page_break()

    # ========== 6. 核心算法设计 ==========
    add_heading_custom(doc, '6. 核心算法设计', level=1)

    # 6.1 协同过滤推荐算法
    add_heading_custom(doc, '6.1 协同过滤推荐算法', level=2)
    add_paragraph_custom(doc,
        '系统采用基于用户的协同过滤算法（User-based Collaborative Filtering）实现个性化课程推荐。'
        '该算法的核心思想是：找到与当前用户兴趣相似的其他用户，然后将这些相似用户喜欢但当前用户未购买的课程推荐给当前用户。')

    add_heading_custom(doc, '6.1.1 算法流程', level=3)
    cf_steps = [
        '构建用户-课程矩阵：从订单表（orders）和积分兑换记录表（scoreorder）中提取用户行为数据，构建用户-课程交互矩阵',
        '计算Jaccard相似系数：对每对用户计算其课程集合的Jaccard相似度',
        '查找Top-5相似用户：按相似度降序排序，选择前5个最相似用户',
        '生成推荐列表：从相似用户的购买记录中筛选当前用户未购买的课程，按购买频次加权排序',
        '热门课程兜底：当推荐数量不足时，补充系统中销量最高的热门课程作为兜底推荐'
    ]
    for i, step in enumerate(cf_steps, 1):
        add_number_paragraph(doc, step)

    add_heading_custom(doc, '6.1.2 Jaccard相似系数', level=3)
    add_paragraph_custom(doc, 'Jaccard相似系数用于衡量两个用户课程集合的相似程度，计算公式如下：')
    p = add_paragraph_custom(doc, 'J(A, B) = |A ∩ B| / |A ∪ B|', size=11)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_paragraph_custom(doc, '其中：')
    add_bullet_paragraph(doc, 'A：用户A购买/兑换的课程集合')
    add_bullet_paragraph(doc, 'B：用户B购买/兑换的课程集合')
    add_bullet_paragraph(doc, '|A ∩ B|：两个用户共同购买/兑换的课程数量')
    add_bullet_paragraph(doc, '|A ∪ B|：两个用户购买/兑换课程的总数（去重）')
    add_paragraph_custom(doc,
        'Jaccard系数的取值范围为[0, 1]，值越大表示两个用户的兴趣越相似。'
        '当两个用户没有共同课程时，相似度为0；当两个用户的课程集合完全相同时，相似度为1。')

    add_heading_custom(doc, '6.1.3 推荐生成策略', level=3)
    add_paragraph_custom(doc,
        '在获取Top-5相似用户后，系统会收集这些用户的所有课程行为记录，排除当前用户已购买的课程，'
        '然后按照课程的购买频次进行加权排序。最终推荐列表包含最多N门课程，如果候选课程不足，'
        '则从热门课程中补充，确保推荐列表的完整性。')

    # 6.2 K-Means用户聚类分析
    add_heading_custom(doc, '6.2 K-Means用户聚类分析', level=2)
    add_paragraph_custom(doc,
        '系统使用K-Means聚类算法对用户进行行为分析，将用户划分为不同的群体，以便进行精准运营和个性化服务。')

    add_heading_custom(doc, '6.2.1 特征向量构建', level=3)
    add_paragraph_custom(doc, '每个用户用一个6维特征向量表示：')
    feature_data = [
        ['维度1', '购买课程数', '用户历史购买/兑换的课程总数'],
        ['维度2', '课程消费额', '用户在课程上的总消费金额'],
        ['维度3', '学习时长', '用户累计学习时长（分钟）'],
        ['维度4', '学习频次', '用户学习的频率（次/周）'],
        ['维度5', '签到天数', '用户累计签到天数'],
        ['维度6', '活跃度', '综合活跃度评分（评论、收藏、分享等行为加权）']
    ]
    create_table_with_header(doc, ['维度', '特征名称', '说明'], feature_data)
    doc.add_paragraph()

    add_heading_custom(doc, '6.2.2 数据预处理', level=3)
    add_paragraph_custom(doc, '由于各维度数据的量纲和取值范围不同，需要进行Min-Max标准化处理：')
    p = add_paragraph_custom(doc, 'x\' = (x - min) / (max - min)', size=11)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_paragraph_custom(doc,
        '通过Min-Max标准化，将每个维度的数据映射到[0, 1]区间，消除量纲影响，使不同维度的特征具有可比性。')

    add_heading_custom(doc, '6.2.3 聚类过程', level=3)
    kmeans_steps = [
        '初始化：随机选择K=4个初始聚类中心',
        '分配：将每个用户分配到距离最近的聚类中心所在的簇',
        '更新：重新计算每个簇的质心作为新的聚类中心',
        '迭代：重复分配和更新步骤，直到聚类中心不再变化或达到最大迭代次数',
        '评估：使用轮廓系数（Silhouette Coefficient）评估聚类效果'
    ]
    for i, step in enumerate(kmeans_steps, 1):
        add_number_paragraph(doc, step)

    add_heading_custom(doc, '6.2.4 用户群体划分结果', level=3)
    cluster_data = [
        ['群体1', '流失风险用户', '购买少、学习少、签到少', '推送优惠活动、发送召回邮件'],
        ['群体2', '低活跃用户', '偶尔学习、消费较低', '推荐免费课程、增加积分激励'],
        ['群体3', '一般活跃用户', '有一定学习行为', '推荐进阶课程、引导消费升级'],
        ['群体4', '高价值用户', '高消费、高频学习', '提供VIP服务、优先客服支持']
    ]
    create_table_with_header(doc, ['群体', '名称', '特征', '运营策略'], cluster_data)
    doc.add_paragraph()

    # 6.3 评论情感分析
    add_heading_custom(doc, '6.3 评论情感分析', level=3)
    add_paragraph_custom(doc,
        '系统基于情感词典实现评论情感分析，采用规则匹配方法对课程评论进行正向/负向情感分类。')

    add_heading_custom(doc, '6.3.1 情感词典构建', level=3)
    dict_data = [
        ['正面词', '120个', '如"优秀"、"精彩"、"实用"、"推荐"等'],
        ['负面词', '120个', '如"差劲"、"失望"、"难懂"、"后悔"等'],
        ['否定词', '15个', '如"不"、"没"、"非"、"无"等'],
        ['程度词', '25个', '如"非常"、"特别"、"比较"、"稍微"等（含权重）']
    ]
    create_table_with_header(doc, ['词典类型', '词数', '说明'], dict_data)
    doc.add_paragraph()

    add_heading_custom(doc, '6.3.2 分析流程', level=3)
    sentiment_steps = [
        '正向最大匹配分词：将评论文本按照词典进行分词，采用正向最大匹配策略',
        '情感词识别：遍历分词结果，识别正面词和负面词',
        '否定词反转：若情感词前存在否定词，则将该情感词的极性反转（正变负，负变正）',
        '程度词加权：若情感词前存在程度词，则根据程度词的权重对情感得分进行加权',
        '情感分类：汇总评论中所有情感词的得分，若总分大于0则判定为正向，小于0为负向，等于0为中性'
    ]
    for i, step in enumerate(sentiment_steps, 1):
        add_number_paragraph(doc, step)

    add_paragraph_custom(doc,
        '情感分析的结果用于生成课程的情感报告和趋势分析，帮助管理员了解用户对课程的满意度变化。')

    # 6.4 JWT无状态认证
    add_heading_custom(doc, '6.4 JWT无状态认证', level=2)
    add_paragraph_custom(doc,
        '系统使用JWT（JSON Web Token）实现无状态用户认证，避免了传统Session机制带来的服务端存储压力和分布式部署问题。')

    add_heading_custom(doc, '6.4.1 Token结构', level=3)
    add_paragraph_custom(doc, 'JWT由三部分组成，用"."分隔：')
    jwt_data = [
        ['Header', '包含Token类型和签名算法', '{"alg": "HS256", "typ": "JWT"}'],
        ['Payload', '包含用户ID和角色信息', '{"userId": 1, "role": "USER"}'],
        ['Signature', 'HMAC256签名', 'HMACSHA256(base64Url(header) + "." + base64Url(payload), secret)']
    ]
    create_table_with_header(doc, ['部分', '说明', '示例'], jwt_data)
    doc.add_paragraph()

    add_heading_custom(doc, '6.4.2 Token生成规则', level=3)
    add_bullet_paragraph(doc, '载荷：包含userId和role字段')
    add_bullet_paragraph(doc, '签名算法：HMAC256（HS256）')
    add_bullet_paragraph(doc, '密钥：使用用户密码作为签名密钥')
    add_bullet_paragraph(doc, '有效期：2小时（7200秒）')

    add_heading_custom(doc, '6.4.3 认证流程', level=3)
    jwt_flow = [
        '用户登录成功后，服务端验证用户名密码，生成JWT Token并返回给客户端',
        '客户端将Token存储在localStorage中，后续请求通过请求头Authorization携带Token',
        '服务端JWT拦截器解析Token，验证签名和过期时间',
        'Token验证通过后，从Payload中提取userId和role，查询数据库验证用户存在且状态正常',
        '验证通过后放行请求，否则返回401未授权错误'
    ]
    for i, step in enumerate(jwt_flow, 1):
        add_number_paragraph(doc, step)

    # 6.5 支付宝支付流程
    add_heading_custom(doc, '6.5 支付宝支付流程', level=2)
    add_paragraph_custom(doc,
        '系统集成支付宝SDK实现在线支付功能，支持用户通过支付宝完成课程购买和账户充值。')

    add_heading_custom(doc, '6.5.1 支付流程', level=3)
    pay_steps = [
        '创建订单：用户选择课程后点击购买，系统创建订单记录，生成唯一订单号',
        '调用支付宝SDK：系统使用订单信息（订单号、金额、商品名称等）调用支付宝SDK生成支付表单',
        '用户支付：前端自动跳转到支付宝收银台，用户完成扫码或密码支付',
        '异步回调：支付宝支付完成后，向系统指定的notify_url发送异步通知',
        '验签更新：系统收到回调后，使用支付宝公钥验证签名，确认支付结果后更新订单状态',
        '权限开通：订单状态更新为"已支付"后，用户获得课程的访问权限'
    ]
    for i, step in enumerate(pay_steps, 1):
        add_number_paragraph(doc, step)

    add_heading_custom(doc, '6.5.2 安全机制', level=3)
    add_bullet_paragraph(doc, '签名验证：所有支付宝回调请求均需通过RSA2签名验证，防止伪造通知')
    add_bullet_paragraph(doc, '幂等处理：同一订单的多次回调不会重复更新状态')
    add_bullet_paragraph(doc, '超时处理：订单设置有效时间，超时未支付自动关闭')
    add_bullet_paragraph(doc, '金额校验：回调中订单金额与系统记录金额一致才更新状态')

    doc.add_page_break()

    # ========== 7. 项目结构 ==========
    add_heading_custom(doc, '7. 项目结构', level=1)

    add_heading_custom(doc, '7.1 后端项目结构', level=2)
    backend_structure = '''springboot/
├── src/main/java/com/example/
│   ├── SpringbootApplication.java    # 启动类
│   ├── common/                        # 公共组件
│   │   ├── config/                    # 配置类
│   │   │   ├── CorsConfig.java        # 跨域配置
│   │   │   ├── JwtInterceptor.java    # JWT拦截器
│   │   │   └── WebConfig.java         # Web配置
│   │   ├── enums/                     # 枚举类
│   │   ├── Constants.java             # 常量定义
│   │   └── Result.java                # 统一返回结果
│   ├── controller/                    # 控制器层（23个）
│   │   ├── WebController.java         # 认证接口
│   │   ├── UserController.java        # 用户管理
│   │   ├── AdminController.java       # 管理员管理
│   │   ├── CourseController.java      # 课程管理
│   │   ├── OrdersController.java      # 订单管理
│   │   ├── AliPayController.java      # 支付宝支付
│   │   ├── ScoreController.java       # 积分商品
│   │   ├── ScoreorderController.java  # 积分兑换
│   │   ├── FileorderController.java   # 资料订单
│   │   ├── CommentController.java     # 评论管理
│   │   ├── SigninController.java      # 签到管理
│   │   ├── LearningRecordController.java  # 学习记录
│   │   ├── LearningPlanController.java    # 学习计划
│   │   ├── NoteController.java        # 笔记管理
│   │   ├── NoticeController.java      # 公告管理
│   │   ├── InformationController.java # 资讯管理
│   │   ├── FileController.java        # 文件管理
│   │   ├── DataAnalysisController.java    # 数据分析
│   │   ├── UserClusterController.java     # 用户聚类
│   │   ├── SentimentController.java   # 情感分析
│   │   ├── ChapterController.java     # 章节管理
│   │   ├── ProxyController.java       # 代理服务
│   │   └── RecordController.java      # 记录管理
│   ├── service/                       # 业务逻辑层
│   │   ├── CollaborativeFilterService.java  # 协同过滤推荐
│   │   ├── KMeansClusterService.java        # K-Means聚类
│   │   ├── SentimentAnalysisService.java    # 情感分析
│   │   ├── UserService.java
│   │   ├── CourseService.java
│   │   └── ...                        # 其他Service
│   ├── entity/                        # 实体类
│   ├── mapper/                        # 数据访问层（MyBatis）
│   └── utils/                         # 工具类
│       └── TokenUtils.java            # JWT工具
├── src/main/resources/
│   ├── application.yml                # 主配置文件
│   ├── manager.sql                    # 数据库脚本
│   └── mapper/                        # MyBatis XML映射文件
└── pom.xml                            # Maven依赖配置'''
    add_paragraph_custom(doc, backend_structure, size=9)

    add_heading_custom(doc, '7.2 前端项目结构', level=2)
    frontend_structure = '''vue/
├── src/
│   ├── api/                           # API接口封装
│   │   ├── index.js                   # Axios实例配置
│   │   └── modules/                   # 按模块封装的API
│   ├── assets/                        # 静态资源
│   │   ├── css/                       # 全局样式
│   │   └── imgs/                      # 图片资源
│   ├── components/                    # 公共组件
│   │   ├── CommonAside.vue            # 侧边栏组件
│   │   └── ...                        # 其他公共组件
│   ├── router/                        # 路由配置
│   │   ├── index.js                   # 路由入口
│   │   └── modules/                   # 路由模块
│   │       ├── manager.js             # 后台路由
│   │       └── front.js               # 前台路由
│   ├── store/                         # Vuex状态管理
│   │   ├── index.js                   # Store入口
│   │   └── modules/                   # 状态模块
│   ├── utils/                         # 工具函数
│   │   ├── request.js                 # 请求拦截器
│   │   └── ...                        # 其他工具
│   ├── views/                         # 页面视图
│   │   ├── Login.vue                  # 登录页
│   │   ├── Register.vue               # 注册页
│   │   ├── Manager.vue                # 后台布局
│   │   ├── Front.vue                  # 前台布局
│   │   ├── front/                     # 前台页面
│   │   │   ├── Home.vue               # 首页
│   │   │   ├── Course.vue             # 课程列表
│   │   │   ├── CourseDetail.vue       # 课程详情
│   │   │   ├── LearningCenter.vue     # 学习中心
│   │   │   ├── Plan.vue               # 学习计划
│   │   │   ├── Note.vue               # 我的笔记
│   │   │   ├── Score.vue              # 积分专区
│   │   │   ├── Information.vue        # 资讯中心
│   │   │   ├── Person.vue             # 个人中心
│   │   │   └── ...
│   │   └── manager/                   # 后台页面
│   │       ├── Home.vue               # 后台首页
│   │       ├── User.vue               # 用户管理
│   │       ├── Admin.vue              # 管理员管理
│   │       ├── Course.vue             # 课程管理
│   │       ├── Orders.vue             # 订单管理
│   │       ├── Score.vue              # 积分管理
│   │       ├── Comment.vue            # 评论管理
│   │       ├── Notice.vue             # 公告管理
│   │       ├── Information.vue        # 资讯管理
│   │       └── ...
│   ├── App.vue                        # 根组件
│   └── main.js                        # 入口文件
├── public/
│   ├── favicon.ico
│   └── index.html
├── package.json                       # npm依赖配置
└── vue.config.js                      # Vue CLI配置'''
    add_paragraph_custom(doc, frontend_structure, size=9)

    doc.add_page_break()

    # ========== 8. 系统部署指南 ==========
    add_heading_custom(doc, '8. 系统部署指南', level=1)

    add_heading_custom(doc, '8.1 环境要求', level=2)
    env_data = [
        ['JDK', '1.8 及以上'],
        ['MySQL', '5.7 及以上'],
        ['Node.js', '14 及以上'],
        ['Maven', '3.6 及以上'],
        ['开发IDE', 'IntelliJ IDEA / VS Code']
    ]
    create_table_with_header(doc, ['环境项', '版本要求'], env_data)
    doc.add_paragraph()

    add_heading_custom(doc, '8.2 数据库配置', level=2)
    add_number_paragraph(doc, '创建数据库：')
    add_paragraph_custom(doc, 'CREATE DATABASE manager DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;')
    add_number_paragraph(doc, '执行SQL脚本：')
    add_bullet_paragraph(doc, 'manager.sql（主表结构，包含15张业务表）', indent_level=1)
    add_bullet_paragraph(doc, 'init_data.sql（初始测试数据）', indent_level=1)
    add_number_paragraph(doc, '数据库连接信息：')
    db_conn_data = [
        ['地址', 'localhost:3306'],
        ['数据库名', 'manager'],
        ['用户名', 'root'],
        ['密码', '根据实际配置']
    ]
    create_table_with_header(doc, ['配置项', '值'], db_conn_data)
    doc.add_paragraph()

    add_heading_custom(doc, '8.3 后端启动', level=2)
    backend_start = [
        '使用IntelliJ IDEA打开springboot项目',
        '修改 src/main/resources/application.yml 中的数据库连接配置',
        '运行 SpringbootApplication.java 主类',
        '等待服务启动，默认端口为 9090',
        '验证：访问 http://localhost:9090 确认服务正常运行'
    ]
    for i, step in enumerate(backend_start, 1):
        add_number_paragraph(doc, step)

    add_heading_custom(doc, '8.4 前端启动', level=2)
    frontend_start = [
        '进入vue目录：cd vue',
        '安装项目依赖：npm install',
        '启动开发服务器：npm run serve',
        '等待编译完成，默认端口为 8080',
        '访问地址：http://localhost:8080'
    ]
    for i, step in enumerate(frontend_start, 1):
        add_number_paragraph(doc, step)

    add_heading_custom(doc, '8.5 服务端口说明', level=2)
    port_data = [
        ['后端服务', '9090', 'SpringBoot应用服务'],
        ['前端服务', '8080', 'Vue开发服务器'],
        ['数据库', '3306', 'MySQL数据库服务']
    ]
    create_table_with_header(doc, ['服务', '端口', '说明'], port_data)
    doc.add_paragraph()

    add_heading_custom(doc, '8.6 默认测试账号', level=2)
    account_data = [
        ['管理员', 'admin', '123', '拥有全部后台管理权限'],
        ['普通用户', 'test', '123', '拥有前台全部功能权限']
    ]
    create_table_with_header(doc, ['角色', '账号', '密码', '权限说明'], account_data)
    doc.add_paragraph()

    add_heading_custom(doc, '8.7 常见问题', level=2)
    add_bullet_paragraph(doc, '跨域问题：后端已配置CorsConfig，如仍有问题请检查前端代理配置')
    add_bullet_paragraph(doc, '数据库连接失败：请检查MySQL服务是否启动，以及application.yml中的连接信息是否正确')
    add_bullet_paragraph(doc, '端口占用：若9090或8080端口被占用，可在配置文件中修改端口号')
    add_bullet_paragraph(doc, '文件上传失败：请检查files目录是否存在且应用有写入权限')

    # ========== 保存文档 ==========
    output_path = '在线学习管理系统项目文档.docx'
    doc.save(output_path)
    print(f'文档生成成功：{output_path}')


if __name__ == '__main__':
    create_project_document()
