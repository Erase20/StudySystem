package com.example.entity;

import java.io.Serializable;

/**
 * 用户聚类结果实体类 - 对应数据库user_cluster表
 * 存储K-Means聚类分析结果
 */
public class UserCluster implements Serializable {

    private static final long serialVersionUID = 1L;

    private Integer id;
    private Integer userId;
    private Integer clusterLabel;
    private String clusterName;
    private String featuresJson;
    private String updateTime;

    // 关联用户信息显示
    private String userName;
    private String userAvatar;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getUserId() {
        return userId;
    }

    public void setUserId(Integer userId) {
        this.userId = userId;
    }

    public Integer getClusterLabel() {
        return clusterLabel;
    }

    public void setClusterLabel(Integer clusterLabel) {
        this.clusterLabel = clusterLabel;
    }

    public String getClusterName() {
        return clusterName;
    }

    public void setClusterName(String clusterName) {
        this.clusterName = clusterName;
    }

    public String getFeaturesJson() {
        return featuresJson;
    }

    public void setFeaturesJson(String featuresJson) {
        this.featuresJson = featuresJson;
    }

    public String getUpdateTime() {
        return updateTime;
    }

    public void setUpdateTime(String updateTime) {
        this.updateTime = updateTime;
    }

    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }

    public String getUserAvatar() {
        return userAvatar;
    }

    public void setUserAvatar(String userAvatar) {
        this.userAvatar = userAvatar;
    }
}
