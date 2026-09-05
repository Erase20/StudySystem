package com.example.service;

import cn.hutool.core.date.DateUtil;
import com.example.entity.Account;
import com.example.entity.RechargeRecord;
import com.example.mapper.RechargeRecordMapper;
import com.example.utils.TokenUtils;
import com.github.pagehelper.PageHelper;
import com.github.pagehelper.PageInfo;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.List;

/**
 * 公告信息表业务处理
 **/
@Service
public class RechargeRecordService {

    @Resource
    private RechargeRecordMapper rechargeRecordMapper;

    /**
     * 新增
     */
    public void add(RechargeRecord rechargeRecord) {
        rechargeRecordMapper.insert(rechargeRecord);
    }

    /**
     * 删除
     */
    public void deleteById(Integer id) {
        rechargeRecordMapper.deleteById(id);
    }

    /**
     * 批量删除
     */
    public void deleteBatch(List<Integer> ids) {
        for (Integer id : ids) {
            rechargeRecordMapper.deleteById(id);
        }
    }

    /**
     * 修改
     */
    public void updateById(RechargeRecord rechargeRecord) {
        rechargeRecordMapper.updateById(rechargeRecord);
    }

    /**
     * 根据ID查询
     */
    public RechargeRecord selectById(Integer id) {
        return rechargeRecordMapper.selectById(id);
    }

    /**
     * 查询所有
     */
    public List<RechargeRecord> selectAll(RechargeRecord rechargeRecord) {
        return rechargeRecordMapper.selectAll(rechargeRecord);
    }

    /**
     * 分页查询
     */
    public PageInfo<RechargeRecord> selectPage(RechargeRecord rechargeRecord, Integer pageNum, Integer pageSize) {
        PageHelper.startPage(pageNum, pageSize);
        List<RechargeRecord> list = rechargeRecordMapper.selectAll(rechargeRecord);
        return PageInfo.of(list);
    }

}