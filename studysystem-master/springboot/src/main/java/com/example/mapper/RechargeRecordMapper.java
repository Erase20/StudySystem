package com.example.mapper;

import com.example.entity.RechargeRecord;

import java.util.List;

/**
 * 操作rechargeRecord相关数据接口
*/
public interface RechargeRecordMapper {

    /**
      * 新增
    */
    int insert(RechargeRecord rechargeRecord);

    /**
      * 删除
    */
    int deleteById(Integer id);

    /**
      * 修改
    */
    int updateById(RechargeRecord rechargeRecord);

    /**
      * 根据ID查询
    */
    RechargeRecord selectById(Integer id);

    /**
      * 查询所有
    */
    List<RechargeRecord> selectAll(RechargeRecord rechargeRecord);

}