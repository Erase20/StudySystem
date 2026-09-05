package com.example.service;

import cn.hutool.core.date.DateUtil;
import com.example.entity.Course;
import com.example.entity.Note;
import com.example.mapper.CourseMapper;
import com.example.mapper.NoteMapper;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.Date;
import java.util.List;

@Service
public class NoteService {

    @Resource
    private NoteMapper noteMapper;

    @Resource
    private CourseMapper courseMapper;

    public void add(Note note) {
        // 补充课程名称
        if (note.getCourseId() != null) {
            Course course = courseMapper.selectById(note.getCourseId());
            if (course != null) {
                note.setCourseName(course.getName());
            }
        }
        note.setCreateTime(DateUtil.format(new Date(), "yyyy-MM-dd HH:mm:ss"));
        note.setUpdateTime(note.getCreateTime());
        noteMapper.insert(note);
    }

    public void update(Note note) {
        note.setUpdateTime(DateUtil.format(new Date(), "yyyy-MM-dd HH:mm:ss"));
        noteMapper.updateById(note);
    }

    public void deleteById(Integer id) {
        noteMapper.deleteById(id);
    }

    public Note selectById(Integer id) {
        return noteMapper.selectById(id);
    }

    public List<Note> selectByUserId(Integer userId) {
        return noteMapper.selectByUserId(userId);
    }

    public List<Note> selectByCourseId(Integer courseId) {
        return noteMapper.selectByCourseId(courseId);
    }
}
