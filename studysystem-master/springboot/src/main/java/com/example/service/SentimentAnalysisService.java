package com.example.service;

import com.example.entity.Comment;
import com.example.entity.CommentSentiment;
import com.example.mapper.CommentMapper;
import com.example.mapper.CommentSentimentMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 评论情感分析服务
 *
 * 算法说明：基于情感词典的规则匹配方法
 * 1. 分词：基于词典的正向最大匹配
 * 2. 情感词识别：匹配正面/负面情感词
 * 3. 情感计算：考虑否定词反转和程度词加权
 * 4. 分类：根据最终得分划分正面/中性/负面
 *
 * 词典规模：
 * - 正面词：约120个
 * - 负面词：约120个
 * - 否定词：约15个
 * - 程度词：约25个
 */
@Service
public class SentimentAnalysisService {

    private static final Logger log = LoggerFactory.getLogger(SentimentAnalysisService.class);

    @Resource
    private CommentMapper commentMapper;

    @Resource
    private CommentSentimentMapper commentSentimentMapper;

    // 正面情感词典
    private static final Set<String> POSITIVE_WORDS = new HashSet<>(Arrays.asList(
            "好", "棒", "优秀", "推荐", "有用", "清晰", "详细", "不错", "满意", "喜欢",
            "爱", "精彩", "完美", "赞", "给力", "干货", "受益匪浅", "收获", "值得",
            "良心", "高质量", "专业", "系统", "全面", "透彻", "易懂", "简单", "通俗",
            "实用", "有效", "帮助", "提升", "进步", "感谢", "感激", "辛苦了", "牛逼",
            "厉害", "强", "太棒了", "非常好", "很好", "极好", "精彩", "出色", "卓越",
            "一流", "顶级", "靠谱", "正宗", "经典", "必备", "神器", "宝藏", "精品",
            "佳作", "用心", "认真", "负责", "耐心", "细致", "周到", "贴心", "感动",
            "惊喜", "意外", "超出预期", "物超所值", "性价比", "划算", "实惠", "优惠",
            "良心价", "免费", "无私", "奉献", "分享", "传承", "启蒙", "指引", "明灯"
    ));

    // 负面情感词典
    private static final Set<String> NEGATIVE_WORDS = new HashSet<>(Arrays.asList(
            "差", "烂", "垃圾", "失望", "难懂", "模糊", "过时", "糟糕", "垃圾", "坑",
            "骗", "忽悠", "虚假宣传", "水", "敷衍", "粗糙", "简陋", "混乱", "错误",
            "误导", "浪费时间", "没用", "无用", "无效", "失败", "后悔", "上当",
            "差评", "反对", "讨厌", "厌恶", "恶心", "烦", "困惑", "迷茫", "糊涂",
            "看不懂", "听不懂", "学不会", "太难", "复杂", "晦涩", "深奥", "枯燥",
            "无聊", "乏味", "单调", "重复", "啰嗦", "冗长", "拖沓", "慢", "卡",
            "崩溃", "闪退", "bug", "错误", "问题", "缺陷", "漏洞", "瑕疵", "毛病",
            "不满", "抱怨", "吐槽", "批评", "指责", "质疑", "怀疑", "担心", "害怕",
            "焦虑", "压力", "痛苦", "折磨", "煎熬", "累", "费劲", "吃力", "困难"
    ));

    // 否定词（用于反转情感极性）
    private static final Set<String> NEGATION_WORDS = new HashSet<>(Arrays.asList(
            "不", "没", "无", "未", "别", "勿", "没有", "不是", "不能", "不会",
            "不可", "不行", "不对", "不好", "不够", "不太", "从未", "毫无", "绝非"
    ));

    // 程度词及权重（用于情感加权）
    private static final Map<String, Double> DEGREE_WORDS = new HashMap<>();

    static {
        // 极程度
        DEGREE_WORDS.put("极其", 2.0);
        DEGREE_WORDS.put("非常", 1.75);
        DEGREE_WORDS.put("十分", 1.75);
        DEGREE_WORDS.put("特别", 1.75);
        DEGREE_WORDS.put("超级", 1.75);
        DEGREE_WORDS.put("太", 1.75);
        // 很程度
        DEGREE_WORDS.put("很", 1.5);
        DEGREE_WORDS.put("相当", 1.5);
        DEGREE_WORDS.put("相当", 1.5);
        DEGREE_WORDS.put("格外", 1.5);
        DEGREE_WORDS.put("分外", 1.5);
        // 较程度
        DEGREE_WORDS.put("比较", 1.25);
        DEGREE_WORDS.put("挺", 1.25);
        DEGREE_WORDS.put("蛮", 1.25);
        DEGREE_WORDS.put("有点", 0.75);
        DEGREE_WORDS.put("稍微", 0.75);
        DEGREE_WORDS.put("略微", 0.75);
        DEGREE_WORDS.put("多少", 0.75);
        DEGREE_WORDS.put("基本", 0.75);
        DEGREE_WORDS.put("大体", 0.75);
    }

    // 情感阈值
    private static final double POSITIVE_THRESHOLD = 0.2;
    private static final double NEGATIVE_THRESHOLD = -0.2;

    /**
     * 批量分析所有评论的情感倾向
     * @return 分析结果摘要
     */
    public Map<String, Object> analyzeAllComments() {
        long startTime = System.currentTimeMillis();

        // 1. 获取所有评论
        List<Comment> comments = commentMapper.selectAll(new Comment());
        if (comments.isEmpty()) {
            throw new RuntimeException("暂无评论数据，无法进行情感分析");
        }

        // 2. 清空旧数据
        commentSentimentMapper.clearAll();

        // 3. 逐条分析
        int positiveCount = 0;
        int negativeCount = 0;
        int neutralCount = 0;
        String now = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));

        for (Comment comment : comments) {
            if (comment.getContent() == null || comment.getContent().trim().isEmpty()) {
                continue;
            }

            SentimentResult result = analyzeSingleComment(comment.getContent());

            CommentSentiment sentiment = new CommentSentiment();
            sentiment.setCommentId(comment.getId());
            sentiment.setSentimentScore(result.score);
            sentiment.setSentimentLabel(result.label);
            sentiment.setPositiveWords(String.join(",", result.positiveWords));
            sentiment.setNegativeWords(String.join(",", result.negativeWords));
            sentiment.setUpdateTime(now);
            commentSentimentMapper.insert(sentiment);

            switch (result.label) {
                case "正面": positiveCount++; break;
                case "负面": negativeCount++; break;
                default: neutralCount++; break;
            }
        }

        long duration = System.currentTimeMillis() - startTime;
        log.info("情感分析完成，评论数={}, 正面={}, 负面={}, 中性={}, 耗时={}ms",
                comments.size(), positiveCount, negativeCount, neutralCount, duration);

        Map<String, Object> summary = new HashMap<>();
        summary.put("totalCount", comments.size());
        summary.put("positiveCount", positiveCount);
        summary.put("negativeCount", negativeCount);
        summary.put("neutralCount", neutralCount);
        summary.put("positiveRate", String.format("%.2f%%", (double) positiveCount / comments.size() * 100));
        summary.put("negativeRate", String.format("%.2f%%", (double) negativeCount / comments.size() * 100));
        summary.put("neutralRate", String.format("%.2f%%", (double) neutralCount / comments.size() * 100));
        summary.put("duration", duration);

        return summary;
    }

    /**
     * 分析单条评论的情感倾向
     * @param content 评论内容
     * @return 情感分析结果
     */
    public SentimentResult analyzeSingleComment(String content) {
        // 1. 分词
        List<String> words = segment(content);

        // 2. 情感词识别与计算
        double totalScore = 0;
        List<String> foundPositive = new ArrayList<>();
        List<String> foundNegative = new ArrayList<>();

        for (int i = 0; i < words.size(); i++) {
            String word = words.get(i);
            double wordScore = 0;

            if (POSITIVE_WORDS.contains(word)) {
                wordScore = 1.0;
                foundPositive.add(word);
            } else if (NEGATIVE_WORDS.contains(word)) {
                wordScore = -1.0;
                foundNegative.add(word);
            }

            if (wordScore != 0) {
                // 检查程度词（向前看2个词）
                double degreeWeight = 1.0;
                for (int j = Math.max(0, i - 2); j < i; j++) {
                    String prevWord = words.get(j);
                    if (DEGREE_WORDS.containsKey(prevWord)) {
                        degreeWeight = DEGREE_WORDS.get(prevWord);
                    }
                }

                // 检查否定词（向前看3个词）
                boolean negated = false;
                for (int j = Math.max(0, i - 3); j < i; j++) {
                    if (NEGATION_WORDS.contains(words.get(j))) {
                        negated = !negated; // 双重否定变肯定
                    }
                }

                if (negated) {
                    wordScore = -wordScore;
                }

                totalScore += wordScore * degreeWeight;
            }
        }

        // 3. 归一化得分到[-1, 1]
        double normalizedScore = normalizeScore(totalScore);

        // 4. 分类
        String label;
        if (normalizedScore > POSITIVE_THRESHOLD) {
            label = "正面";
        } else if (normalizedScore < NEGATIVE_THRESHOLD) {
            label = "负面";
        } else {
            label = "中性";
        }

        SentimentResult result = new SentimentResult();
        result.score = normalizedScore;
        result.label = label;
        result.positiveWords = foundPositive;
        result.negativeWords = foundNegative;

        return result;
    }

    /**
     * 简单分词：基于词典的正向最大匹配（FMM）
     * 对于中文短文本评论，此方法足够有效
     */
    private List<String> segment(String text) {
        List<String> words = new ArrayList<>();
        String cleaned = text.replaceAll("<[^>]+>", "").replaceAll("[^\\u4e00-\\u9fa5]", " ");

        int i = 0;
        while (i < cleaned.length()) {
            // 跳过空格
            if (cleaned.charAt(i) == ' ') {
                i++;
                continue;
            }

            // 尝试最长匹配
            boolean matched = false;
            for (int len = Math.min(4, cleaned.length() - i); len >= 1; len--) {
                String substr = cleaned.substring(i, i + len);
                if (POSITIVE_WORDS.contains(substr) || NEGATIVE_WORDS.contains(substr)
                        || NEGATION_WORDS.contains(substr) || DEGREE_WORDS.containsKey(substr)) {
                    words.add(substr);
                    i += len;
                    matched = true;
                    break;
                }
            }

            if (!matched) {
                // 未匹配到词典词，按单字切分
                words.add(String.valueOf(cleaned.charAt(i)));
                i++;
            }
        }

        return words;
    }

    /**
     * 使用tanh函数将得分归一化到[-1, 1]
     */
    private double normalizeScore(double score) {
        return Math.tanh(score);
    }

    /**
     * 查询情感分析结果
     */
    public List<CommentSentiment> getSentimentResults(String sentimentLabel) {
        return commentSentimentMapper.selectAllWithComment(sentimentLabel);
    }

    /**
     * 获取情感分布统计
     */
    public List<Map<String, Object>> getSentimentDistribution() {
        return commentSentimentMapper.countByLabel();
    }

    /**
     * 获取课程情感排行
     */
    public List<Map<String, Object>> getCourseSentimentRank(Integer limit) {
        return commentSentimentMapper.selectCourseSentimentRank(limit);
    }

    /**
     * 情感分析结果内部类
     */
    public static class SentimentResult {
        public double score;
        public String label;
        public List<String> positiveWords;
        public List<String> negativeWords;
    }
}
