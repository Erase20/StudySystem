package com.example.controller;

import com.example.common.Result;
import com.example.entity.Note;
import com.example.service.NoteService;
import com.example.utils.TokenUtils;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;

@RestController
@RequestMapping("/note")
public class NoteController {

    @Resource
    private NoteService noteService;

    @PostMapping("/add")
    public Result add(@RequestBody Note note) {
        note.setUserId(TokenUtils.getCurrentUser().getId());
        noteService.add(note);
        return Result.success();
    }

    @PutMapping("/update")
    public Result update(@RequestBody Note note) {
        noteService.update(note);
        return Result.success();
    }

    @DeleteMapping("/delete/{id}")
    public Result delete(@PathVariable Integer id) {
        noteService.deleteById(id);
        return Result.success();
    }

    @GetMapping("/selectById/{id}")
    public Result selectById(@PathVariable Integer id) {
        return Result.success(noteService.selectById(id));
    }

    @GetMapping("/selectByUser")
    public Result selectByUser() {
        Integer userId = TokenUtils.getCurrentUser().getId();
        List<Note> list = noteService.selectByUserId(userId);
        return Result.success(list);
    }

    @GetMapping("/selectByCourse/{courseId}")
    public Result selectByCourse(@PathVariable Integer courseId) {
        List<Note> list = noteService.selectByCourseId(courseId);
        return Result.success(list);
    }
}
