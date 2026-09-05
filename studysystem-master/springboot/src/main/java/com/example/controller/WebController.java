package com.example.controller;

import cn.hutool.core.util.ObjectUtil;
import cn.hutool.core.util.StrUtil;
import com.example.common.Result;
import com.example.common.enums.ResultCodeEnum;
import com.example.common.enums.RoleEnum;
import com.example.entity.*;
import com.example.exception.CustomException;
import com.example.service.*;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.management.relation.Role;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 基础前端接口
 */
@RestController
public class WebController {

    @Resource
    private AdminService adminService;

    @Resource
    private UserService userService;

    @Resource
    private CourseService courseService;

    @Resource
    private ScoreService scoreService;

    @Resource
    private InformationService informationService;

    @GetMapping("/")
    public Result hello() {
        return Result.success("访问成功");
    }

    /**
     * 登录
     */
    @PostMapping("/login")
    public Result login(@RequestBody Account account) {
        if (ObjectUtil.isEmpty(account.getUsername()) || ObjectUtil.isEmpty(account.getPassword())
                || ObjectUtil.isEmpty(account.getRole())) {
            return Result.error(ResultCodeEnum.PARAM_LOST_ERROR);
        }
        if (RoleEnum.ADMIN.name().equals(account.getRole())) {
            try {
                account = adminService.login(account);
            } catch (CustomException e) {
                // 演示用户: admin表查不到时回退到user表查
                account = userService.login(account);
            }
        } else if (RoleEnum.USER.name().equals(account.getRole())){
            account = userService.login(account);
        } else {
            return Result.error(ResultCodeEnum.PARAM_ERROR);
        }
        return Result.success(account);
    }

    /**
     * 注册
     */
    @PostMapping("/register")
    public Result register(@RequestBody Account account) {
        if (StrUtil.isBlank(account.getUsername()) || StrUtil.isBlank(account.getPassword())
                || ObjectUtil.isEmpty(account.getRole())) {
            return Result.error(ResultCodeEnum.PARAM_LOST_ERROR);
        }
//        if (RoleEnum.ADMIN.name().equals(account.getRole())) {
//            adminService.register(account);
//        }
        if (RoleEnum.USER.name().equals(account.getRole())){
            userService.register(account);
        }
        return Result.success();
    }

    /**
     * 修改密码
     */
    @PutMapping("/updatePassword")
    public Result updatePassword(@RequestBody Account account) {
        if (StrUtil.isBlank(account.getUsername()) || StrUtil.isBlank(account.getPassword())
                || ObjectUtil.isEmpty(account.getNewPassword())) {
            return Result.error(ResultCodeEnum.PARAM_LOST_ERROR);
        }
        if (RoleEnum.ADMIN.name().equals(account.getRole())) {
            adminService.updatePassword(account);
        }
        if (RoleEnum.USER.name().equals(account.getRole())){
            userService.updatePassword(account);
        }
        return Result.success();
    }

    @GetMapping("getBar")
    public Result getBar(){
        Map<String , Object> resultMap = new HashMap<>();
        List<String> xList = new ArrayList<>();
        List<Long> yList = new ArrayList<>();

        xList.add("视频课程");
        xList.add("积分兑换课程");
        xList.add("下载资源");

        List<Course> courses = courseService.selectAll(new Course());
        yList.add((long) courses.size());
        // yList.add(courses.stream().filter(x -> "TEXT".equals(x.getType())).count());  // 图文课程已下线

        yList.add((long) scoreService.selectAll(new Score()).size());
        yList.add((long) informationService.selectAll(new Information()).size());


        resultMap.put("text" , "平台所有资料总数统计(柱状图)");
        resultMap.put("subText" , "统计维度：资料类型");
        resultMap.put("xAxis",xList);
        resultMap.put("yAxis",yList);

        return Result.success(resultMap);
    }

}
