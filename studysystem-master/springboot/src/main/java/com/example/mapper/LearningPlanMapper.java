package com.example.mapper;

import com.example.entity.LearningPlan;
import org.apache.ibatis.annotations.Select;

import java.util.List;

public interface LearningPlanMapper {

    int insert(LearningPlan plan);

    int deleteById(Integer id);

    int updateById(LearningPlan plan);

    LearningPlan selectById(Integer id);

    List<LearningPlan> selectAll(LearningPlan plan);

    @Select("select learning_plan.*, course.name as courseName from learning_plan left join course on learning_plan.target_course_id = course.id where user_id = #{userId} order by create_time desc")
    List<LearningPlan> selectByUserId(Integer userId);
}
