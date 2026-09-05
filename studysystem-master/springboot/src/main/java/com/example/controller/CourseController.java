package com.example.controller;

import com.example.common.Result;
import com.example.entity.Course;
import com.example.mapper.CourseMapper;
import com.example.service.CourseService;
import com.example.service.CollaborativeFilterService;
import com.example.service.BilibiliVideoService;
import com.example.utils.TokenUtils;
import com.github.pagehelper.PageInfo;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;

/**
 * 课程信息表前端操作接口
 **/
@RestController
@RequestMapping("/course")
public class CourseController {

    @Resource
    private CourseService courseService;

    @Resource
    private CollaborativeFilterService collaborativeFilterService;

    @Resource
    private CourseMapper courseMapper;

    @Resource
    private BilibiliVideoService bilibiliVideoService;

    /**
     * 新增
     */
    @PostMapping("/add")
    public Result add(@RequestBody Course course) {
        courseService.add(course);
        return Result.success();
    }

    /**
     * 删除
     */
    @DeleteMapping("/delete/{id}")
    public Result deleteById(@PathVariable Integer id) {
        courseService.deleteById(id);
        return Result.success();
    }

    /**
     * 批量删除
     */
    @DeleteMapping("/delete/batch")
    public Result deleteBatch(@RequestBody List<Integer> ids) {
        courseService.deleteBatch(ids);
        return Result.success();
    }

    /**
     * 修改
     */
    @PutMapping("/update")
    public Result updateById(@RequestBody Course course) {
        courseService.updateById(course);
        return Result.success();
    }

    /**
     * 根据ID查询
     */
    @GetMapping("/selectById/{id}")
    public Result selectById(@PathVariable Integer id) {
        Course course = courseService.selectById(id);
        return Result.success(course);
    }

    @GetMapping("/getRecommend")
    public Result getRecommend(@RequestParam(required = false) String type,
                               @RequestParam(required = false) String category){
        Course course = courseService.getRecommend(type, category);
        return Result.success(course);
    }

    /**
     * 查询所有
     */
    @GetMapping("/selectAll")
    public Result selectAll(Course course ) {
        List<Course> list = courseService.selectAll(course);
        return Result.success(list);
    }

    @GetMapping("/selectTop8")
    public Result selectTop8(@RequestParam(required = false) String type,
                             @RequestParam(required = false) String category){
        List<Course> list = courseService.selectTop8(type, category);
        return Result.success(list);
    }


    /**
     * 分页查询
     */
    @GetMapping("/selectPage")
    public Result selectPage(Course course,
                             @RequestParam(defaultValue = "1") Integer pageNum,
                             @RequestParam(defaultValue = "10") Integer pageSize) {
        PageInfo<Course> page = courseService.selectPage(course, pageNum, pageSize);
        return Result.success(page);
    }

    /**
     * 协同过滤推荐课程（未登录时返回热门课程）
     */
    @GetMapping("/recommend")
    public Result recommend(@RequestParam(defaultValue = "8") Integer limit) {
        try {
            Integer userId = TokenUtils.getCurrentUser().getId();
            List<Course> recommendCourses = collaborativeFilterService.recommendCourses(userId, limit);
            return Result.success(recommendCourses);
        } catch (Exception e) {
            // 未登录时返回热门课程
            List<Course> hotCourses = courseMapper.selectHotCourses(limit);
            return Result.success(hotCourses);
        }
    }

    /**
     * 热门课程推荐
     */
    @GetMapping("/hot")
    public Result hotCourses(@RequestParam(defaultValue = "8") Integer limit) {
        List<Course> hotCourses = courseMapper.selectHotCourses(limit);
        return Result.success(hotCourses);
    }

    /**
     * 批量更新B站视频链接
     * 根据课程名搜索B站视频，将嵌入播放链接写入video字段
     */
    @GetMapping("/updateVideoLinks")
    public Result updateVideoLinks() {
        int updated = bilibiliVideoService.batchUpdateVideoLinks();
        return Result.success("成功更新 " + updated + " 门课程的视频链接");
    }

}