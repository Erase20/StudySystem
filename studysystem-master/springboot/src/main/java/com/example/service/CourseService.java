package com.example.service;

import cn.hutool.core.date.DateUtil;
import cn.hutool.core.util.ObjectUtil;
import com.example.common.enums.RecommendEnum;
import com.example.common.enums.ResultCodeEnum;
import com.example.entity.Account;
import com.example.entity.Course;
import com.example.entity.Orders;
import com.example.exception.CustomException;
import com.example.mapper.CourseMapper;
import com.example.mapper.OrdersMapper;
import com.example.utils.TokenUtils;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import java.util.Date;
import java.util.List;

/**
 * 课程信息表业务处理
 **/
@Service
public class CourseService {

    @Resource
    private CourseMapper courseMapper;

    @Resource
    private OrdersMapper ordersMapper;


    /**
     * 新增
     */
    public void add(Course course) {
        if (ObjectUtil.isNotEmpty(course.getRecommend()) && RecommendEnum.YES.status.equals(course.getRecommend())){
            //  进行校验
            Course recommend = courseMapper.getRecommend(course.getType(), course.getCategory());   //将数据库中的推荐字段是'是'的数据放入recommend 判断是否为空
            if (ObjectUtil.isNotEmpty(recommend)){
                throw new CustomException(ResultCodeEnum.RECOMMEND_ALREADY_ERROR);
            }
        }
        course.setTime(DateUtil.format(new Date(),"yyyy-MM-dd"));
        courseMapper.insert(course);
    }

    /**
     * 删除
     */
    public void deleteById(Integer id) {
        courseMapper.deleteById(id);
    }

    /**
     * 批量删除
     */
    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            courseMapper.deleteById(id);
        }
    }

    /**
     * 修改
     */
    public void updateById(Course course) {
        if (ObjectUtil.isNotEmpty(course.getRecommend()) && RecommendEnum.YES.status.equals(course.getRecommend())){
            //  进行校验
            Course recommend = courseMapper.getRecommend(course.getType(), course.getCategory());
            if (ObjectUtil.isNotEmpty(recommend) && !recommend.getId().equals(course.getId())){
                throw new CustomException(ResultCodeEnum.RECOMMEND_ALREADY_ERROR);
            }
        }
        courseMapper.updateById(course);
    }

    /**
     * 根据ID查询
     */
    public Course selectById(Integer id) {
        Course course = courseMapper.selectById(id);
        //把敏感数据屏蔽
        Account account = TokenUtils.getCurrentUser();
        Orders orders = new Orders();
        orders.setUserId(account.getId());
        orders.setCourseId(id);
        List<Orders> ordersList = ordersMapper.selectAll(orders);
        if (ObjectUtil.isEmpty(ordersList) && 0 != course.getPrice()){
            course.setFile("");
            course.setVideo("");
        }
        return course;
    }

    /**
     * 查询所有
     */
    public List<Course> selectAll(Course course) {
        return courseMapper.selectAll(course);
    }

    /**
     * 分页查询
     */
    public PageInfo<Course> selectPage(Course course, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Course> list = courseMapper.selectAll(course);
        return PageInfo.of(list);
    }

    public Course getRecommend(String type, String category) {
        return courseMapper.getRecommend(type, category);
    }

    public List<Course> selectTop8(String type, String category) {
        return courseMapper.selectTop8(type, category);
    }
}