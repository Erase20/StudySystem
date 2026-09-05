package com.example.common.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import javax.annotation.Resource;

@Configuration
public class WebConfig implements  WebMvcConfigurer {

    @Resource
    private JwtInterceptor jwtInterceptor;

    // 加自定义拦截器JwtInterceptor，设置拦截规则
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(jwtInterceptor).addPathPatterns("/**")
                .excludePathPatterns("/")
                .excludePathPatterns("/login")
                .excludePathPatterns("/register")
                .excludePathPatterns("/files/**")
                .excludePathPatterns("/proxy/**")           // 图片代理接口
                .excludePathPatterns("/course/recommend")      // 协同过滤推荐接口
                .excludePathPatterns("/course/hot")            // 热门课程接口
                .excludePathPatterns("/course/getRecommend")   // 课程推荐
                .excludePathPatterns("/course/selectTop8")     // 课程列表
                .excludePathPatterns("/course/selectAll")      // 所有课程
                .excludePathPatterns("/course/selectById/**")  // 课程详情
                .excludePathPatterns("/course/updateVideoLinks") // 批量更新视频链接
                .excludePathPatterns("/score/getRecommend")    // 积分商品推荐
                .excludePathPatterns("/score/getTop8")         // 积分商品列表
                .excludePathPatterns("/score/selectAll")       // 所有积分商品
                .excludePathPatterns("/information/getRecommend")  // 资料推荐
                .excludePathPatterns("/information/selectTop8")    // 资料列表
                .excludePathPatterns("/information/selectAll")     // 所有资料
                .excludePathPatterns("/information/selectById/**") // 资料详情
                .excludePathPatterns("/notice/selectAll")     // 公告列表
                .excludePathPatterns("/user/scoreRank")      // 积分排行榜
                .excludePathPatterns("/chapter/course/**")    // 课程章节列表
                .excludePathPatterns("/chapter/selectAll");   // 章节查询
    }
}