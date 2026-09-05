package com.example.controller;

import com.example.common.Result;
import com.example.entity.LearningRecord;
import com.example.service.LearningRecordService;
import com.example.utils.TokenUtils;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/learningRecord")
public class LearningRecordController {

    @Resource
    private LearningRecordService learningRecordService;

    @PostMapping("/add")
    public Result add(@RequestBody LearningRecord record) {
        learningRecordService.add(record);
        return Result.success();
    }

    @PutMapping("/update")
    public Result update(@RequestBody LearningRecord record) {
        learningRecordService.update(record);
        return Result.success();
    }

    @DeleteMapping("/delete/{id}")
    public Result delete(@PathVariable Integer id) {
        learningRecordService.deleteById(id);
        return Result.success();
    }

    @GetMapping("/selectById/{id}")
    public Result selectById(@PathVariable Integer id) {
        return Result.success(learningRecordService.selectById(id));
    }

    @GetMapping("/selectByUser")
    public Result selectByUser() {
        Integer userId = TokenUtils.getCurrentUser().getId();
        List<LearningRecord> list = learningRecordService.selectByUserId(userId);
        return Result.success(list);
    }

    /**
     * 记录学习进度
     */
    @PostMapping("/record")
    public Result record(@RequestBody LearningRecord record) {
        Integer userId = TokenUtils.getCurrentUser().getId();
        learningRecordService.recordLearning(
            userId, 
            record.getCourseId(), 
            record.getDuration(), 
            record.getProgress(), 
            record.getLastPosition()
        );
        return Result.success();
    }

    /**
     * 获取学习统计
     */
    @GetMapping("/statistics")
    public Result statistics() {
        Integer userId = TokenUtils.getCurrentUser().getId();
        List<LearningRecord> records = learningRecordService.selectByUserId(userId);
        Integer totalDuration = learningRecordService.getTotalDuration(userId);
        
        Map<String, Object> data = new HashMap<>();
        data.put("totalCourses", records.size());
        data.put("totalDuration", totalDuration);
        data.put("records", records);
        return Result.success(data);
    }
}
