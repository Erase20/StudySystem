package com.example.service;

import com.example.entity.Course;
import com.example.entity.Orders;
import com.example.entity.Scoreorder;
import com.example.mapper.CourseMapper;
import com.example.mapper.OrdersMapper;
import com.example.mapper.ScoreorderMapper;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 协同过滤推荐服务
 * 基于用户的协同过滤算法（User-based Collaborative Filtering）
 *
 */
@Service
public class CollaborativeFilterService {

    @Resource
    private OrdersMapper ordersMapper;

    @Resource
    private ScoreorderMapper scoreorderMapper;

    @Resource
    private CourseMapper courseMapper;

    /**
     * 为指定用户推荐课程
     * @param userId 用户ID
     * @param topN 推荐数量
     * @return 推荐课程列表
     */
    public List<Course> recommendCourses(Integer userId, int topN) {
        // 1. 获取所有用户的购买记录
        List<Orders> allOrders = ordersMapper.selectAll(new Orders());

        // 2. 获取积分兑换记录（仅用于扩充用户兴趣判断，不混入课程ID）
        List<Scoreorder> allScoreOrders = scoreorderMapper.selectAll(new Scoreorder());

        // 3. 构建用户-课程矩阵（仅课程购买行为）
        Map<Integer, Set<Integer>> userCourseMap = buildUserCourseMatrix(allOrders);

        // 4. 用积分兑换数据增强相似度计算（独立维度）
        Map<Integer, Set<Integer>> userScoreMap = buildUserScoreMatrix(allScoreOrders);

        // 5. 获取当前用户已购买的课程
        Set<Integer> currentUserCourses = userCourseMap.getOrDefault(userId, new HashSet<>());

        // 6. 计算用户相似度，找到相似用户
        List<Integer> similarUsers = findSimilarUsers(userId, userCourseMap, userScoreMap, 5);

        // 7. 基于相似用户推荐课程
        Set<Integer> recommendCourseIds = new LinkedHashSet<>();
        for (Integer similarUserId : similarUsers) {
            Set<Integer> similarUserCourses = userCourseMap.get(similarUserId);
            if (similarUserCourses != null) {
                for (Integer courseId : similarUserCourses) {
                    if (!currentUserCourses.contains(courseId)) {
                        recommendCourseIds.add(courseId);
                        if (recommendCourseIds.size() >= topN * 2) break;
                    }
                }
            }
            if (recommendCourseIds.size() >= topN * 2) break;
        }

        // 8. 如果推荐数量不足，补充热门课程（复用 allOrders，不重复查库）
        if (recommendCourseIds.size() < topN) {
            List<Integer> hotCourseIds = getHotCourseIds(allOrders, topN);
            for (Integer courseId : hotCourseIds) {
                if (!currentUserCourses.contains(courseId)) {
                    recommendCourseIds.add(courseId);
                }
                if (recommendCourseIds.size() >= topN) break;
            }
        }

        // 9. 批量查询课程详情（修复 N+1 查询）
        return batchGetCourses(recommendCourseIds, topN);
    }

    /**
     * 构建用户-课程购买矩阵（仅包含真实课程ID）
     */
    private Map<Integer, Set<Integer>> buildUserCourseMatrix(List<Orders> orders) {
        Map<Integer, Set<Integer>> userCourseMap = new HashMap<>();
        for (Orders order : orders) {
            Integer userId = order.getUserId();
            Integer courseId = order.getCourseId();
            if (userId != null && courseId != null) {
                userCourseMap.computeIfAbsent(userId, k -> new HashSet<>()).add(courseId);
            }
        }
        return userCourseMap;
    }

    /**
     * 构建用户-积分商品矩阵（独立维度，不与课程ID混用）
     */
    private Map<Integer, Set<Integer>> buildUserScoreMatrix(List<Scoreorder> scoreOrders) {
        Map<Integer, Set<Integer>> userScoreMap = new HashMap<>();
        for (Scoreorder scoreOrder : scoreOrders) {
            Integer userId = scoreOrder.getUserId();
            Integer scoreId = scoreOrder.getScoreId();
            if (userId != null && scoreId != null) {
                userScoreMap.computeIfAbsent(userId, k -> new HashSet<>()).add(scoreId);
            }
        }
        return userScoreMap;
    }

    /**
     * 找到与当前用户最相似的K个用户
     * 综合课程购买相似度和积分兑换相似度（加权融合）
     *
     * @param userId 当前用户ID
     * @param userCourseMap 用户-课程矩阵
     * @param userScoreMap 用户-积分商品矩阵
     * @param k 返回的相似用户数量
     */
    private List<Integer> findSimilarUsers(Integer userId,
                                           Map<Integer, Set<Integer>> userCourseMap,
                                           Map<Integer, Set<Integer>> userScoreMap,
                                           int k) {
        Set<Integer> currentUserCourses = userCourseMap.getOrDefault(userId, new HashSet<>());
        Set<Integer> currentUserScores = userScoreMap.getOrDefault(userId, new HashSet<>());

        if (currentUserCourses.isEmpty() && currentUserScores.isEmpty()) {
            return new ArrayList<>();
        }

        // 收集所有用户ID
        Set<Integer> allUserIds = new HashSet<>();
        allUserIds.addAll(userCourseMap.keySet());
        allUserIds.addAll(userScoreMap.keySet());
        allUserIds.remove(userId);

        // 计算综合相似度：课程相似度(权重0.8) + 积分商品相似度(权重0.2)
        Map<Integer, Double> similarityMap = new HashMap<>();
        for (Integer otherUserId : allUserIds) {
            double courseSim = calculateJaccardSimilarity(
                    currentUserCourses,
                    userCourseMap.getOrDefault(otherUserId, Collections.emptySet()));
            double scoreSim = calculateJaccardSimilarity(
                    currentUserScores,
                    userScoreMap.getOrDefault(otherUserId, Collections.emptySet()));

            double totalSim = courseSim * 0.8 + scoreSim * 0.2;
            if (totalSim > 0) {
                similarityMap.put(otherUserId, totalSim);
            }
        }

        return similarityMap.entrySet().stream()
                .sorted(Map.Entry.<Integer, Double>comparingByValue().reversed())
                .limit(k)
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());
    }

    /**
     * 计算Jaccard相似系数
     * J(A,B) = |A ∩ B| / |A ∪ B|
     */
    private double calculateJaccardSimilarity(Set<Integer> set1, Set<Integer> set2) {
        if (set1 == null || set2 == null || set1.isEmpty() || set2.isEmpty()) {
            return 0.0;
        }
        Set<Integer> intersection = new HashSet<>(set1);
        intersection.retainAll(set2);
        Set<Integer> union = new HashSet<>(set1);
        union.addAll(set2);
        return (double) intersection.size() / union.size();
    }

    /**
     * 从已有订单数据中统计热门课程ID（不再重复查库）
     */
    private List<Integer> getHotCourseIds(List<Orders> allOrders, int limit) {
        Map<Integer, Integer> courseCountMap = new HashMap<>();
        for (Orders order : allOrders) {
            Integer courseId = order.getCourseId();
            if (courseId != null) {
                courseCountMap.merge(courseId, 1, Integer::sum);
            }
        }
        return courseCountMap.entrySet().stream()
                .sorted(Map.Entry.<Integer, Integer>comparingByValue().reversed())
                .limit(limit)
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());
    }

    /**
     * 批量查询课程详情（修复 N+1 查询问题）
     * 使用 selectByIds 一次性查出所有课程，再按原顺序排列
     */
    private List<Course> batchGetCourses(Set<Integer> courseIds, int limit) {
        if (courseIds.isEmpty()) {
            return new ArrayList<>();
        }
        // 限制数量
        Set<Integer> limitedIds = courseIds.stream().limit(limit).collect(Collectors.toCollection(LinkedHashSet::new));
        List<Course> courses = courseMapper.selectByIds(limitedIds);

        // 按原始顺序排列
        Map<Integer, Course> courseMap = courses.stream()
                .collect(Collectors.toMap(Course::getId, c -> c, (a, b) -> a));
        List<Course> result = new ArrayList<>();
        for (Integer id : limitedIds) {
            Course course = courseMap.get(id);
            if (course != null) {
                result.add(course);
            }
        }
        return result;
    }

    /**
     * 基于课程类型的推荐（当用户无历史数据时使用）
     */
    public List<Course> recommendByType(String type, Integer userId, int topN) {
        Orders query = new Orders();
        query.setUserId(userId);
        List<Orders> userOrders = ordersMapper.selectAll(query);
        Set<Integer> purchasedCourseIds = userOrders.stream()
                .map(Orders::getCourseId)
                .filter(Objects::nonNull)
                .collect(Collectors.toSet());

        List<Course> allCourses = courseMapper.selectAll(new Course());
        return allCourses.stream()
                .filter(c -> type.equals(c.getType()))
                .filter(c -> !purchasedCourseIds.contains(c.getId()))
                .limit(topN)
                .collect(Collectors.toList());
    }
}
