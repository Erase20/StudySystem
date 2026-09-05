package com.example.entity;

/**
 * 用户行为特征向量
 * 用于K-Means聚类分析的特征工程
 */
public class UserBehaviorFeature {

    private Integer userId;
    private String userName;

    // 原始特征值
    private double purchaseCount;      // 购买课程数量
    private double totalLearnDuration; // 总学习时长(分钟)
    private double avgProgress;        // 平均学习进度(0-100)
    private double signinDays;         // 签到天数
    private double commentCount;       // 评论次数
    private double totalSpend;         // 总消费金额

    // 标准化后的特征值(0-1)
    private double normalizedPurchaseCount;
    private double normalizedLearnDuration;
    private double normalizedProgress;
    private double normalizedSigninDays;
    private double normalizedCommentCount;
    private double normalizedTotalSpend;

    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }

    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }

    public double getPurchaseCount() {
        return purchaseCount;
    }

    public void setPurchaseCount(double purchaseCount) {
        this.purchaseCount = purchaseCount;
    }

    public double getTotalLearnDuration() {
        return totalLearnDuration;
    }

    public void setTotalLearnDuration(double totalLearnDuration) {
        this.totalLearnDuration = totalLearnDuration;
    }

    public double getAvgProgress() {
        return avgProgress;
    }

    public void setAvgProgress(double avgProgress) {
        this.avgProgress = avgProgress;
    }

    public double getSigninDays() {
        return signinDays;
    }

    public void setSigninDays(double signinDays) {
        this.signinDays = signinDays;
    }

    public double getCommentCount() {
        return commentCount;
    }

    public void setCommentCount(double commentCount) {
        this.commentCount = commentCount;
    }

    public double getTotalSpend() {
        return totalSpend;
    }

    public void setTotalSpend(double totalSpend) {
        this.totalSpend = totalSpend;
    }

    public double getNormalizedPurchaseCount() {
        return normalizedPurchaseCount;
    }

    public void setNormalizedPurchaseCount(double normalizedPurchaseCount) {
        this.normalizedPurchaseCount = normalizedPurchaseCount;
    }

    public double getNormalizedLearnDuration() {
        return normalizedLearnDuration;
    }

    public void setNormalizedLearnDuration(double normalizedLearnDuration) {
        this.normalizedLearnDuration = normalizedLearnDuration;
    }

    public double getNormalizedProgress() {
        return normalizedProgress;
    }

    public void setNormalizedProgress(double normalizedProgress) {
        this.normalizedProgress = normalizedProgress;
    }

    public double getNormalizedSigninDays() {
        return normalizedSigninDays;
    }

    public void setNormalizedSigninDays(double normalizedSigninDays) {
        this.normalizedSigninDays = normalizedSigninDays;
    }

    public double getNormalizedCommentCount() {
        return normalizedCommentCount;
    }

    public void setNormalizedCommentCount(double normalizedCommentCount) {
        this.normalizedCommentCount = normalizedCommentCount;
    }

    public double getNormalizedTotalSpend() {
        return normalizedTotalSpend;
    }

    public void setNormalizedTotalSpend(double normalizedTotalSpend) {
        this.normalizedTotalSpend = normalizedTotalSpend;
    }

    /**
     * 获取标准化后的特征向量（用于K-Means距离计算）
     */
    public double[] getFeatureVector() {
        return new double[]{
                normalizedPurchaseCount,
                normalizedLearnDuration,
                normalizedProgress,
                normalizedSigninDays,
                normalizedCommentCount,
                normalizedTotalSpend
        };
    }

    /**
     * 获取特征名称数组（用于前端展示）
     */
    public static String[] getFeatureNames() {
        return new String[]{"购买课程数", "学习时长", "平均进度", "签到天数", "评论次数", "消费金额"};
    }
}
