package com.example.service;

import com.example.entity.Course;
import com.example.mapper.ChapterMapper;
import com.example.mapper.CourseMapper;
import com.example.entity.Chapter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.*;

/**
 * 课程章节生成服务
 * 为没有章节的课程自动生成标准化的章节目录
 */
@Service
public class ChapterGenerateService {

    private static final Logger log = LoggerFactory.getLogger(ChapterGenerateService.class);

    @Resource
    private CourseMapper courseMapper;

    @Resource
    private ChapterMapper chapterMapper;

    // 课程方向关键词 -> 章节模板映射
    private static final Map<String, List<String[]>> CHAPTER_TEMPLATES = new LinkedHashMap<>();

    static {
        CHAPTER_TEMPLATES.put("Python", Arrays.asList(
                new String[]{"1-1 Python开发环境搭建", "900"},
                new String[]{"1-2 基础语法入门", "1200"},
                new String[]{"1-3 变量与数据类型", "1500"},
                new String[]{"1-4 条件语句与循环", "1200"},
                new String[]{"1-5 函数与模块", "1600"},
                new String[]{"2-1 面向对象编程", "2000"},
                new String[]{"2-2 文件操作与异常处理", "1400"},
                new String[]{"2-3 综合实战项目", "2400"}
        ));
        CHAPTER_TEMPLATES.put("Java", Arrays.asList(
                new String[]{"1-1 Java开发环境配置", "800"},
                new String[]{"1-2 基础语法", "1200"},
                new String[]{"1-3 面向对象基础", "1800"},
                new String[]{"1-4 面向对象进阶", "2000"},
                new String[]{"1-5 异常处理与常用类", "1400"},
                new String[]{"2-1 集合框架", "2200"},
                new String[]{"2-2 IO流与文件操作", "1600"},
                new String[]{"2-3 多线程编程", "2000"},
                new String[]{"2-4 网络编程基础", "1800"}
        ));
        CHAPTER_TEMPLATES.put("Vue", Arrays.asList(
                new String[]{"1-1 Vue简介与环境搭建", "600"},
                new String[]{"1-2 模板语法与数据绑定", "1200"},
                new String[]{"1-3 计算属性与侦听器", "1000"},
                new String[]{"1-4 条件渲染与列表渲染", "1200"},
                new String[]{"1-5 事件处理与表单绑定", "1400"},
                new String[]{"2-1 组件基础", "1600"},
                new String[]{"2-2 组件通信", "1800"},
                new String[]{"2-3 Vue Router路由", "1500"},
                new String[]{"2-4 Vuex状态管理", "1800"},
                new String[]{"2-5 项目实战", "2400"}
        ));
        CHAPTER_TEMPLATES.put("前端", Arrays.asList(
                new String[]{"1-1 HTML基础", "900"},
                new String[]{"1-2 CSS样式入门", "1200"},
                new String[]{"1-3 CSS布局与动画", "1500"},
                new String[]{"1-4 JavaScript基础", "1800"},
                new String[]{"1-5 DOM操作与事件", "1400"},
                new String[]{"2-1 ES6+新特性", "1600"},
                new String[]{"2-2 异步编程", "1200"},
                new String[]{"2-3 前端工程化", "1500"}
        ));
        CHAPTER_TEMPLATES.put("数据库", Arrays.asList(
                new String[]{"1-1 数据库基础概念", "800"},
                new String[]{"1-2 MySQL安装与配置", "600"},
                new String[]{"1-3 SQL基础查询", "1500"},
                new String[]{"1-4 多表连接查询", "1800"},
                new String[]{"1-5 索引与性能优化", "2000"},
                new String[]{"2-1 存储过程与函数", "1600"},
                new String[]{"2-2 事务与锁机制", "1400"},
                new String[]{"2-3 数据库设计实战", "2200"}
        ));
        CHAPTER_TEMPLATES.put("Web", Arrays.asList(
                new String[]{"1-1 Web开发概述", "600"},
                new String[]{"1-2 HTTP协议基础", "1000"},
                new String[]{"1-3 前端基础回顾", "1200"},
                new String[]{"1-4 后端技术选型", "800"},
                new String[]{"2-1 MVC架构设计", "1500"},
                new String[]{"2-2 RESTful API开发", "1800"},
                new String[]{"2-3 前后端联调", "1600"},
                new String[]{"2-4 部署与运维", "1200"}
        ));
        CHAPTER_TEMPLATES.put("Linux", Arrays.asList(
                new String[]{"1-1 Linux系统安装", "800"},
                new String[]{"1-2 文件系统与目录操作", "1200"},
                new String[]{"1-3 用户与权限管理", "1000"},
                new String[]{"1-4 进程与服务管理", "1400"},
                new String[]{"2-1 Shell脚本编程", "2000"},
                new String[]{"2-2 网络配置与防火墙", "1200"},
                new String[]{"2-3 服务器部署实战", "1800"}
        ));
        CHAPTER_TEMPLATES.put("爬虫", Arrays.asList(
                new String[]{"1-1 爬虫原理与法律须知", "600"},
                new String[]{"1-2 HTTP请求与响应", "1000"},
                new String[]{"1-3 HTML解析与数据提取", "1500"},
                new String[]{"1-4 数据存储", "1200"},
                new String[]{"2-1 动态网页爬取", "1800"},
                new String[]{"2-2 反爬虫策略与应对", "1600"},
                new String[]{"2-3 分布式爬虫实战", "2200"}
        ));
        CHAPTER_TEMPLATES.put("架构", Arrays.asList(
                new String[]{"1-1 架构设计原则", "900"},
                new String[]{"1-2 单体与微服务", "1200"},
                new String[]{"1-3 分布式系统基础", "1500"},
                new String[]{"1-4 高可用设计", "1800"},
                new String[]{"2-1 消息队列", "1600"},
                new String[]{"2-2 缓存架构", "1400"},
                new String[]{"2-3 数据库分库分表", "2000"}
        ));
        CHAPTER_TEMPLATES.put("算法", Arrays.asList(
                new String[]{"1-1 算法复杂度分析", "800"},
                new String[]{"1-2 数组与链表", "1200"},
                new String[]{"1-3 栈与队列", "1000"},
                new String[]{"1-4 树与二叉树", "1500"},
                new String[]{"1-5 图的基础", "1800"},
                new String[]{"2-1 排序算法", "1600"},
                new String[]{"2-2 搜索与回溯", "1400"},
                new String[]{"2-3 动态规划", "2000"}
        ));
        CHAPTER_TEMPLATES.put("测试", Arrays.asList(
                new String[]{"1-1 软件测试基础", "800"},
                new String[]{"1-2 测试用例设计", "1200"},
                new String[]{"1-3 功能测试实战", "1500"},
                new String[]{"1-4 接口测试", "1400"},
                new String[]{"2-1 UI自动化测试", "1800"},
                new String[]{"2-2 性能测试入门", "1600"},
                new String[]{"2-3 持续集成与DevOps", "1200"}
        ));
        CHAPTER_TEMPLATES.put("AI", Arrays.asList(
                new String[]{"1-1 人工智能概述", "800"},
                new String[]{"1-2 机器学习基础", "1500"},
                new String[]{"1-3 数学基础回顾", "1200"},
                new String[]{"1-4 特征工程", "1400"},
                new String[]{"2-1 监督学习算法", "2000"},
                new String[]{"2-2 无监督学习算法", "1600"},
                new String[]{"2-3 深度学习入门", "2200"},
                new String[]{"2-4 模型评估与调优", "1800"}
        ));
        // 默认模板
        CHAPTER_TEMPLATES.put("default", Arrays.asList(
                new String[]{"1-1 课程导学", "500"},
                new String[]{"1-2 基础入门", "1200"},
                new String[]{"1-3 核心概念", "1500"},
                new String[]{"1-4 进阶内容", "1800"},
                new String[]{"2-1 实战演练", "2000"},
                new String[]{"2-2 综合应用", "1600"},
                new String[]{"2-3 课程总结", "800"}
        ));
    }

    /**
     * 为所有没有章节的课程批量生成章节目录
     */
    public int generateChaptersForAllCourses() {
        List<Course> courses = courseMapper.selectAll(new Course());
        int generated = 0;

        for (Course course : courses) {
            // 检查是否已有章节
            Chapter query = new Chapter();
            query.setCourseId(course.getId());
            List<Chapter> existing = chapterMapper.selectAll(query);
            if (!existing.isEmpty()) continue;

            // 根据课程名匹配模板
            List<String[]> template = matchTemplate(course.getName());
            int sortOrder = 1;
            for (String[] item : template) {
                Chapter chapter = new Chapter();
                chapter.setCourseId(course.getId());
                chapter.setTitle(item[0]);
                chapter.setSortOrder(sortOrder++);
                chapter.setType("VIDEO");
                chapter.setDuration(Integer.parseInt(item[1]));
                // 第1、2节免费试看
                chapter.setFreePreview(sortOrder <= 3 ? 1 : 0);
                chapterMapper.insert(chapter);
            }
            generated++;
            log.info("为课程生成章节: id={}, name={}, 章节数={}", course.getId(), course.getName(), template.size());
        }

        return generated;
    }

    private List<String[]> matchTemplate(String courseName) {
        String name = courseName.toLowerCase();
        for (Map.Entry<String, List<String[]>> entry : CHAPTER_TEMPLATES.entrySet()) {
            if (entry.getKey().equals("default")) continue;
            if (name.contains(entry.getKey().toLowerCase())) {
                return entry.getValue();
            }
        }
        // 关键词别名
        if (name.contains("javascript") || name.contains("js")) return CHAPTER_TEMPLATES.get("前端");
        if (name.contains("mysql")) return CHAPTER_TEMPLATES.get("数据库");
        if (name.contains("spring") || name.contains("springboot")) return CHAPTER_TEMPLATES.get("Java");
        if (name.contains("深度学习") || name.contains("机器学习") || name.contains("pytorch") || name.contains("人工智能"))
            return CHAPTER_TEMPLATES.get("AI");
        if (name.contains("软件测试")) return CHAPTER_TEMPLATES.get("测试");
        return CHAPTER_TEMPLATES.get("default");
    }
}
