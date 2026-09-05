package com.example.controller;

import com.example.common.Result;
import com.example.entity.UserCluster;
import com.example.service.UserClusterService;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;
import java.util.Map;

/**
 * 用户聚类分析接口
 * 提供K-Means聚类执行和结果查询
 */
@RestController
@RequestMapping("/userCluster")
public class UserClusterController {

    @Resource
    private UserClusterService userClusterService;

    /**
     * 执行K-Means聚类分析
     * @return 聚类结果摘要（轮廓系数、各簇分布、中心点等）
     */
    @PostMapping("/perform")
    public Result performClustering() {
        try {
            Map<String, Object> result = userClusterService.performClustering();
            return Result.success(result);
        } catch (Exception e) {
            return Result.error("500", "聚类分析失败：" + e.getMessage());
        }
    }

    /**
     * 查询聚类结果列表（带用户信息）
     * @param clusterLabel 聚类标签筛选（可选）
     * @return 聚类结果列表
     */
    @GetMapping("/selectAll")
    public Result selectAll(@RequestParam(required = false) Integer clusterLabel) {
        List<UserCluster> list = userClusterService.getClusterResults(clusterLabel);
        return Result.success(list);
    }

    /**
     * 获取聚类分布统计
     * @return 各簇用户数量统计
     */
    @GetMapping("/distribution")
    public Result getDistribution() {
        List<Map<String, Object>> distribution = userClusterService.getClusterDistribution();
        return Result.success(distribution);
    }
}
