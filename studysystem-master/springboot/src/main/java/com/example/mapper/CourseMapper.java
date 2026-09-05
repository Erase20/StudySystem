package com.example.mapper;

import com.example.entity.Course;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;
import java.util.Set;

/**
 * 操作course相关数据接口
*/
public interface CourseMapper {

    /**
      * 新增
    */
    int insert(Course course);

    /**
      * 删除
    */
    int deleteById(Integer id);

    /**
      * 修改
    */
    int updateById(Course course);

    /**
      * 根据ID查询
    */
    Course selectById(Integer id);

    /**
      * 查询所有
    */
    List<Course> selectAll(Course course);

    Course getRecommend(@Param("type") String type, @Param("category") String category);

    List<Course> selectTop8(@Param("type") String type, @Param("category") String category);

    /**
     * 查询热门课程（按购买次数排序，无订单时返回最新课程）
     */
    @Select("SELECT c.* FROM course c " +
            "LEFT JOIN orders o ON c.id = o.course_id " +
            "GROUP BY c.id " +
            "ORDER BY COUNT(o.id) DESC, c.id DESC " +
            "LIMIT #{limit}")
    List<Course> selectHotCourses(int limit);

    /**
     * 根据ID集合批量查误课程
     */
    List<Course> selectByIds(@Param("ids") Set<Integer> ids);
}