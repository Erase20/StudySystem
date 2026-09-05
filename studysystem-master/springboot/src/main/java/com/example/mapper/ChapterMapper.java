package com.example.mapper;

import com.example.entity.Chapter;
import org.apache.ibatis.annotations.Param;

import java.util.List;

public interface ChapterMapper {

    int insert(Chapter chapter);

    int deleteById(Integer id);

    int updateById(Chapter chapter);

    Chapter selectById(Integer id);

    List<Chapter> selectAll(Chapter chapter);

    List<Chapter> selectByCourseId(@Param("courseId") Integer courseId);

    void deleteByCourseId(@Param("courseId") Integer courseId);
}
