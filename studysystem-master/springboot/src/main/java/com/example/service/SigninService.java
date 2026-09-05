package com.example.service;

import cn.hutool.core.date.DateUtil;
import cn.hutool.core.util.ObjectUtil;
import com.example.common.enums.ResultCodeEnum;
import com.example.entity.Signin;
import com.example.entity.User;
import com.example.exception.CustomException;
import com.example.mapper.SigninMapper;
import com.example.mapper.UserMapper;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.Date;
import java.util.List;

/**
 * 签到信息信息表业务处理
 **/
@Service
public class SigninService {

    @Resource 
    private SigninMapper signinMapper;
    @Resource
    private UserMapper userMapper;

    /**
     * 新增
     */
    public void add(Signin signin) {
        //获取今日日期
        String day = DateUtil.format(new Date(), "yyyy-MM-dd");

        //判断用户是否签过到
        Signin dbSign = signinMapper.selectByUserIdAndDay(signin.getUserId(), day);
        if (ObjectUtil.isNotEmpty(dbSign)){
            throw new CustomException(ResultCodeEnum.SIGNIN_ALREADY_ERROR);
        }
        // 插入新的签到记录
        signin.setTime(DateUtil.now());
        signin.setDay(day);
        signinMapper.insert(signin);
        //签到成功领取积分
        User user = userMapper.selectById(signin.getUserId());
        user.setScore(user.getScore() + 10);
        userMapper.updateById(user);
    }

    /**
     * 删除
     */
    public void deleteById(Integer id) {
        signinMapper.deleteById(id);
    }

    /**
     * 批量删除
     */
    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            signinMapper.deleteById(id);
        }
    }

    /**
     * 修改
     */
    public void updateById(Signin signin) {
        signinMapper.updateById(signin);
    }

    /**
     * 根据ID查询
     */
    public Signin selectById(Integer id) {
        return signinMapper.selectById(id);
    }

    /**
     * 查询所有
     */
    public List<Signin> selectAll(Signin signin) {
        return signinMapper.selectAll(signin);
    }

    /**
     * 分页查询
     */
    public PageInfo<Signin> selectPage(Signin signin, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<Signin> list = signinMapper.selectAll(signin);
        return PageInfo.of(list);
    }


    public Signin selectByUserId(Integer UserId) {
        return signinMapper.selectByUserId(UserId);
    }
}