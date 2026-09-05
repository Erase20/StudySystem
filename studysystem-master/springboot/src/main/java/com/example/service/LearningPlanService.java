package com.example.service;

import cn.hutool.core.date.DateUtil;
import com.example.entity.LearningPlan;
import com.example.mapper.LearningPlanMapper;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.Date;
import java.util.List;

@Service
public class LearningPlanService {

    @Resource
    private LearningPlanMapper learningPlanMapper;

    public void add(LearningPlan plan) {
        plan.setCreateTime(DateUtil.format(new Date(), "yyyy-MM-dd HH:mm:ss"));
        plan.setUpdateTime(plan.getCreateTime());
        if (plan.getStatus() == null) {
            plan.setStatus("进行中");
        }
        if (plan.getProgress() == null) {
            plan.setProgress(0);
        }
        learningPlanMapper.insert(plan);
    }

    public void update(LearningPlan plan) {
        plan.setUpdateTime(DateUtil.format(new Date(), "yyyy-MM-dd HH:mm:ss"));
        learningPlanMapper.updateById(plan);
    }

    public void deleteById(Integer id) {
        learningPlanMapper.deleteById(id);
    }

    public LearningPlan selectById(Integer id) {
        return learningPlanMapper.selectById(id);
    }

    public List<LearningPlan> selectByUserId(Integer userId) {
        return learningPlanMapper.selectByUserId(userId);
    }

    /**
     * 更新计划进度
     */
    public void updateProgress(Integer id, Integer progress) {
        LearningPlan plan = learningPlanMapper.selectById(id);
        if (plan != null) {
            plan.setProgress(progress);
            if (progress >= 100) {
                plan.setStatus("已完成");
            }
            plan.setUpdateTime(DateUtil.format(new Date(), "yyyy-MM-dd HH:mm:ss"));
            learningPlanMapper.updateById(plan);
        }
    }
}
