package com.example.mapper;

import com.example.entity.LearningRecord;
import org.apache.ibatis.annotations.Select;

import java.util.List;

public interface LearningRecordMapper {

    int insert(LearningRecord record);

    int deleteById(Integer id);

    int updateById(LearningRecord record);

    LearningRecord selectById(Integer id);

    List<LearningRecord> selectAll(LearningRecord record);

    @Select("select * from learning_record where user_id = #{userId} order by update_time desc")
    List<LearningRecord> selectByUserId(Integer userId);

    @Select("select * from learning_record where user_id = #{userId} and course_id = #{courseId}")
    LearningRecord selectByUserAndCourse(Integer userId, Integer courseId);
}
