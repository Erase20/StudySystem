package com.example.service;

import com.example.entity.Course;
import com.example.entity.Orders;
import com.example.entity.Signin;
import com.example.entity.User;
import com.example.mapper.CourseMapper;
import com.example.mapper.OrdersMapper;
import com.example.mapper.SigninMapper;
import com.example.mapper.UserMapper;
import com.example.utils.DateUtils;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 数据分析服务
 * 提供用户画像、RFM分层、学习进度分析等数据分析功能
 */
@Service
public class DataAnalysisService {

    @Resource
    private UserMapper userMapper;

    @Resource
    private OrdersMapper ordersMapper;

    @Resource
    private CourseMapper courseMapper;

    @Resource
    private SigninMapper signinMapper;

    // ==================== 用户画像分析 ====================

    /**
     * 生成用户画像标签
     * 根据用户的购买行为、学习偏好生成标签
     * 
     * @param userId 用户ID
     * @return 用户画像数据（包含标签列表、偏好类型、活跃度等）
     */
    public Map<String, Object> generateUserProfile(Integer userId) {
        Map<String, Object> profile = new HashMap<>();
        
        // 1. 获取用户基本信息
        User user = userMapper.selectById(userId);
        if (user == null) {
            return profile;
        }
        
        // 2. 获取用户订单数据
        Orders query = new Orders();
        query.setUserId(userId);
        List<Orders> userOrders = ordersMapper.selectAll(query);
        
        // 3. 分析用户偏好类型（批量查询课程，修复 N+1）
        Map<String, Integer> typeCount = new HashMap<>();
        Set<Integer> courseIds = new HashSet<>();
        for (Orders order : userOrders) {
            if (order.getCourseId() != null) {
                courseIds.add(order.getCourseId());
            }
        }
        if (!courseIds.isEmpty()) {
            List<Course> courses = courseMapper.selectByIds(courseIds);
            for (Course course : courses) {
                if (course.getType() != null) {
                    typeCount.merge(course.getType(), 1, Integer::sum);
                }
            }
        }
        
        // 找出最偏好的课程类型
        String preferredType = typeCount.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse("未确定");
        
        // 4. 生成用户标签
        List<String> tags = new ArrayList<>();
        
        // 根据购买数量判断
        int orderCount = userOrders.size();
        if (orderCount >= 10) {
            tags.add("学习达人");
        } else if (orderCount >= 5) {
            tags.add("积极学习者");
        } else if (orderCount >= 1) {
            tags.add("初学者");
        }
        
        // 根据会员状态
        if ("是".equals(user.getMember())) {
            tags.add("VIP会员");
        }
        
        // 根据积分
        if (user.getScore() != null && user.getScore() >= 500) {
            tags.add("积分达人");
        }
        
        // 根据偏好类型
        if ("VIDEO".equals(preferredType)) {
            tags.add("视频学习者");
        } else if ("TEXT".equals(preferredType)) {
            tags.add("阅读爱好者");
        }
        
        // 5. 计算活跃度（0-100分）
        int activityScore = calculateActivityScore(userId, userOrders);
        
        // 6. 组装结果
        profile.put("userId", userId);
        profile.put("name", user.getName());
        profile.put("avatar", user.getAvatar());
        profile.put("tags", tags);
        profile.put("preferredType", preferredType);
        profile.put("activityScore", activityScore);
        profile.put("orderCount", orderCount);
        profile.put("totalSpent", userOrders.stream()
                .mapToDouble(o -> o.getPrice() != null ? o.getPrice() : 0)
                .sum());
        
        return profile;
    }

    /**
     * 计算用户活跃度分数
     * 基于登录频率、购买频率、学习时长等维度
     * 
     * @param userId 用户ID
     * @param orders 用户订单列表
     * @return 活跃度分数（0-100）
     */
    private int calculateActivityScore(Integer userId, List<Orders> orders) {
        int score = 0;
        
        // 1. 购买频率贡献（最高40分）
        int orderCount = orders.size();
        score += Math.min(orderCount * 4, 40);
        
        // 2. 最近活跃度贡献（最高30分）
        if (!orders.isEmpty()) {
            // 找最近一次购买
            Optional<LocalDateTime> lastOrderTime = orders.stream()
                    .filter(o -> o.getTime() != null)
                    .map(o -> DateUtils.parseDateTime(o.getTime()))
                    .filter(Objects::nonNull)
                    .max(LocalDateTime::compareTo);
            
            if (lastOrderTime.isPresent()) {
                long daysSinceLastOrder = ChronoUnit.DAYS.between(
                        lastOrderTime.get(), LocalDateTime.now());
                if (daysSinceLastOrder <= 7) {
                    score += 30;
                } else if (daysSinceLastOrder <= 30) {
                    score += 20;
                } else if (daysSinceLastOrder <= 90) {
                    score += 10;
                }
            }
        }
        
        // 3. 积分贡献（最高30分）
        User user = userMapper.selectById(userId);
        if (user != null && user.getScore() != null) {
            score += Math.min(user.getScore() / 50, 30);
        }
        
        return Math.min(score, 100);
    }

    // ==================== RFM用户分层 ====================

    /**
     * RFM用户分层分析
     * R(Recency): 最近一次购买时间
     * F(Frequency): 购买频率
     * M(Monetary): 消费金额
     * 
     * @return 各层级用户统计及用户列表
     */
    public Map<String, Object> rfmAnalysis() {
        Map<String, Object> result = new HashMap<>();
        
        // 1. 获取所有用户
        List<User> allUsers = userMapper.selectAll(new User());
        
        // 2. 获取所有订单
        List<Orders> allOrders = ordersMapper.selectAll(new Orders());
        
        // 3. 按用户分组订单
        Map<Integer, List<Orders>> userOrdersMap = allOrders.stream()
                .filter(o -> o.getUserId() != null)
                .collect(Collectors.groupingBy(Orders::getUserId));
        
        // 4. 计算每个用户的RFM值
        List<Map<String, Object>> userRfmList = new ArrayList<>();
        LocalDateTime now = LocalDateTime.now();
        
        for (User user : allUsers) {
            List<Orders> userOrders = userOrdersMap.getOrDefault(user.getId(), new ArrayList<>());
            
            // R: 最近一次购买距今天数
            int rValue = 999; // 默认很大表示从未购买
            if (!userOrders.isEmpty()) {
                Optional<LocalDateTime> lastOrder = userOrders.stream()
                        .filter(o -> o.getTime() != null)
                        .map(o -> DateUtils.parseDateTime(o.getTime()))
                        .filter(Objects::nonNull)
                        .max(LocalDateTime::compareTo);
                if (lastOrder.isPresent()) {
                    rValue = (int) ChronoUnit.DAYS.between(lastOrder.get(), now);
                }
            }
            
            // F: 购买次数
            int fValue = userOrders.size();
            
            // M: 消费总金额
            double mValue = userOrders.stream()
                    .mapToDouble(o -> o.getPrice() != null ? o.getPrice() : 0)
                    .sum();
            
            // 计算RFM得分（每项1-5分）
            int rScore = rValue <= 30 ? 5 : rValue <= 90 ? 4 : rValue <= 180 ? 3 : rValue <= 365 ? 2 : 1;
            int fScore = fValue >= 10 ? 5 : fValue >= 5 ? 4 : fValue >= 3 ? 3 : fValue >= 1 ? 2 : 1;
            int mScore = mValue >= 1000 ? 5 : mValue >= 500 ? 4 : mValue >= 200 ? 3 : mValue >= 50 ? 2 : 1;
            
            // 确定用户层级
            String segment = determineRfmSegment(rScore, fScore, mScore);
            
            Map<String, Object> userRfm = new HashMap<>();
            userRfm.put("userId", user.getId());
            userRfm.put("name", user.getName());
            userRfm.put("avatar", user.getAvatar());
            userRfm.put("rScore", rScore);
            userRfm.put("fScore", fScore);
            userRfm.put("mScore", mScore);
            userRfm.put("totalScore", rScore + fScore + mScore);
            userRfm.put("segment", segment);
            userRfm.put("rValue", rValue);
            userRfm.put("fValue", fValue);
            userRfm.put("mValue", mValue);
            
            userRfmList.add(userRfm);
        }
        
        // 5. 统计各层级用户数量
        Map<String, Long> segmentCount = userRfmList.stream()
                .collect(Collectors.groupingBy(u -> (String) u.get("segment"), Collectors.counting()));
        
        // 6. 按总分排序
        userRfmList.sort((a, b) -> (int) b.get("totalScore") - (int) a.get("totalScore"));
        
        result.put("segmentCount", segmentCount);
        result.put("userList", userRfmList);
        result.put("totalUsers", allUsers.size());
        
        return result;
    }

    /**
     * 根据RFM得分确定用户层级
     * 
     * @param rScore 最近购买得分
     * @param fScore 购买频率得分
     * @param mScore 消费金额得分
     * @return 用户层级标签
     */
    private String determineRfmSegment(int rScore, int fScore, int mScore) {
        int total = rScore + fScore + mScore;
        
        // 重要价值客户：三项都高
        if (rScore >= 4 && fScore >= 4 && mScore >= 4) {
            return "重要价值客户";
        }
        // 重要发展客户：近期有购买，但频率或金额不高
        if (rScore >= 4 && (fScore < 4 || mScore < 4)) {
            return "重要发展客户";
        }
        // 重要保持客户：频率和金额高，但近期未购买
        if (rScore < 4 && fScore >= 4 && mScore >= 4) {
            return "重要保持客户";
        }
        // 一般客户：中等水平
        if (total >= 9) {
            return "一般客户";
        }
        // 潜在客户：有购买但活跃度低
        if (fScore >= 2) {
            return "潜在客户";
        }
        // 流失客户：长期未购买
        return "流失风险客户";
    }

    // ==================== 学习进度分析 ====================

    /**
     * 预测用户学习进度
     * 基于历史学习行为预测课程完成率
     * 
     * @param userId 用户ID
     * @return 学习进度分析数据
     */
    public Map<String, Object> predictLearningProgress(Integer userId) {
        Map<String, Object> result = new HashMap<>();
        
        // 1. 获取用户订单
        Orders query = new Orders();
        query.setUserId(userId);
        List<Orders> userOrders = ordersMapper.selectAll(query);
        
        // 2. 获取用户信息
        User user = userMapper.selectById(userId);
        
        // 3. 计算学习进度指标
        int totalCourses = userOrders.size();
        
        // 基于订单时间计算真实学习进度（而非硬编码比例）
        // 已完成 = 购买超过60天的课程，学习中 = 购买不超过60天的课程
        LocalDateTime now = LocalDateTime.now();
        int completedCourses = 0;
        int inProgressCourses = 0;
        for (Orders order : userOrders) {
            LocalDateTime orderTime = DateUtils.parseDateTime(order.getTime());
            if (orderTime != null) {
                long daysSince = ChronoUnit.DAYS.between(orderTime, now);
                if (daysSince > 60) {
                    completedCourses++;
                } else {
                    inProgressCourses++;
                }
            } else {
                inProgressCourses++;
            }
        }
        
        // 4. 预测完成率（基于活跃度和历史表现）
        double predictedCompletionRate = 0.0;
        if (user != null) {
            // 基础完成率
            predictedCompletionRate = 0.6;
            
            // 会员加成
            if ("是".equals(user.getMember())) {
                predictedCompletionRate += 0.1;
            }
            
            // 积分加成
            if (user.getScore() != null && user.getScore() > 100) {
                predictedCompletionRate += Math.min(user.getScore() / 1000.0, 0.15);
            }
            
            // 购买数量加成
            if (totalCourses > 5) {
                predictedCompletionRate += 0.05;
            }
        }
        
        predictedCompletionRate = Math.min(predictedCompletionRate, 0.95);
        
        // 5. 预计完成时间（天）
        int estimatedDaysToComplete = (int) (inProgressCourses / Math.max(predictedCompletionRate, 0.1) * 7);
        
        // 6. 学习建议
        List<String> suggestions = generateLearningSuggestions(user, totalCourses, predictedCompletionRate);
        
        result.put("userId", userId);
        result.put("totalCourses", totalCourses);
        result.put("completedCourses", completedCourses);
        result.put("inProgressCourses", inProgressCourses);
        result.put("predictedCompletionRate", String.format("%.1f%%", predictedCompletionRate * 100));
        result.put("estimatedDaysToComplete", estimatedDaysToComplete);
        result.put("suggestions", suggestions);
        result.put("learningStreak", calculateLearningStreak(userId));
        
        return result;
    }

    /**
     * 生成学习建议
     */
    private List<String> generateLearningSuggestions(User user, int totalCourses, double completionRate) {
        List<String> suggestions = new ArrayList<>();
        
        if (completionRate < 0.5) {
            suggestions.add("建议制定每周学习计划，保持学习连贯性");
        }
        if (totalCourses < 3) {
            suggestions.add("可以尝试更多课程，拓宽知识面");
        }
        if (user != null && "否".equals(user.getMember())) {
            suggestions.add("成为会员可解锁更多优质课程");
        }
        if (user != null && (user.getScore() == null || user.getScore() < 100)) {
            suggestions.add("每日签到获取积分，兑换更多学习资源");
        }
        
        suggestions.add("坚持学习，每天进步一点点");
        
        return suggestions;
    }

    /**
     * 计算学习连续天数（基于签到记录）
     */
    private int calculateLearningStreak(Integer userId) {
        // 查询用户全部签到记录
        Signin query = new Signin();
        query.setUserId(userId);
        List<Signin> signinList = signinMapper.selectAll(query);
        
        if (signinList == null || signinList.isEmpty()) {
            return 0;
        }
        
        // 提取所有签到日期，按日期倒序排列
        Set<LocalDate> signinDays = new TreeSet<>(Comparator.reverseOrder());
        for (Signin signin : signinList) {
            if (signin.getDay() != null && !signin.getDay().isEmpty()) {
                try {
                    signinDays.add(LocalDate.parse(signin.getDay()));
                } catch (Exception ignored) {}
            }
        }
        
        if (signinDays.isEmpty()) {
            return 0;
        }
        
        // 从今天开始向前计算连续天数
        LocalDate today = LocalDate.now();
        int streak = 0;
        LocalDate checkDate = today;
        
        for (LocalDate day : signinDays) {
            if (day.equals(checkDate)) {
                streak++;
                checkDate = checkDate.minusDays(1);
            } else if (day.isBefore(checkDate)) {
                break;
            }
        }
        
        return streak;
    }

    // ==================== 课程热度分析 ====================

    /**
     * 课程热度分析
     * 综合购买量、时间衰减、评分等因素
     * 
     * @param limit 返回数量
     * @return 热门课程列表
     */
    public List<Map<String, Object>> analyzeCoursePopularity(int limit) {
        List<Map<String, Object>> result = new ArrayList<>();
        
        // 1. 获取所有订单
        List<Orders> allOrders = ordersMapper.selectAll(new Orders());
        
        // 2. 统计每个课程的购买数据
        Map<Integer, List<Orders>> courseOrdersMap = allOrders.stream()
                .filter(o -> o.getCourseId() != null)
                .collect(Collectors.groupingBy(Orders::getCourseId));
        
        // 3. 批量查询课程详情（修复 N+1 查询）
        Map<Integer, Course> courseMap = new HashMap<>();
        if (!courseOrdersMap.isEmpty()) {
            List<Course> courses = courseMapper.selectByIds(courseOrdersMap.keySet());
            for (Course c : courses) {
                courseMap.put(c.getId(), c);
            }
        }

        // 4. 计算热度分数
        LocalDateTime now = LocalDateTime.now();
        
        for (Map.Entry<Integer, List<Orders>> entry : courseOrdersMap.entrySet()) {
            Integer courseId = entry.getKey();
            List<Orders> orders = entry.getValue();
            
            Course course = courseMap.get(courseId);
            if (course == null) continue;
            
            // 基础热度 = 购买数量 * 10
            double hotScore = orders.size() * 10.0;
            
            // 时间衰减：近期购买权重更高
            for (Orders order : orders) {
            LocalDateTime orderTime = DateUtils.parseDateTime(order.getTime());
                if (orderTime != null) {
                    long daysAgo = ChronoUnit.DAYS.between(orderTime, now);
                    // 衰减系数：30天内不衰减，之后每天衰减1%
                    double decayFactor = daysAgo <= 30 ? 1.0 : Math.pow(0.99, daysAgo - 30);
                    hotScore += decayFactor * 5;
                }
            }
            
            // 推荐加成
            if ("是".equals(course.getRecommend())) {
                hotScore *= 1.2;
            }
            
            Map<String, Object> courseHot = new HashMap<>();
            courseHot.put("courseId", courseId);
            courseHot.put("name", course.getName());
            courseHot.put("img", course.getImg());
            courseHot.put("price", course.getPrice());
            courseHot.put("type", course.getType());
            courseHot.put("orderCount", orders.size());
            courseHot.put("hotScore", Math.round(hotScore * 100) / 100.0);
            
            result.add(courseHot);
        }
        
        // 4. 按热度排序
        result.sort((a, b) -> Double.compare((Double) b.get("hotScore"), (Double) a.get("hotScore")));
        
        // 5. 返回Top N
        return result.stream().limit(limit).collect(Collectors.toList());
    }

    // ==================== 平台整体数据分析 ====================

    /**
     * 获取平台整体数据统计
     * 
     * @return 平台统计数据
     */
    public Map<String, Object> getPlatformStatistics() {
        Map<String, Object> stats = new HashMap<>();
        
        // 1. 用户统计
        List<User> allUsers = userMapper.selectAll(new User());
        long totalUsers = allUsers.size();
        long memberUsers = allUsers.stream().filter(u -> "是".equals(u.getMember())).count();
        
        stats.put("totalUsers", totalUsers);
        stats.put("memberUsers", memberUsers);
        stats.put("memberRate", totalUsers > 0 ? 
                String.format("%.1f%%", memberUsers * 100.0 / totalUsers) : "0%");
        
        // 2. 课程统计
        List<Course> allCourses = courseMapper.selectAll(new Course());
        long totalCourses = allCourses.size();
        long videoCourses = allCourses.stream().filter(c -> "VIDEO".equals(c.getType())).count();
        long textCourses = allCourses.stream().filter(c -> "TEXT".equals(c.getType())).count();
        
        stats.put("totalCourses", totalCourses);
        stats.put("videoCourses", videoCourses);
        stats.put("textCourses", textCourses);
        
        // 3. 订单统计
        List<Orders> allOrders = ordersMapper.selectAll(new Orders());
        long totalOrders = allOrders.size();
        double totalRevenue = allOrders.stream()
                .mapToDouble(o -> o.getPrice() != null ? o.getPrice() : 0)
                .sum();
        
        stats.put("totalOrders", totalOrders);
        stats.put("totalRevenue", String.format("%.2f", totalRevenue));
        stats.put("avgOrderValue", totalOrders > 0 ? 
                String.format("%.2f", totalRevenue / totalOrders) : "0");
        
        // 4. 活跃度统计（修复 N+1 查询：复用已查询的 allOrders）
        Map<Integer, List<Orders>> userOrdersMap = allOrders.stream()
                .filter(o -> o.getUserId() != null)
                .collect(Collectors.groupingBy(Orders::getUserId));
        double avgActivityScore = allUsers.stream()
                .mapToInt(u -> calculateActivityScore(u.getId(), 
                        userOrdersMap.getOrDefault(u.getId(), Collections.emptyList())))
                .average()
                .orElse(0);
        
        stats.put("avgActivityScore", String.format("%.1f", avgActivityScore));
        
        return stats;
    }

    // ==================== 工具方法 ====================
}
