package com.example.controller;

import com.example.common.Result;
import com.example.entity.CommentSentiment;
import com.example.service.SentimentAnalysisService;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;
import java.util.Map;

/**
 * 评论情感分析接口
 * 提供情感分析执行和结果查询
 */
@RestController
@RequestMapping("/sentiment")
public class SentimentController {

    @Resource
    private SentimentAnalysisService sentimentAnalysisService;

    /**
     * 批量分析所有评论情感
     * @return 分析结果摘要（各情感类别数量、占比等）
     */
    @PostMapping("/analyze")
    public Result analyzeAll() {
        try {
            Map<String, Object> result = sentimentAnalysisService.analyzeAllComments();
            return Result.success(result);
        } catch (Exception e) {
            return Result.error("500", "情感分析失败：" + e.getMessage());
        }
    }

    /**
     * 单条评论情感分析（测试用）
     * @param content 评论内容
     * @return 情感分析结果
     */
    @PostMapping("/analyzeSingle")
    public Result analyzeSingle(@RequestBody Map<String, String> params) {
        String content = params.get("content");
        if (content == null || content.trim().isEmpty()) {
            return Result.error("500", "评论内容不能为空");
        }
        SentimentAnalysisService.SentimentResult result = sentimentAnalysisService.analyzeSingleComment(content);
        return Result.success(result);
    }

    /**
     * 查询情感分析结果列表
     * @param sentimentLabel 情感标签筛选（可选：正面/中性/负面）
     * @return 情感分析结果列表
     */
    @GetMapping("/selectAll")
    public Result selectAll(@RequestParam(required = false) String sentimentLabel) {
        List<CommentSentiment> list = sentimentAnalysisService.getSentimentResults(sentimentLabel);
        return Result.success(list);
    }

    /**
     * 获取情感分布统计
     * @return 各情感标签数量统计
     */
    @GetMapping("/distribution")
    public Result getDistribution() {
        List<Map<String, Object>> distribution = sentimentAnalysisService.getSentimentDistribution();
        return Result.success(distribution);
    }

    /**
     * 获取课程情感评分排行
     * @param limit 返回数量（默认10）
     * @return 课程情感评分排行
     */
    @GetMapping("/courseRank")
    public Result getCourseRank(@RequestParam(defaultValue = "10") Integer limit) {
        List<Map<String, Object>> rank = sentimentAnalysisService.getCourseSentimentRank(limit);
        return Result.success(rank);
    }
}
