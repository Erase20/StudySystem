package com.example.utils;

import cn.hutool.core.date.DateUtil;
import cn.hutool.core.util.ObjectUtil;
import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.example.common.Constants;
import com.example.common.enums.RoleEnum;
import com.example.entity.Account;
import com.example.service.AdminService;
import com.example.service.UserService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import javax.annotation.PostConstruct;
import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.util.Date;

/**
 * JWT Token工具类
 * 作用：生成和解析JWT令牌，实现用户身份认证
 * 
 * JWT（JSON Web Token）结构：Header.Payload.Signature
 * - Header: 算法类型（HS256）
 * - Payload: 携带的数据（用户ID、角色、过期时间）
 * - Signature: 签名，用于验证token未被篡改
 */
@Component  // 标记为Spring组件，会被自动扫描
public class TokenUtils {

    // 日志记录器，用于记录错误信息
    private static final Logger log = LoggerFactory.getLogger(TokenUtils.class);

    // ==================== 静态Service引用（用于静态方法中调用）====================
    
    // 静态变量保存Service实例，供静态方法使用
    private static AdminService staticAdminService;
    private static UserService staticUserService;

    // 非静态变量用于依赖注入
    @Resource
    AdminService adminService;

    @Resource
    UserService userService;

    /**
     * @PostConstruct: 在依赖注入完成后执行的方法
     * 作用：将注入的Service赋值给静态变量，使静态方法可以使用
     * 原因：静态方法无法直接访问非静态成员，需要通过这种方式间接获取
     */
    @PostConstruct
    public void setUserService() {
        staticAdminService = adminService;
        staticUserService = userService;
    }

    /**
     * 生成JWT Token
     * 
     * @param data 载荷数据，格式："用户ID-角色"，如 "1-USER"
     * @param sign 签名密钥，这里使用用户密码作为密钥（每个用户的token密钥不同）
     * @return 生成的JWT字符串
     * 
     * 生成过程：
     * 1. withAudience(data): 设置载荷（用户ID和角色）
     * 2. withExpiresAt(...): 设置过期时间（当前时间+2小时）
     * 3. sign(...): 使用HMAC256算法和密钥签名
     */
    public static String createToken(String data, String sign) {
        return JWT.create()
                .withAudience(data)                                 // 将 userId-role 保存到token载荷中
                .withExpiresAt(DateUtil.offsetHour(new Date(), 2))  // 2小时后token过期
                .sign(Algorithm.HMAC256(sign));                     // 使用密码作为密钥进行HMAC256签名
    }

    /**
     * 从当前请求中获取登录用户信息
     * 
     * 使用场景：需要获取当前登录用户ID、角色等信息的接口
     * 实现原理：
     * 1. 从请求头中获取token
     * 2. 解析token获取用户ID和角色
     * 3. 根据角色查询对应的用户信息
     * 
     * @return Account对象（包含用户基本信息），未登录或token无效返回空对象
     */
    public static Account getCurrentUser() {
        try {
            // 1. 获取当前HTTP请求对象
            // RequestContextHolder: Spring提供的请求上下文持有者
            // ServletRequestAttributes: 包含HttpServletRequest和HttpServletResponse
            HttpServletRequest request = ((ServletRequestAttributes) 
                    RequestContextHolder.getRequestAttributes()).getRequest();
            
            // 2. 从请求头中获取token
            String token = request.getHeader(Constants.TOKEN);
            
            // 3. 解析token
            if (ObjectUtil.isNotEmpty(token)) {
                // JWT.decode(): 解码token（不验证签名，仅解析内容）
                // getAudience(): 获取载荷中的audience列表（createToken时设置的data）
                String userRole = JWT.decode(token).getAudience().get(0);
                
                // 4. 分割字符串获取用户ID和角色
                String userId = userRole.split("-")[0];   // 获取用户id
                String role = userRole.split("-")[1];     // 获取角色（ADMIN/USER）
                
                // 5. 根据角色查询对应的用户信息
                if (RoleEnum.ADMIN.name().equals(role)) {
                    return staticAdminService.selectById(Integer.valueOf(userId));
                }
                if (RoleEnum.USER.name().equals(role)){
                    return staticUserService.selectById(Integer.valueOf(userId));
                }
            }
        } catch (Exception e) {
            // 记录错误日志，如token格式错误、解析失败等
            log.error("获取当前用户信息出错", e);
        }
        // 返回空对象而非null，避免调用方出现空指针异常
        return new Account();
    }
}

