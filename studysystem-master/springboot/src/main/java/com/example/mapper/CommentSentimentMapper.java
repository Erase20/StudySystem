package com.example.mapper;

import com.example.entity.CommentSentiment;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;
import java.util.Map;

/**
 * 评论情感分析结果数据访问层
 */
public interface CommentSentimentMapper {

    int insert(CommentSentiment commentSentiment);

    int deleteById(Integer id);

    int updateById(CommentSentiment commentSentiment);

    CommentSentiment selectById(Integer id);

    List<CommentSentiment> selectAll(CommentSentiment commentSentiment);

    @Select("SELECT * FROM comment_sentiment WHERE comment_id = #{commentId}")
    CommentSentiment selectByCommentId(Integer commentId);

    void clearAll();

    /**
     * 按情感标签统计
     */
    @Select("SELECT sentiment_label, COUNT(*) as cnt FROM comment_sentiment GROUP BY sentiment_label")
    List<Map<String, Object>> countByLabel();

    /**
     * 查询情感分析结果并关联评论信息
     */
    List<CommentSentiment> selectAllWithComment(@Param("sentimentLabel") String sentimentLabel);

    /**
     * 获取课程情感评分排行
     */
    List<Map<String, Object>> selectCourseSentimentRank(@Param("limit") Integer limit);
}
