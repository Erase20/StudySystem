package com.example.entity;

import java.io.Serializable;

/**
 * 评论情感分析结果实体类 - 对应数据库comment_sentiment表
 */
public class CommentSentiment implements Serializable {

    private static final long serialVersionUID = 1L;

    private Integer id;
    private Integer commentId;
    private Double sentimentScore;
    private String sentimentLabel;
    private String positiveWords;
    private String negativeWords;
    private String updateTime;

    // 关联评论信息
    private String commentContent;
    private String userName;
    private String courseName;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getCommentId() {
        return commentId;
    }

    public void setCommentId(Integer commentId) {
        this.commentId = commentId;
    }

    public Double getSentimentScore() {
        return sentimentScore;
    }

    public void setSentimentScore(Double sentimentScore) {
        this.sentimentScore = sentimentScore;
    }

    public String getSentimentLabel() {
        return sentimentLabel;
    }

    public void setSentimentLabel(String sentimentLabel) {
        this.sentimentLabel = sentimentLabel;
    }

    public String getPositiveWords() {
        return positiveWords;
    }

    public void setPositiveWords(String positiveWords) {
        this.positiveWords = positiveWords;
    }

    public String getNegativeWords() {
        return negativeWords;
    }

    public void setNegativeWords(String negativeWords) {
        this.negativeWords = negativeWords;
    }

    public String getUpdateTime() {
        return updateTime;
    }

    public void setUpdateTime(String updateTime) {
        this.updateTime = updateTime;
    }

    public String getCommentContent() {
        return commentContent;
    }

    public void setCommentContent(String commentContent) {
        this.commentContent = commentContent;
    }

    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }

    public String getCourseName() {
        return courseName;
    }

    public void setCourseName(String courseName) {
        this.courseName = courseName;
    }
}
