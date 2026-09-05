package com.example.service;

import cn.hutool.core.date.DateUtil;
import cn.hutool.core.util.ObjectUtil;
import com.example.entity.Course;
import com.example.entity.LearningRecord;
import com.example.mapper.CourseMapper;
import com.example.mapper.LearningRecordMapper;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.Date;
import java.util.List;

@Service
public class LearningRecordService {

    @Resource
    private LearningRecordMapper learningRecordMapper;

    @Resource
    private CourseMapper courseMapper;

    public void add(LearningRecord record) {
        record.setCreateTime(DateUtil.now());
        record.setUpdateTime(DateUtil.now());
        learningRecordMapper.insert(record);
    }

    public void update(LearningRecord record) {
        record.setUpdateTime(DateUtil.now());
        learningRecordMapper.updateById(record);
    }

    public void deleteById(Integer id) {
        learningRecordMapper.deleteById(id);
    }

    public LearningRecord selectById(Integer id) {
        return learningRecordMapper.selectById(id);
    }

    public List<LearningRecord> selectByUserId(Integer userId) {
        return learningRecordMapper.selectByUserId(userId);
    }

    /**
     * 记录学习进度（如果已存在则更新）
     */
    public void recordLearning(Integer userId, Integer courseId, Integer duration, Integer progress, String lastPosition) {
        LearningRecord record = learningRecordMapper.selectByUserAndCourse(userId, courseId);
        Course course = courseMapper.selectById(courseId);
        
        if (record == null) {
            // 新增学习记录
            record = new LearningRecord();
            record.setUserId(userId);
            record.setCourseId(courseId);
            record.setCourseName(course != null ? course.getName() : null);
            record.setCourseType(course != null ? course.getType() : null);
            record.setDuration(duration);
            record.setProgress(progress);
            record.setLastPosition(lastPosition);
            record.setCreateTime(DateUtil.now());
            record.setUpdateTime(DateUtil.now());
            learningRecordMapper.insert(record);
        } else {
            // 更新学习记录
            record.setDuration(record.getDuration() + duration);
            record.setProgress(progress);
            record.setLastPosition(lastPosition);
            record.setUpdateTime(DateUtil.now());
            learningRecordMapper.updateById(record);
        }
    }

    /**
     * 获取用户总学习时长
     */
    public Integer getTotalDuration(Integer userId) {
        List<LearningRecord> records = learningRecordMapper.selectByUserId(userId);
        return records.stream().mapToInt(r -> r.getDuration() != null ? r.getDuration() : 0).sum();
    }
}
