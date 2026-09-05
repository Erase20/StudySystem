package com.example.controller;

import com.example.common.Result;
import com.example.entity.RechargeRecord;
import com.example.service.RechargeRecordService;
import com.github.pagehelper.PageInfo;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;

/**
 * 公告信息表前端操作接口
 **/
@RestController
@RequestMapping("/rechargeRecord")
public class RecordController {

    @Resource
    private RechargeRecordService rechargeRecordService;

    /**
     * 新增
     */
    @PostMapping("/add")
    public Result add(@RequestBody RechargeRecord rechargeRecord) {
        rechargeRecordService.add(rechargeRecord);
        return Result.success();
    }

    /**
     * 删除
     */
    @DeleteMapping("/delete/{id}")
    public Result deleteById(@PathVariable Integer id) {
        rechargeRecordService.deleteById(id);
        return Result.success();
    }

    /**
     * 批量删除
     */
    @DeleteMapping("/delete/batch")
    public Result deleteBatch(@RequestBody List<Integer> ids) {
        rechargeRecordService.deleteBatch(ids);
        return Result.success();
    }

    /**
     * 修改
     */
    @PutMapping("/update")
    public Result updateById(@RequestBody RechargeRecord rechargeRecord) {
        rechargeRecordService.updateById(rechargeRecord);
        return Result.success();
    }

    /**
     * 根据ID查询
     */
    @GetMapping("/selectById/{id}")
    public Result selectById(@PathVariable Integer id) {
        RechargeRecord rechargeRecord = rechargeRecordService.selectById(id);
        return Result.success(rechargeRecord);
    }

    /**
     * 查询所有
     */
    @GetMapping("/selectAll")
    public Result selectAll(RechargeRecord rechargeRecord ) {
        List<RechargeRecord> list = rechargeRecordService.selectAll(rechargeRecord);
        return Result.success(list);
    }

    /**
     * 分页查询
     */
    @GetMapping("/selectPage")
    public Result selectPage(RechargeRecord rechargeRecord,
                             @RequestParam(defaultValue = "1") Integer pageNum,
                             @RequestParam(defaultValue = "10") Integer pageSize) {
        PageInfo<RechargeRecord> page = rechargeRecordService.selectPage(rechargeRecord, pageNum, pageSize);
        return Result.success(page);
    }

}