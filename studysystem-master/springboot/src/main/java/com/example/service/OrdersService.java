package com.example.service;

import cn.hutool.core.date.DateUtil;
import com.example.common.enums.MemberEnum;
import com.example.common.enums.ResultCodeEnum;
import com.example.common.enums.RoleEnum;
import com.example.entity.Account;
import com.example.entity.Course;
import com.example.entity.Orders;
import com.example.entity.User;
import com.example.exception.CustomException;
import com.example.mapper.CourseMapper;
import com.example.mapper.OrdersMapper;
import com.example.mapper.UserMapper;
import com.example.utils.TokenUtils;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import org.springframework.stereotype.Service;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import java.util.Date;
import java.util.List;

/**
 * 公告信息表业务处理
 **/
@Service
public class OrdersService {

    @Resource
    private OrdersMapper ordersMapper;

    @Resource
    private UserMapper userMapper;

    @Resource
    private CourseMapper courseMapper;
    
    /**
     * 新增
     */
    public void add(Orders orders) {
        orders.setTime(DateUtil.now());
        orders.setOrderId(DateUtil.format(new Date(),"yyyyMMddHHmmss"));
        //获取当前登录用户
        Account currentUser = TokenUtils.getCurrentUser();
        Course course = courseMapper.selectById(orders.getCourseId());

        // 管理员无限余额，直接创建订单，不查用户表、不检查余额、不扣费
        if (RoleEnum.ADMIN.name().equals(currentUser.getRole())) {
            orders.setPrice(0.0);
            ordersMapper.insert(orders);
            return;
        }

        //普通用户购买流程
        User user = userMapper.selectById(currentUser.getId());

        Double price = course.getPrice();
        if (MemberEnum.YES.info.equals(user.getMember())){
            //打折
            price = course.getPrice() * course.getDiscount();
        }

        //判断余额
        if (user.getAccount() < price){
            throw new CustomException(ResultCodeEnum.ACCOUNT_LOWER_ERROR);
        }
        orders.setPrice(price);
        //创建订单
        ordersMapper.insert(orders);
        //扣除用户余额
        user.setAccount(user.getAccount() - price);
        userMapper.updateById(user);
    }

    /**
     * 删除
     */
    public void deleteById(Integer id) {
        ordersMapper.deleteById(id);
    }

    /**
     * 批量删除
     */
    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            ordersMapper.deleteById(id);
        }
    }

    /**
     * 修改
     */
    public void updateById(Orders orders) {
        ordersMapper.updateById(orders);
    }

    /**
     * 根据ID查询
     */
    public Orders selectById(Integer id) {
        return ordersMapper.selectById(id);
    }

    /**
     * 查询所有
     */
    public List<Orders> selectAll(Orders orders) {
        return ordersMapper.selectAll(orders);
    }

    /**
     * 分页查询
     */
    public PageInfo<Orders> selectPage(Orders orders, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Orders> list = ordersMapper.selectAll(orders);
        return PageInfo.of(list);
    }

}