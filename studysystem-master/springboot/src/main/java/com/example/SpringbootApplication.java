package com.example;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Spring Boot 应用启动类
 * @SpringBootApplication: 组合注解，包含@Configuration(配置类)、@EnableAutoConfiguration(自动配置)、@ComponentScan(组件扫描)
 * @MapperScan("com.example.mapper"): 扫描指定包下的MyBatis Mapper接口，自动生成代理实现类
 */
@SpringBootApplication(scanBasePackages = "com.example")
@MapperScan("com.example.mapper")
public class SpringbootApplication {

    /**
     * 应用入口方法
     * SpringApplication.run(): 启动Spring Boot应用，创建应用上下文，加载所有配置和Bean
     */
    public static void main(String[] args) {
        SpringApplication.run(SpringbootApplication.class, args);
    }

}
