package com.example.mapper;

import com.example.entity.Note;
import org.apache.ibatis.annotations.Select;

import java.util.List;

public interface NoteMapper {

    int insert(Note note);

    int deleteById(Integer id);

    int updateById(Note note);

    Note selectById(Integer id);

    List<Note> selectAll(Note note);

    @Select("select note.*, user.name as userName from note left join user on note.user_id = user.id where note.user_id = #{userId} order by create_time desc")
    List<Note> selectByUserId(Integer userId);

    @Select("select note.*, user.name as userName from note left join user on note.user_id = user.id where note.course_id = #{courseId} order by create_time desc")
    List<Note> selectByCourseId(Integer courseId);
}
