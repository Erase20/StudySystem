package com.example.controller;

import com.example.common.Result;
import com.example.entity.LearningPlan;
import com.example.service.LearningPlanService;
import com.example.utils.TokenUtils;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;

@RestController
@RequestMapping("/learningPlan")
public class LearningPlanController {

    @Resource
    private LearningPlanService learningPlanService;

    @PostMapping("/add")
    public Result add(@RequestBody LearningPlan plan) {
        plan.setUserId(TokenUtils.getCurrentUser().getId());
        learningPlanService.add(plan);
        return Result.success();
    }

    @PutMapping("/update")
    public Result update(@RequestBody LearningPlan plan) {
        learningPlanService.update(plan);
        return Result.success();
    }

    @DeleteMapping("/delete/{id}")
    public Result delete(@PathVariable Integer id) {
        learningPlanService.deleteById(id);
        return Result.success();
    }

    @GetMapping("/selectById/{id}")
    public Result selectById(@PathVariable Integer id) {
        return Result.success(learningPlanService.selectById(id));
    }

    @GetMapping("/selectByUser")
    public Result selectByUser() {
        Integer userId = TokenUtils.getCurrentUser().getId();
        List<LearningPlan> list = learningPlanService.selectByUserId(userId);
        return Result.success(list);
    }

    /**
     * 更新计划进度
     */
    @PutMapping("/updateProgress/{id}")
    public Result updateProgress(@PathVariable Integer id, @RequestParam Integer progress) {
        learningPlanService.updateProgress(id, progress);
        return Result.success();
    }
}
