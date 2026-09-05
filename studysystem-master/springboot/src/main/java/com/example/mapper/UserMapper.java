package com.example.mapper;

import com.example.entity.User;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/**
 * 用户数据访问层（DAO层）
 * 作用：定义数据库操作方法，MyBatis会自动生成实现类
 * 对应XML文件：resources/mapper/UserMapper.xml
 */
public interface UserMapper {

    /**
     * 根据用户名查询用户
     * @Select注解：直接在接口上写SQL，简单查询推荐用注解方式
     * #{username}: 预编译参数，防止SQL注入攻击
     * 用途：登录验证、注册时检查用户名是否已存在
     */
    @Select("select * from user where username = #{username}")
    User selectByUserName(String username);

    /**
     * 新增用户
     * 对应XML中的<insert>标签
     * @param user 用户实体对象
     * @return 影响的行数，成功返回1
     */
    int insert(User user);

    /**
     * 根据ID删除用户
     * 对应XML中的<delete>标签
     * @param id 用户ID
     * @return 影响的行数
     */
    int deleteById(Integer id);

    /**
     * 根据ID修改用户信息
     * 对应XML中的<update>标签
     * @param user 包含更新数据的实体对象
     * @return 影响的行数
     */
    int updateById(User user);

    /**
     * 根据ID查询用户详情
     * 对应XML中的<select>标签
     * @param id 用户ID
     * @return 用户实体对象，不存在返回null
     */
    User selectById(Integer id);

    /**
     * 条件查询所有用户
     * 对应XML中的<select>标签，支持动态SQL条件
     * @param user 查询条件（可为空），包含用户名、角色等筛选条件
     * @return 用户列表
     */
    List<User> selectAll(User user);

}
