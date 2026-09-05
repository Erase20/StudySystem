package com.example.service;


import cn.hutool.core.util.ObjectUtil;
import com.example.common.Constants;
import com.example.common.enums.MemberEnum;
import com.example.common.enums.ResultCodeEnum;
import com.example.common.enums.RoleEnum;
import com.example.entity.Account;
import com.example.entity.User;
import com.example.exception.CustomException;
import com.example.mapper.UserMapper;
import com.example.utils.TokenUtils;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.List;

/**
 * 用户业务逻辑层
 * 作用：处理用户相关的业务逻辑，协调Controller和Mapper层
 * @Service: 标记为Spring服务层组件，会被自动扫描注入
 */
@Service
public class UserService {

    /**
     * 注入UserMapper，用于数据库操作
     * @Resource: JDK提供的注入注解，按名称注入；也可用@Autowired按类型注入
     */
    @Resource
    private UserMapper userMapper;

    /**
     * 新增用户（注册）
     * 业务逻辑：
     * 1. 校验用户名是否已存在
     * 2. 设置默认值（密码、昵称、会员状态、角色）
     * 3. 保存到数据库
     * @param user 用户信息
     * @throws CustomException 用户名已存在时抛出
     */
    public void add(User user) {
        // 1. 判断数据库是否已有该用户名
        User dbUser = userMapper.selectByUserName(user.getUsername());
        if (ObjectUtil.isNotEmpty(dbUser)){
            // 抛出业务异常，由全局异常处理器捕获并返回错误信息
            throw new CustomException(ResultCodeEnum.USER_EXIST_ERROR); // 错误码："用户名已存在"
        }
        
        // 2. 初始化默认信息
        // 密码为空则使用默认密码"123456"
        if (ObjectUtil.isEmpty(user.getPassword())){
            user.setPassword(Constants.USER_DEFAULT_PASSWORD);
        }
        // 昵称为空则使用用户名作为昵称
        if (ObjectUtil.isEmpty(user.getName())){
            user.setName(user.getUsername());
        }
        // 默认非会员
        user.setMember(MemberEnum.NO.info);     // "否"
        // 默认角色为普通用户
        user.setRole(RoleEnum.USER.name());     // "USER"

        // 3. 插入数据库
        userMapper.insert(user);
    }


    /**
     * 根据ID删除用户
     */
    public void deleteById(Integer id) {
        userMapper.deleteById(id);
    }

    /**
     * 批量删除用户
     * 实现方式：循环调用单条删除（生产环境建议用SQL的IN语句批量删除提高效率）
     * @param ids 用户ID列表
     */
    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            userMapper.deleteById(id);
        }
    }

    /**
     * 修改用户信息
     */
    public void updateById(User user) {
        userMapper.updateById(user);
    }

    /**
     * 根据ID查询用户详情
     * 特殊处理：生成JWT token并设置到用户对象中
     * @param id 用户ID
     * @return 包含token的用户对象
     */
    public User selectById(Integer id) {
        User user = userMapper.selectById(id);
        // 生成JWT token：格式为 "用户ID-角色"
        String tokenData = user.getId() + "-" + RoleEnum.USER.name();
        // 使用用户密码作为密钥创建token，2小时过期
        String token = TokenUtils.createToken(tokenData, user.getPassword());
        user.setToken(token);   // 将token设置到用户对象返回给前端
        return user;
    }

    /**
     * 查询所有用户（支持条件筛选）
     * @param user 查询条件对象，包含用户名、角色等字段
     * @return 用户列表
     */
    public List<User> selectAll(User user) {
        return userMapper.selectAll(user);
    }

    /**
     * 分页查询用户
     * 使用PageHelper插件实现分页
     * @param user 查询条件
     * @param pageNum 当前页码（从1开始）
     * @param pageSize 每页条数
     * @return PageInfo对象，包含列表数据和分页信息（总条数、总页数等）
     */
    public PageInfo<User> selectPage(User user, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);    // 开启分页，自动对下一次查询进行分页
        List<User> list = userMapper.selectAll(user);   // 执行查询
        return PageInfo.of(list);   // 包装分页结果
    }

    /**
     * 用户登录
     * 业务逻辑：
     * 1. 根据用户名查询用户
     * 2. 校验用户是否存在
     * 3. 校验密码是否正确
     * 4. 生成JWT token返回
     * @param account 登录账号信息（用户名、密码）
     * @return 包含token的用户信息
     * @throws CustomException 用户不存在或密码错误时抛出
     */
    public Account login(Account account) {
        // 1. 查询用户
        Account dbUser = userMapper.selectByUserName(account.getUsername());
        // 2. 校验用户是否存在
        if (ObjectUtil.isNull(dbUser)) {
            throw new CustomException(ResultCodeEnum.USER_NOT_EXIST_ERROR); // "用户不存在"
        }
        // 3. 校验密码（明文比较，生产环境应使用加密比较）
        if (!account.getPassword().equals(dbUser.getPassword())) {
            throw new CustomException(ResultCodeEnum.USER_ACCOUNT_ERROR);   // "账号或密码错误"
        }
        // 4. 生成token
        String tokenData = dbUser.getId() + "-" + RoleEnum.USER.name();
        String token = TokenUtils.createToken(tokenData, dbUser.getPassword());
        dbUser.setToken(token);
        return dbUser;
    }

    /**
     * 用户注册
     * 实现：将Account对象属性复制到User对象，调用add方法
     * @param account 注册信息
     */
    public void register(Account account) {
        User user = new User();
        BeanUtils.copyProperties(account, user);    // Spring提供的属性拷贝工具
        add(user);
    }

    /**
     * 修改密码
     * 业务逻辑：
     * 1. 查询用户
     * 2. 校验原密码是否正确
     * 3. 更新为新密码
     * @param account 包含用户名、原密码、新密码
     */
    public void updatePassword(Account account) {
        User dbUser = userMapper.selectByUserName(account.getUsername());
        if (ObjectUtil.isNull(dbUser)) {
            throw new CustomException(ResultCodeEnum.USER_NOT_EXIST_ERROR);
        }
        // 校验原密码
        if (!account.getPassword().equals(dbUser.getPassword())) {
            throw new CustomException(ResultCodeEnum.PARAM_PASSWORD_ERROR); // "原密码错误"
        }
        dbUser.setPassword(account.getNewPassword());
        userMapper.updateById(dbUser);
    }

    /**
     * 账户充值
     * 业务逻辑：
     * 1. 获取当前登录用户
     * 2. 增加账户余额
     * 3. 一次性充值满500自动升级为会员
     * @param account 充值金额
     */
    public void recharge(Double account) {
        // 从token中获取当前登录用户
        Account currentUser = TokenUtils.getCurrentUser();
        User user = userMapper.selectById(currentUser.getId());
        
        // 增加余额
        user.setAccount(user.getAccount() + account);
        
        // 一次性充值满500自动成为会员
        if (account >= 500){
            user.setMember(MemberEnum.YES.info);    // "是"
        }
        
        userMapper.updateById(user);
    }
}
