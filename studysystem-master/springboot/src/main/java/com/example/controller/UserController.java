  package com.example.controller;


import cn.hutool.core.util.ObjectUtil;
import com.example.common.Result;
import com.example.entity.User;
import com.example.service.UserService;
import com.github.pagehelper.PageInfo;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 用户控制器 - 处理用户相关的HTTP请求
 * 路径前缀：/user
 * 
 * @RestController: 组合注解 = @Controller(标记为控制器) + @ResponseBody(返回JSON格式)
 * @RequestMapping("/user"): 设置该控制器的基础请求路径
 */
@RestController
@RequestMapping("/user")
public class UserController {

    /**
     * 注入UserService，处理业务逻辑
     */
    @Resource
    private UserService userService;

    /**
     * 新增用户
     * @PostMapping: 处理POST请求，用于创建资源
     * @RequestBody: 将请求体中的JSON数据自动转换为User对象
     * 请求示例：POST /user/add
     * 请求体：{"username":"zhangsan","password":"123456","name":"张三"}
     */
    @PostMapping("/add")
    public Result add(@RequestBody User user){
        userService.add(user);      // 调用Service层处理业务
        return Result.success();    // 返回统一响应格式
    }

    /**
     * 根据ID删除用户
     * @DeleteMapping: 处理DELETE请求，用于删除资源
     * @PathVariable: 从URL路径中获取参数值
     * 请求示例：DELETE /user/delete/1
     */
    @DeleteMapping("/delete/{id}")
    public Result deleteById(@PathVariable Integer id) {
        userService.deleteById(id);
        return Result.success();
    }

    /**
     * 批量删除用户
     * @RequestBody: 接收JSON数组，如 [1, 2, 3]
     * 请求示例：DELETE /user/delete/batch
     * 请求体：[1, 2, 3]
     */
    @DeleteMapping("/delete/batch")
    public Result deleteBatch(@RequestBody List<Integer> ids) {
        userService.deleteBatch(ids);
        return Result.success();
    }

    /**
     * 修改用户信息
     * @PutMapping: 处理PUT请求，用于更新资源
     * 请求示例：PUT /user/update
     * 请求体：{"id":1,"name":"新名字","phone":"13800138000"}
     */
    @PutMapping("/update")
    public Result updateById(@RequestBody User user) {
        userService.updateById(user);
        return Result.success();
    }

    /**
     * 根据ID查询用户详情
     * @GetMapping: 处理GET请求，用于查询资源
     * 请求示例：GET /user/selectById/1
     */
    @GetMapping("/selectById/{id}")
    public Result selectById(@PathVariable Integer id) {
        User user = userService.selectById(id);
        return Result.success(user);
    }

    /**
     * 查询所有用户（支持条件筛选）
     * 请求示例：
     *   GET /user/selectAll                    查询所有
     *   GET /user/selectAll?username=zhangsan  按用户名筛选
     *   GET /user/selectAll?role=USER          按角色筛选
     */
    @GetMapping("/selectAll")
    public Result selectAll(User user ) {
        List<User> list = userService.selectAll(user);
        return Result.success(list);
    }

    /**
     * 分页查询用户
     * @RequestParam: 从URL查询参数中获取值，defaultValue设置默认值
     * 请求示例：GET /user/selectPage?pageNum=1&pageSize=10&username=zhang
     */
    @GetMapping("/selectPage")
    public Result selectPage(User user,
                             @RequestParam(defaultValue = "1") Integer pageNum,
                             @RequestParam(defaultValue = "10") Integer pageSize) {
        PageInfo<User> page = userService.selectPage(user, pageNum, pageSize);
        return Result.success(page);
    }

    /**
     * 账户充值
     * 请求示例：GET /user/recharge?account=500
     */
    @GetMapping("/recharge")
    public Result recharge(@RequestParam Double account){
        userService.recharge(account);
        return Result.success();
    }

    /**
     * 获取会员占比饼图数据
     * 使用Java 8 Stream API进行数据统计
     * 返回ECharts饼图所需的数据格式
     */
    @GetMapping("/getPie")
    public Result getPie(){
        Map<String , Object> resultMap = new HashMap<>();
        List<Map<String , Object>> list = new ArrayList<>();

        // 1. 查询所有用户
        List<User> ordersList = userService.selectAll(new User());
        
        // 2. 使用Stream API按会员状态分组统计
        // filter: 过滤掉member为空的用户
        // groupingBy: 按member字段分组（"是"/"否"）
        // counting: 统计每组数量
        Map<String, Long> collect = ordersList.stream()
                .filter(x -> ObjectUtil.isNotEmpty(x.getMember()))
                .collect(Collectors.groupingBy(User::getMember, Collectors.counting()));

        // 3. 转换为ECharts饼图数据格式 [{name:"是",value:10},{name:"否",value:20}]
        for (String key: collect.keySet()) {
            Map<String , Object> map = new HashMap<>();
            map.put("name" , key);          // 会员状态
            map.put("value" , collect.get(key));  // 数量
            list.add(map);
        }

        // 4. 组装返回数据
        resultMap.put("text" , "平台会员用户占比统计（饼图）");
        resultMap.put("subText" , "统计维度：是否为会员身份");
        resultMap.put("name","占比统计");
        resultMap.put("data",list);
        return Result.success(resultMap);
    }

    /**
     * 积分排行榜
     * 使用Stream API实现排序和限制
     * @param limit 取前N名，默认10
     */
    @GetMapping("/scoreRank")
    public Result scoreRank(@RequestParam(defaultValue = "10") Integer limit) {
        List<User> allUsers = userService.selectAll(new User());
        
        // Stream链式操作：
        // 1. filter: 过滤积分为空或0的用户
        // 2. sorted: 按积分降序排序（b.getScore() - a.getScore()）
        // 3. limit: 只取前limit条
        // 4. map: 将User对象转换为Map（只取需要的字段）
        // 5. collect: 收集为List
        List<Map<String, Object>> rankList = allUsers.stream()
                .filter(u -> u.getScore() != null && u.getScore() > 0)
                .sorted((a, b) -> b.getScore() - a.getScore())
                .limit(limit)
                .map(u -> {
                    Map<String, Object> item = new HashMap<>();
                    item.put("id", u.getId());
                    item.put("name", u.getName());
                    item.put("avatar", u.getAvatar());
                    item.put("score", u.getScore());
                    return item;
                })
                .collect(Collectors.toList());
        return Result.success(rankList);
    }

}
