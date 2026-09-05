package com.example.service;

import com.example.entity.*;
import com.example.mapper.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

/**
 * K-Means用户行为聚类分析服务
 *
 * 算法说明：
 * 1. 特征工程：从多表聚合用户行为数据，构建6维特征向量
 * 2. Min-Max标准化：将各特征缩放到[0,1]区间
 * 3. K-Means聚类：K=4，迭代至中心点收敛
 * 4. 轮廓系数评估：计算聚类效果
 *
 * 聚类群体定义：
 * - 0: 流失风险用户 (低购买、低学习、低活跃)
 * - 1: 低活跃用户 (偶尔学习、低消费)
 * - 2: 一般活跃用户 (正常学习、中等消费)
 * - 3: 高价值用户 (高购买、高学习、高活跃)
 */
@Service
public class UserClusterService {

    private static final Logger log = LoggerFactory.getLogger(UserClusterService.class);

    @Resource
    private UserMapper userMapper;

    @Resource
    private OrdersMapper ordersMapper;

    @Resource
    private LearningRecordMapper learningRecordMapper;

    @Resource
    private SigninMapper signinMapper;

    @Resource
    private CommentMapper commentMapper;

    @Resource
    private UserClusterMapper userClusterMapper;

    private final ObjectMapper objectMapper = new ObjectMapper();

    // 聚类群体名称
    private static final String[] CLUSTER_NAMES = {"流失风险", "低活跃用户", "一般活跃用户", "高价值用户"};
    // K值
    private static final int K = 4;
    // 最大迭代次数
    private static final int MAX_ITERATIONS = 100;
    // 收敛阈值
    private static final double CONVERGENCE_THRESHOLD = 0.001;

    /**
     * 执行K-Means聚类分析
     * @return 聚类结果摘要
     */
    public Map<String, Object> performClustering() {
        long startTime = System.currentTimeMillis();

        // 1. 特征工程：构建用户行为特征向量
        List<UserBehaviorFeature> features = extractFeatures();
        if (features.size() < K) {
            throw new RuntimeException("用户数量不足，无法进行聚类分析（至少需要" + K + "个用户）");
        }

        // 2. Min-Max标准化
        normalizeFeatures(features);

        // 3. K-Means聚类
        int[] labels = kMeans(features, K);

        // 4. 计算轮廓系数
        double silhouetteScore = calculateSilhouetteScore(features, labels);

        // 5. 计算各簇中心特征
        List<double[]> clusterCenters = calculateClusterCenters(features, labels, K);

        // 6. 保存聚类结果到数据库
        saveClusterResults(features, labels, clusterCenters);

        long duration = System.currentTimeMillis() - startTime;
        log.info("K-Means聚类完成，用户数={}, 轮廓系数={}, 耗时={}ms", features.size(), String.format("%.4f", silhouetteScore), duration);

        // 7. 构建返回结果
        Map<String, Object> result = new HashMap<>();
        result.put("userCount", features.size());
        result.put("silhouetteScore", silhouetteScore);
        result.put("duration", duration);
        result.put("clusterCenters", clusterCenters);
        result.put("clusterNames", CLUSTER_NAMES);
        result.put("featureNames", UserBehaviorFeature.getFeatureNames());

        // 各簇统计
        Map<Integer, Integer> clusterCount = new HashMap<>();
        for (int label : labels) {
            clusterCount.merge(label, 1, Integer::sum);
        }
        result.put("clusterDistribution", clusterCount);

        return result;
    }

    /**
     * 特征工程：从多表聚合用户行为数据
     */
    private List<UserBehaviorFeature> extractFeatures() {
        List<User> users = userMapper.selectAll(new User());
        List<UserBehaviorFeature> features = new ArrayList<>();

        for (User user : users) {
            UserBehaviorFeature feature = new UserBehaviorFeature();
            feature.setUserId(user.getId());
            feature.setUserName(user.getName());

            // 1. 购买课程数量 & 总消费金额
            Orders orderQuery = new Orders();
            orderQuery.setUserId(user.getId());
            List<Orders> orders = ordersMapper.selectAll(orderQuery);
            feature.setPurchaseCount(orders.size());
            double totalSpend = orders.stream().mapToDouble(o -> o.getPrice() != null ? o.getPrice() : 0).sum();
            feature.setTotalSpend(totalSpend);

            // 2. 总学习时长 & 平均进度
            LearningRecord recordQuery = new LearningRecord();
            recordQuery.setUserId(user.getId());
            List<LearningRecord> records = learningRecordMapper.selectAll(recordQuery);
            int totalDuration = records.stream().mapToInt(r -> r.getDuration() != null ? r.getDuration() : 0).sum();
            double avgProgress = records.isEmpty() ? 0 :
                    records.stream().mapToInt(r -> r.getProgress() != null ? r.getProgress() : 0).average().orElse(0);
            feature.setTotalLearnDuration(totalDuration);
            feature.setAvgProgress(avgProgress);

            // 3. 签到天数
            Signin signinQuery = new Signin();
            signinQuery.setUserId(user.getId());
            List<Signin> signins = signinMapper.selectAll(signinQuery);
            feature.setSigninDays(signins.size());

            // 4. 评论次数
            Comment commentQuery = new Comment();
            commentQuery.setUserId(user.getId());
            List<Comment> comments = commentMapper.selectAll(commentQuery);
            feature.setCommentCount(comments.size());

            features.add(feature);
        }

        return features;
    }

    /**
     * Min-Max标准化：将特征缩放到[0,1]区间
     * formula: x' = (x - min) / (max - min)
     */
    private void normalizeFeatures(List<UserBehaviorFeature> features) {
        if (features.isEmpty()) return;

        // 计算各维度的最大值和最小值
        double[] minValues = new double[6];
        double[] maxValues = new double[6];
        Arrays.fill(minValues, Double.MAX_VALUE);
        Arrays.fill(maxValues, -Double.MAX_VALUE);

        for (UserBehaviorFeature f : features) {
            double[] rawValues = {f.getPurchaseCount(), f.getTotalLearnDuration(), f.getAvgProgress(),
                    f.getSigninDays(), f.getCommentCount(), f.getTotalSpend()};
            for (int i = 0; i < 6; i++) {
                minValues[i] = Math.min(minValues[i], rawValues[i]);
                maxValues[i] = Math.max(maxValues[i], rawValues[i]);
            }
        }

        // 标准化并赋值
        for (UserBehaviorFeature f : features) {
            f.setNormalizedPurchaseCount(normalize(f.getPurchaseCount(), minValues[0], maxValues[0]));
            f.setNormalizedLearnDuration(normalize(f.getTotalLearnDuration(), minValues[1], maxValues[1]));
            f.setNormalizedProgress(normalize(f.getAvgProgress(), minValues[2], maxValues[2]));
            f.setNormalizedSigninDays(normalize(f.getSigninDays(), minValues[3], maxValues[3]));
            f.setNormalizedCommentCount(normalize(f.getCommentCount(), minValues[4], maxValues[4]));
            f.setNormalizedTotalSpend(normalize(f.getTotalSpend(), minValues[5], maxValues[5]));
        }
    }

    private double normalize(double value, double min, double max) {
        if (max - min == 0) return 0;
        return (value - min) / (max - min);
    }

    /**
     * K-Means核心算法
     * @param features 标准化后的特征列表
     * @param k 聚类数量
     * @return 每个样本的聚类标签
     */
    private int[] kMeans(List<UserBehaviorFeature> features, int k) {
        int n = features.size();
        int[] labels = new int[n];
        double[][] centers = new double[k][6];

        // 1. 随机初始化中心点（K-Means++简化版：随机选k个样本作为初始中心）
        Random random = new Random(42); // 固定种子保证结果可复现
        Set<Integer> selected = new HashSet<>();
        for (int i = 0; i < k; i++) {
            int idx;
            do {
                idx = random.nextInt(n);
            } while (selected.contains(idx));
            selected.add(idx);
            centers[i] = features.get(idx).getFeatureVector().clone();
        }

        // 2. 迭代优化
        for (int iter = 0; iter < MAX_ITERATIONS; iter++) {
            // 2.1 分配样本到最近的中心
            boolean changed = false;
            for (int i = 0; i < n; i++) {
                double[] vector = features.get(i).getFeatureVector();
                int nearestCluster = findNearestCluster(vector, centers);
                if (labels[i] != nearestCluster) {
                    labels[i] = nearestCluster;
                    changed = true;
                }
            }

            // 2.2 更新中心点
            double[][] newCenters = new double[k][6];
            int[] clusterSizes = new int[k];
            for (int i = 0; i < n; i++) {
                double[] vector = features.get(i).getFeatureVector();
                int cluster = labels[i];
                for (int j = 0; j < 6; j++) {
                    newCenters[cluster][j] += vector[j];
                }
                clusterSizes[cluster]++;
            }

            for (int i = 0; i < k; i++) {
                if (clusterSizes[i] > 0) {
                    for (int j = 0; j < 6; j++) {
                        newCenters[i][j] /= clusterSizes[i];
                    }
                }
            }

            // 2.3 检查收敛
            double maxShift = 0;
            for (int i = 0; i < k; i++) {
                maxShift = Math.max(maxShift, euclideanDistance(centers[i], newCenters[i]));
            }
            centers = newCenters;

            if (!changed || maxShift < CONVERGENCE_THRESHOLD) {
                log.info("K-Means收敛于第{}轮迭代", iter + 1);
                break;
            }
        }

        return labels;
    }

    /**
     * 找到最近的簇中心
     */
    private int findNearestCluster(double[] vector, double[][] centers) {
        int nearest = 0;
        double minDist = Double.MAX_VALUE;
        for (int i = 0; i < centers.length; i++) {
            double dist = euclideanDistance(vector, centers[i]);
            if (dist < minDist) {
                minDist = dist;
                nearest = i;
            }
        }
        return nearest;
    }

    /**
     * 欧氏距离计算
     */
    private double euclideanDistance(double[] a, double[] b) {
        double sum = 0;
        for (int i = 0; i < a.length; i++) {
            sum += Math.pow(a[i] - b[i], 2);
        }
        return Math.sqrt(sum);
    }

    /**
     * 计算轮廓系数(Silhouette Score)
     * 取值范围[-1,1]，越接近1表示聚类效果越好
     */
    private double calculateSilhouetteScore(List<UserBehaviorFeature> features, int[] labels) {
        int n = features.size();
        if (n <= K) return 0;

        double totalScore = 0;
        for (int i = 0; i < n; i++) {
            double[] vector_i = features.get(i).getFeatureVector();
            int cluster_i = labels[i];

            // 计算a(i)：样本i到同簇其他样本的平均距离
            double a = 0;
            int sameClusterCount = 0;
            for (int j = 0; j < n; j++) {
                if (i != j && labels[j] == cluster_i) {
                    a += euclideanDistance(vector_i, features.get(j).getFeatureVector());
                    sameClusterCount++;
                }
            }
            a = sameClusterCount > 0 ? a / sameClusterCount : 0;

            // 计算b(i)：样本i到最近其他簇的平均距离
            double b = Double.MAX_VALUE;
            for (int c = 0; c < K; c++) {
                if (c == cluster_i) continue;
                double avgDist = 0;
                int count = 0;
                for (int j = 0; j < n; j++) {
                    if (labels[j] == c) {
                        avgDist += euclideanDistance(vector_i, features.get(j).getFeatureVector());
                        count++;
                    }
                }
                if (count > 0) {
                    avgDist /= count;
                    b = Math.min(b, avgDist);
                }
            }

            // 轮廓系数 s(i) = (b - a) / max(a, b)
            if (Math.max(a, b) > 0) {
                totalScore += (b - a) / Math.max(a, b);
            }
        }

        return totalScore / n;
    }

    /**
     * 计算各簇中心特征（用于前端雷达图展示）
     */
    private List<double[]> calculateClusterCenters(List<UserBehaviorFeature> features, int[] labels, int k) {
        List<double[]> centers = new ArrayList<>();
        for (int i = 0; i < k; i++) {
            centers.add(new double[6]);
        }

        int[] counts = new int[k];
        for (int i = 0; i < features.size(); i++) {
            double[] vector = features.get(i).getFeatureVector();
            int cluster = labels[i];
            for (int j = 0; j < 6; j++) {
                centers.get(cluster)[j] += vector[j];
            }
            counts[cluster]++;
        }

        for (int i = 0; i < k; i++) {
            if (counts[i] > 0) {
                for (int j = 0; j < 6; j++) {
                    centers.get(i)[j] /= counts[i];
                }
            }
        }

        return centers;
    }

    /**
     * 保存聚类结果到数据库
     */
    private void saveClusterResults(List<UserBehaviorFeature> features, int[] labels, List<double[]> centers) {
        // 清空旧数据
        userClusterMapper.clearAll();

        String now = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));

        for (int i = 0; i < features.size(); i++) {
            UserBehaviorFeature feature = features.get(i);
            int label = labels[i];

            UserCluster cluster = new UserCluster();
            cluster.setUserId(feature.getUserId());
            cluster.setClusterLabel(label);
            cluster.setClusterName(CLUSTER_NAMES[label]);

            // 保存特征向量JSON
            Map<String, Object> featureMap = new HashMap<>();
            featureMap.put("purchaseCount", feature.getPurchaseCount());
            featureMap.put("totalLearnDuration", feature.getTotalLearnDuration());
            featureMap.put("avgProgress", feature.getAvgProgress());
            featureMap.put("signinDays", feature.getSigninDays());
            featureMap.put("commentCount", feature.getCommentCount());
            featureMap.put("totalSpend", feature.getTotalSpend());
            try {
                cluster.setFeaturesJson(objectMapper.writeValueAsString(featureMap));
            } catch (Exception e) {
                cluster.setFeaturesJson("{}");
            }

            cluster.setUpdateTime(now);
            userClusterMapper.insert(cluster);
        }
    }

    /**
     * 查询聚类结果（带用户信息）
     */
    public List<UserCluster> getClusterResults(Integer clusterLabel) {
        return userClusterMapper.selectAllWithUser(clusterLabel);
    }

    /**
     * 获取聚类统计分布
     */
    public List<Map<String, Object>> getClusterDistribution() {
        return userClusterMapper.countByCluster();
    }
}
