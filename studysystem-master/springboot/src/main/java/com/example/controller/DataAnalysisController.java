package com.example.controller;

import com.example.common.Result;
import com.example.service.DataAnalysisService;
import com.example.service.EnhancedRecommendService;
import com.example.utils.TokenUtils;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.Map;

/**
 * 数据分析与推荐控制器
 * 提供用户画像、RFM分层、学习进度预测、智能推荐等接口
 */
@RestController
@RequestMapping("/analysis")
public class DataAnalysisController {

    @Resource
    private DataAnalysisService dataAnalysisService;

    @Resource
    private EnhancedRecommendService enhancedRecommendService;

    // ==================== 用户画像接口 ====================

    /**
     * 获取当前登录用户的画像
     * 返回用户标签、偏好类型、活跃度等信息
     * 
     * @return 用户画像数据
     */
    @GetMapping("/profile")
    public Result getUserProfile() {
        Integer userId = TokenUtils.getCurrentUser().getId();
        Map<String, Object> profile = dataAnalysisService.generateUserProfile(userId);
        return Result.success(profile);
    }

    /**
     * 获取指定用户的画像
     * 
     * @param userId 用户ID
     * @return 用户画像数据
     */
    @GetMapping("/profile/{userId}")
    public Result getUserProfileById(@PathVariable Integer userId) {
        Map<String, Object> profile = dataAnalysisService.generateUserProfile(userId);
        return Result.success(profile);
    }

    // ==================== RFM用户分层接口 ====================

    /**
     * 获取RFM用户分层分析结果
     * 返回各层级用户数量及用户列表
     * 
     * @return RFM分析数据
     */
    @GetMapping("/rfm")
    public Result getRfmAnalysis() {
        Map<String, Object> result = dataAnalysisService.rfmAnalysis();
        return Result.success(result);
    }

    // ==================== 学习进度预测接口 ====================

    /**
     * 获取当前用户的学习进度分析
     * 返回预测完成率、学习建议等
     * 
     * @return 学习进度预测数据
     */
    @GetMapping("/learning-progress")
    public Result getLearningProgress() {
        Integer userId = TokenUtils.getCurrentUser().getId();
        Map<String, Object> progress = dataAnalysisService.predictLearningProgress(userId);
        return Result.success(progress);
    }

    /**
     * 获取指定用户的学习进度分析
     * 
     * @param userId 用户ID
     * @return 学习进度预测数据
     */
    @GetMapping("/learning-progress/{userId}")
    public Result getLearningProgressById(@PathVariable Integer userId) {
        Map<String, Object> progress = dataAnalysisService.predictLearningProgress(userId);
        return Result.success(progress);
    }

    // ==================== 课程热度分析接口 ====================

    /**
     * 获取课程热度排行
     * 综合购买量、时间衰减等因素计算热度
     * 
     * @param limit 返回数量，默认10
     * @return 热门课程列表
     */
    @GetMapping("/course-popularity")
    public Result getCoursePopularity(
            @RequestParam(defaultValue = "10") Integer limit) {
        return Result.success(dataAnalysisService.analyzeCoursePopularity(limit));
    }

    // ==================== 平台统计接口 ====================

    /**
     * 获取平台整体统计数据
     * 包括用户数、课程数、订单数、收入等
     * 
     * @return 平台统计数据
     */
    @GetMapping("/platform-stats")
    public Result getPlatformStatistics() {
        Map<String, Object> stats = dataAnalysisService.getPlatformStatistics();
        return Result.success(stats);
    }

    // ==================== 智能推荐接口 ====================

    /**
     * 智能推荐课程
     * 根据用户状态自动选择最合适的推荐策略
     * 
     * @param limit 推荐数量，默认8
     * @return 推荐结果（包含课程和推荐原因）
     */
    @GetMapping("/smart-recommend")
    public Result smartRecommend(
            @RequestParam(defaultValue = "8") Integer limit) {
        Map<String, Object> result = enhancedRecommendService.smartRecommend(limit);
        return Result.success(result);
    }

    /**
     * 冷启动推荐
     * 针对新用户或未登录用户的热门课程推荐
     * 
     * @param limit 推荐数量
     * @return 推荐课程列表
     */
    @GetMapping("/cold-start")
    public Result coldStartRecommend(
            @RequestParam(defaultValue = "8") Integer limit) {
        return Result.success(enhancedRecommendService.coldStartRecommend(limit));
    }

    /**
     * 混合推荐
     * 融合协同过滤和基于内容的推荐算法
     * 
     * @param limit 推荐数量
     * @return 推荐课程列表
     */
    @GetMapping("/hybrid-recommend")
    public Result hybridRecommend(
            @RequestParam(defaultValue = "8") Integer limit) {
        Integer userId = TokenUtils.getCurrentUser().getId();
        return Result.success(enhancedRecommendService.hybridRecommend(userId, limit));
    }

    /**
     * 学习路径推荐
     * 基于课程难度和依赖关系推荐学习路径
     * 
     * @return 学习路径数据
     */
    @GetMapping("/learning-path")
    public Result learningPathRecommend() {
        Integer userId = TokenUtils.getCurrentUser().getId();
        Map<String, Object> path = enhancedRecommendService.learningPathRecommend(userId);
        return Result.success(path);
    }

    /**
     * 时间衰减热门推荐
     * 近期购买的课程权重更高
     * 
     * @param limit 返回数量
     * @return 热门课程列表
     */
    @GetMapping("/time-decay-hot")
    public Result timeDecayHotRecommend(
            @RequestParam(defaultValue = "10") Integer limit) {
        return Result.success(enhancedRecommendService.timeDecayHotRecommend(limit));
    }
}
