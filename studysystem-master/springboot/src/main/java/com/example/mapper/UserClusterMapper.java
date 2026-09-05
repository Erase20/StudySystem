package com.example.mapper;

import com.example.entity.UserCluster;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 用户聚类结果数据访问层
 */
public interface UserClusterMapper {

    int insert(UserCluster userCluster);

    int deleteById(Integer id);

    int updateById(UserCluster userCluster);

    UserCluster selectById(Integer id);

    List<UserCluster> selectAll(UserCluster userCluster);

    @Select("SELECT * FROM user_cluster WHERE user_id = #{userId}")
    UserCluster selectByUserId(Integer userId);

    /**
     * 清空聚类结果表
     */
    void clearAll();

    /**
     * 按聚类标签统计数量
     */
    @Select("SELECT cluster_label, COUNT(*) as cnt FROM user_cluster GROUP BY cluster_label")
    List<java.util.Map<String, Object>> countByCluster();

    /**
     * 查询聚类结果并关联用户信息
     */
    List<UserCluster> selectAllWithUser(@Param("clusterLabel") Integer clusterLabel);
}
