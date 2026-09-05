package com.example.controller;

import com.example.common.Result;
import com.example.entity.Chapter;
import com.example.mapper.ChapterMapper;
import com.example.service.ChapterGenerateService;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;

/**
 * 课程章节前端操作接口
 */
@RestController
@RequestMapping("/chapter")
public class ChapterController {

    @Resource
    private ChapterMapper chapterMapper;

    @Resource
    private ChapterGenerateService chapterGenerateService;

    /**
     * 新增章节
     */
    @PostMapping("/add")
    public Result add(@RequestBody Chapter chapter) {
        chapterMapper.insert(chapter);
        return Result.success();
    }

    /**
     * 删除章节
     */
    @DeleteMapping("/delete/{id}")
    public Result deleteById(@PathVariable Integer id) {
        chapterMapper.deleteById(id);
        return Result.success();
    }

    /**
     * 修改章节
     */
    @PutMapping("/update")
    public Result update(@RequestBody Chapter chapter) {
        chapterMapper.updateById(chapter);
        return Result.success();
    }

    /**
     * 查询所有章节
     */
    @GetMapping("/selectAll")
    public Result selectAll(Chapter chapter) {
        List<Chapter> list = chapterMapper.selectAll(chapter);
        return Result.success(list);
    }

    /**
     * 根据课程ID查询章节列表
     */
    @GetMapping("/course/{courseId}")
    public Result selectByCourseId(@PathVariable Integer courseId) {
        List<Chapter> list = chapterMapper.selectByCourseId(courseId);
        return Result.success(list);
    }

    /**
     * 批量生成课程章节（管理端用）
     */
    @PostMapping("/generate")
    public Result generateChapters() {
        int count = chapterGenerateService.generateChaptersForAllCourses();
        return Result.success("为" + count + "门课程生成了章节目录");
    }
}
