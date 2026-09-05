package com.example.service;

import com.example.entity.Course;
import com.example.entity.Orders;
import com.example.entity.User;
import com.example.mapper.CourseMapper;
import com.example.mapper.OrdersMapper;
import com.example.mapper.UserMapper;
import com.example.utils.DateUtils;
import com.example.utils.TokenUtils;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 增强推荐服务
 * 提供多种推荐算法：冷启动推荐、混合推荐、学习路径推荐等
 */
@Service
public class EnhancedRecommendService {

    @Resource
    private CourseMapper courseMapper;

    @Resource
    private OrdersMapper ordersMapper;

    @Resource
    private UserMapper userMapper;

    @Resource
    private CollaborativeFilterService collaborativeFilterService;

    // 课程难度等级定义
    private static final Map<String, Integer> COURSE_DIFFICULTY = new HashMap<String, Integer>() {{
        put("入门", 1);
        put("基础", 1);
        put("初级", 1);
        put("进阶", 2);
        put("中级", 2);
        put("高级", 3);
        put("实战", 3);
        put("精通", 4);
        put("架构", 4);
    }};

    // 课程依赖关系（学习路径）
    private static final Map<String, List<String>> COURSE_DEPENDENCIES = new HashMap<String, List<String>>() {{
        put("SpringBoot框架", Arrays.asList("Java基础入门", "Java Web开发"));
        put("微服务架构", Arrays.asList("SpringBoot框架", "Docker基础"));
        put("Vue.js实战", Arrays.asList("JavaScript基础", "HTML/CSS基础"));
        put("React框架", Arrays.asList("JavaScript基础", "ES6新特性"));
        put("深度学习基础", Arrays.asList("Python入门", "数据分析"));
        put("Kubernetes入门", Arrays.asList("Docker基础", "Linux基础"));
    }};

    // ==================== 冷启动推荐 ====================

    /**
     * 冷启动推荐 - 针对新用户
     * 当用户无历史行为数据时，基于以下策略推荐：
     * 1. 热门课程（基于购买量）
     * 2. 高评分课程
     * 3. 最新课程
     * 
     * @param limit 推荐数量
     * @return 推荐课程列表
     */
    public List<Course> coldStartRecommend(int limit) {
        List<Course> result = new ArrayList<>();
        
        // 1. 获取所有课程
        List<Course> allCourses = courseMapper.selectAll(new Course());
        
        // 2. 获取所有订单，计算热度
        List<Orders> allOrders = ordersMapper.selectAll(new Orders());
        Map<Integer, Integer> courseOrderCount = new HashMap<>();
        for (Orders order : allOrders) {
            if (order.getCourseId() != null) {
                courseOrderCount.merge(order.getCourseId(), 1, Integer::sum);
            }
        }
        
        // 3. 计算综合分数并排序
        // 分数 = 热度分(40%) + 推荐分(30%) + 时间分(30%)
        LocalDateTime now = LocalDateTime.now();
        
        List<Map<String, Object>> scoredCourses = new ArrayList<>();
        for (Course course : allCourses) {
            double score = 0;
            
            // 热度分：购买数量归一化
            int orderCount = courseOrderCount.getOrDefault(course.getId(), 0);
            double hotScore = Math.min(orderCount / 10.0, 1.0) * 40;
            score += hotScore;
            
            // 推荐分
            if ("是".equals(course.getRecommend())) {
                score += 30;
            }
            
            // 时间分：越新分数越高
            LocalDateTime createTime = parseDateTime(course.getTime());
            if (createTime != null) {
                long daysAgo = ChronoUnit.DAYS.between(createTime, now);
                double timeScore = Math.max(0, 30 - daysAgo * 0.1);
                score += timeScore;
            }
            
            // 免费课程加分
            if (course.getPrice() != null && course.getPrice() == 0) {
                score += 10;
            }
            
            Map<String, Object> item = new HashMap<>();
            item.put("course", course);
            item.put("score", score);
            scoredCourses.add(item);
        }
        
        // 4. 按分数排序
        scoredCourses.sort((a, b) -> Double.compare((Double) b.get("score"), (Double) a.get("score")));
        
        // 5. 返回Top N
        for (int i = 0; i < Math.min(limit, scoredCourses.size()); i++) {
            result.add((Course) scoredCourses.get(i).get("course"));
        }
        
        return result;
    }

    // ==================== 基于内容的推荐 ====================

    /**
     * 基于内容的推荐
     * 根据课程类型、标签匹配用户偏好
     * 
     * @param userId 用户ID
     * @param limit 推荐数量
     * @return 推荐课程列表
     */
    public List<Course> contentBasedRecommend(Integer userId, int limit) {
        List<Course> result = new ArrayList<>();
        
        // 1. 获取用户历史购买的课程类型偏好
        Orders query = new Orders();
        query.setUserId(userId);
        List<Orders> userOrders = ordersMapper.selectAll(query);
        
        // 统计用户偏好的课程类型
        Map<String, Integer> typePreference = new HashMap<>();
        Set<Integer> purchasedCourseIds = new HashSet<>();
        
        // 批量收集课程ID
        for (Orders order : userOrders) {
            if (order.getCourseId() != null) {
                purchasedCourseIds.add(order.getCourseId());
            }
        }
        // 批量查询课程详情（修复 N+1 查询）
        if (!purchasedCourseIds.isEmpty()) {
            List<Course> purchasedCourses = courseMapper.selectByIds(purchasedCourseIds);
            for (Course course : purchasedCourses) {
                if (course.getType() != null) {
                    typePreference.merge(course.getType(), 1, Integer::sum);
                }
            }
        }
        
        // 2. 如果用户无偏好，返回热门课程
        if (typePreference.isEmpty()) {
            return coldStartRecommend(limit);
        }
        
        // 3. 找出最偏好的类型
        String preferredType = typePreference.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse("VIDEO");
        
        // 4. 获取该类型的课程，排除已购买的
        List<Course> allCourses = courseMapper.selectAll(new Course());
        
        result = allCourses.stream()
                .filter(c -> preferredType.equals(c.getType()))
                .filter(c -> !purchasedCourseIds.contains(c.getId()))
                .limit(limit)
                .collect(Collectors.toList());
        
        // 5. 如果数量不足，补充其他类型的热门课程
        if (result.size() < limit) {
            List<Course> hotCourses = coldStartRecommend(limit - result.size());
            for (Course course : hotCourses) {
                if (!purchasedCourseIds.contains(course.getId()) 
                        && result.stream().noneMatch(c -> c.getId().equals(course.getId()))) {
                    result.add(course);
                }
            }
        }
        
        return result;
    }

    // ==================== 混合推荐 ====================

    /**
     * 混合推荐算法
     * 融合协同过滤和基于内容的推荐
     * 
     * @param userId 用户ID
     * @param limit 推荐数量
     * @return 推荐课程列表
     */
    public List<Course> hybridRecommend(Integer userId, int limit) {
        List<Course> result = new ArrayList<>();
        Set<Integer> recommendedIds = new LinkedHashSet<>();
        
        // 1. 获取协同过滤推荐结果（权重60%）
        List<Course> cfCourses = collaborativeFilterService.recommendCourses(userId, limit);
        
        // 2. 获取基于内容的推荐结果（权重40%）
        List<Course> cbCourses = contentBasedRecommend(userId, limit);
        
        // 3. 加权融合：为每个课程综合评分，然后排序
        Map<Integer, Double> courseScoreMap = new LinkedHashMap<>();
        Map<Integer, Course> courseMap = new HashMap<>();
        
        // 协同过滤结果赋分（倒序排名分，权重0.6）
        for (int i = 0; i < cfCourses.size(); i++) {
            Course c = cfCourses.get(i);
            double score = (cfCourses.size() - i) * 0.6;
            courseScoreMap.merge(c.getId(), score, Double::sum);
            courseMap.putIfAbsent(c.getId(), c);
        }
        
        // 基于内容结果赋分（倒序排名分，权重0.4）
        for (int i = 0; i < cbCourses.size(); i++) {
            Course c = cbCourses.get(i);
            double score = (cbCourses.size() - i) * 0.4;
            courseScoreMap.merge(c.getId(), score, Double::sum);
            courseMap.putIfAbsent(c.getId(), c);
        }
        
        // 按综合分排序
        List<Integer> sortedIds = courseScoreMap.entrySet().stream()
                .sorted(Map.Entry.<Integer, Double>comparingByValue().reversed())
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());
        
        for (Integer id : sortedIds) {
            if (result.size() >= limit) break;
            Course c = courseMap.get(id);
            if (c != null && !recommendedIds.contains(c.getId())) {
                result.add(c);
                recommendedIds.add(c.getId());
            }
        }
        
        // 4. 如果结果不足，补充热门课程
        if (result.size() < limit) {
            List<Course> hotCourses = coldStartRecommend(limit - result.size());
            for (Course course : hotCourses) {
                if (!recommendedIds.contains(course.getId())) {
                    result.add(course);
                    recommendedIds.add(course.getId());
                }
            }
        }
        
        return result;
    }

    // ==================== 学习路径推荐 ====================

    /**
     * 学习路径推荐
     * 基于课程难度和依赖关系，推荐适合的学习路径
     * 
     * @param userId 用户ID
     * @return 学习路径数据
     */
    public Map<String, Object> learningPathRecommend(Integer userId) {
        Map<String, Object> result = new HashMap<>();
        
        // 1. 获取用户已学课程
        Orders query = new Orders();
        query.setUserId(userId);
        List<Orders> userOrders = ordersMapper.selectAll(query);
        
        Set<String> learnedCourses = new HashSet<>();
        Set<Integer> purchasedCourseIds = new HashSet<>();
        
        for (Orders order : userOrders) {
            if (order.getCourseId() != null) {
                purchasedCourseIds.add(order.getCourseId());
            }
        }
        // 批量查询课程详情（修复 N+1 查询）
        if (!purchasedCourseIds.isEmpty()) {
            List<Course> purchasedCourses = courseMapper.selectByIds(purchasedCourseIds);
            for (Course course : purchasedCourses) {
                learnedCourses.add(course.getName());
            }
        }
        
        // 2. 计算用户当前学习阶段
        int currentLevel = calculateUserLevel(learnedCourses);
        
        // 3. 推荐下一阶段课程
        List<Course> nextLevelCourses = new ArrayList<>();
        List<Course> allCourses = courseMapper.selectAll(new Course());
        
        for (Course course : allCourses) {
            if (purchasedCourseIds.contains(course.getId())) {
                continue;
            }
            
            // 检查课程难度是否适合
            int courseLevel = estimateCourseLevel(course.getName());
            if (courseLevel == currentLevel || courseLevel == currentLevel + 1) {
                // 检查依赖是否满足
                if (checkDependencies(course.getName(), learnedCourses)) {
                    nextLevelCourses.add(course);
                }
            }
        }
        
        // 4. 生成学习路径
        List<Map<String, Object>> learningPath = generateLearningPath(currentLevel, nextLevelCourses);
        
        result.put("currentLevel", currentLevel);
        result.put("levelName", getLevelName(currentLevel));
        result.put("learningPath", learningPath);
        result.put("recommendedCourses", nextLevelCourses.stream().limit(5).collect(Collectors.toList()));
        result.put("completedCourses", learnedCourses.size());
        
        return result;
    }

    /**
     * 计算用户学习等级
     */
    private int calculateUserLevel(Set<String> learnedCourses) {
        int level = 1;
        
        for (String courseName : learnedCourses) {
            int courseLevel = estimateCourseLevel(courseName);
            level = Math.max(level, courseLevel);
        }
        
        return level;
    }

    /**
     * 估算课程难度等级
     */
    private int estimateCourseLevel(String courseName) {
        if (courseName == null) return 1;
        
        for (Map.Entry<String, Integer> entry : COURSE_DIFFICULTY.entrySet()) {
            if (courseName.contains(entry.getKey())) {
                return entry.getValue();
            }
        }
        
        return 2; // 默认中级
    }

    /**
     * 检查课程依赖是否满足
     */
    private boolean checkDependencies(String courseName, Set<String> learnedCourses) {
        List<String> dependencies = COURSE_DEPENDENCIES.get(courseName);
        if (dependencies == null || dependencies.isEmpty()) {
            return true;
        }
        
        // 至少满足一个前置课程
        for (String dep : dependencies) {
            if (learnedCourses.stream().anyMatch(c -> c.contains(dep))) {
                return true;
            }
        }
        
        return false;
    }

    /**
     * 生成学习路径
     */
    private List<Map<String, Object>> generateLearningPath(int currentLevel, List<Course> nextCourses) {
        List<Map<String, Object>> path = new ArrayList<>();
        
        String[] levelNames = {"入门阶段", "基础阶段", "进阶阶段", "高级阶段"};
        
        for (int i = 1; i <= 4; i++) {
            final int level = i;  // 必须是final才能用于lambda
            Map<String, Object> stage = new HashMap<>();
            stage.put("level", i);
            stage.put("name", levelNames[i - 1]);
            stage.put("status", i < currentLevel ? "已完成" : 
                              i == currentLevel ? "进行中" : "未开始");
            
            // 该阶段推荐课程
            List<Course> stageCourses = nextCourses.stream()
                    .filter(c -> estimateCourseLevel(c.getName()) == level)
                    .limit(3)
                    .collect(Collectors.toList());
            stage.put("courses", stageCourses);
            
            path.add(stage);
        }
        
        return path;
    }

    /**
     * 获取等级名称
     */
    private String getLevelName(int level) {
        String[] names = {"入门", "基础", "进阶", "高级"};
        return names[Math.min(level - 1, 3)];
    }

    // ==================== 时间衰减热门推荐 ====================

    /**
     * 时间衰减热门推荐
     * 近期购买的课程权重更高
     * 
     * @param limit 返回数量
     * @return 热门课程列表
     */
    public List<Course> timeDecayHotRecommend(int limit) {
        List<Course> result = new ArrayList<>();
        
        // 1. 获取所有订单
        List<Orders> allOrders = ordersMapper.selectAll(new Orders());
        
        // 2. 计算每个课程的时间衰减热度
        Map<Integer, Double> courseHotScore = new HashMap<>();
        LocalDateTime now = LocalDateTime.now();
        
        for (Orders order : allOrders) {
            if (order.getCourseId() == null) continue;
            
            LocalDateTime orderTime = parseDateTime(order.getTime());
            double score = 1.0;
            
            if (orderTime != null) {
                long daysAgo = ChronoUnit.DAYS.between(orderTime, now);
                // 时间衰减公式：score = e^(-daysAgo / 30)
                score = Math.exp(-daysAgo / 30.0);
            }
            
            courseHotScore.merge(order.getCourseId(), score, Double::sum);
        }
        
        // 3. 按热度排序
        List<Integer> sortedCourseIds = courseHotScore.entrySet().stream()
                .sorted(Map.Entry.<Integer, Double>comparingByValue().reversed())
                .limit(limit)
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());
        
        // 4. 批量查询课程详情（修复 N+1 查询）
        if (!sortedCourseIds.isEmpty()) {
            Set<Integer> idSet = new LinkedHashSet<>(sortedCourseIds);
            List<Course> courses = courseMapper.selectByIds(idSet);
            Map<Integer, Course> courseDetailMap = courses.stream()
                    .collect(Collectors.toMap(Course::getId, c -> c, (a, b) -> a));
            for (Integer courseId : sortedCourseIds) {
                Course course = courseDetailMap.get(courseId);
                if (course != null) {
                    result.add(course);
                }
            }
        }
        
        return result;
    }

    // ==================== 个性化推荐入口 ====================

    /**
     * 智能推荐入口
     * 根据用户状态自动选择最合适的推荐策略
     * 
     * @param limit 推荐数量
     * @return 推荐结果（包含推荐课程和推荐原因）
     */
    public Map<String, Object> smartRecommend(int limit) {
        Map<String, Object> result = new HashMap<>();
        
        try {
            // 获取当前用户
            User currentUser = (User) TokenUtils.getCurrentUser();
            
            if (currentUser == null || currentUser.getId() == null) {
                // 未登录：冷启动推荐
                result.put("courses", coldStartRecommend(limit));
                result.put("reason", "热门课程推荐");
                result.put("strategy", "COLD_START");
            } else {
                // 检查用户是否有历史行为
                Orders query = new Orders();
                query.setUserId(currentUser.getId());
                List<Orders> userOrders = ordersMapper.selectAll(query);
                
                if (userOrders.isEmpty()) {
                    // 新用户：冷启动推荐
                    result.put("courses", coldStartRecommend(limit));
                    result.put("reason", "为您精选热门课程");
                    result.put("strategy", "COLD_START");
                } else if (userOrders.size() < 3) {
                    // 少量行为：基于内容推荐
                    result.put("courses", contentBasedRecommend(currentUser.getId(), limit));
                    result.put("reason", "根据您的偏好推荐");
                    result.put("strategy", "CONTENT_BASED");
                } else {
                    // 有足够行为：混合推荐
                    result.put("courses", hybridRecommend(currentUser.getId(), limit));
                    result.put("reason", "为您个性化推荐");
                    result.put("strategy", "HYBRID");
                }
                
                result.put("userId", currentUser.getId());
            }
        } catch (Exception e) {
            // 异常情况：返回热门课程
            result.put("courses", coldStartRecommend(limit));
            result.put("reason", "热门课程推荐");
            result.put("strategy", "FALLBACK");
        }
        
        return result;
    }

    // ==================== 工具方法 ====================

    /**
     * 解析日期时间字符串（委托给公共工具类）
     */
    private LocalDateTime parseDateTime(String timeStr) {
        return DateUtils.parseDateTime(timeStr);
    }
}
