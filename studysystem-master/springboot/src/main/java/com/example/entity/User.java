package com.example.entity;

import java.io.Serializable;

/**
 * 用户实体类 - 对应数据库user表
 * 继承Account基类，实现Serializable接口支持对象序列化（用于缓存、网络传输等）
 */
public class User extends Account implements Serializable {
    /**
     * 序列化版本号
     * 作用：确保序列化和反序列化时类版本一致，避免兼容性问题
     */
    private static final long serialVersionUID = 1L;

    // ==================== 用户基本信息字段 ====================
    
    private Integer id;         // 用户ID，主键，数据库自增
    
    private String username;    // 登录账号，唯一，用于登录验证
    
    private String password;    // 登录密码，明文存储（生产环境应加密）
    
    private String name;        // 用户昵称/真实姓名，显示用
    
    private String avatar;      // 头像图片URL，存储文件访问路径
    
    private String role;        // 角色：ADMIN(管理员) / USER(普通用户)，控制权限
    
    private String phone;       // 手机号，联系方式
    
    private String email;       // 邮箱地址，可用于找回密码
    
    // ==================== 会员与积分相关字段 ====================
    
    private String member;      // 会员状态："是" / "否"，充值满500自动成为会员
    
    private Integer score;      // 积分，通过学习、签到等行为获取
    
    private Double account;     // 账户余额，可用于购买课程

    private String direction;   // 学习方向（逗号分隔，如"Java,Python,Vue"）

    @Override
    public Integer getId() {
        return id;
    }

    @Override
    public void setId(Integer id) {
        this.id = id;
    }

    @Override
    public String getUsername() {
        return username;
    }

    @Override
    public void setUsername(String username) {
        this.username = username;
    }

    @Override
    public String getPassword() {
        return password;
    }

    @Override
    public void setPassword(String password) {
        this.password = password;
    }

    @Override
    public String getName() {
        return name;
    }

    @Override
    public void setName(String name) {
        this.name = name;
    }

    @Override
    public String getAvatar() {
        return avatar;
    }

    @Override
    public void setAvatar(String avatar) {
        this.avatar = avatar;
    }

    @Override
    public String getRole() {
        return role;
    }

    @Override
    public void setRole(String role) {
        this.role = role;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getMember() {
        return member;
    }

    public void setMember(String member) {
        this.member = member;
    }

    public Integer getScore() {
        return score;
    }

    public void setScore(Integer score) {
        this.score = score;
    }

    public Double getAccount() {
        return account;
    }

    public void setAccount(Double account) {
        this.account = account;
    }

    public String getDirection() {
        return direction;
    }

    public void setDirection(String direction) {
        this.direction = direction;
    }
}