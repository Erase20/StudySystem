package com.example.common;

import com.example.common.enums.ResultCodeEnum;


/**
 * 统一API响应结果封装类
 * 作用：规范所有接口的返回格式，包含状态码、提示信息、业务数据三部分
 * 前端根据code判断请求是否成功，根据data获取具体数据
 */
public class Result {
    private String code;    // 状态码，如"200"表示成功，"401"表示未登录，"500"表示系统错误
    private String msg;     // 提示信息，如"操作成功"、"用户名已存在"
    private Object data;    // 业务数据，可以是任意类型（对象、列表、Map等）

    /**
     * 私有构造方法，传入数据对象
     * 使用私有构造强制通过静态方法创建实例，保证代码规范性
     */
    private Result(Object data) {
        this.data = data;
    }

    /**
     * 无参构造方法
     */
    public Result() {
    }

    /**
     * 成功响应（无数据）
     * 用于新增、删除、修改等不需要返回数据的场景
     * 示例：return Result.success();
     */
    public static Result success() {
        Result tResult = new Result();
        tResult.setCode(ResultCodeEnum.SUCCESS.code);   // 从枚举获取成功状态码"200"
        tResult.setMsg(ResultCodeEnum.SUCCESS.msg);     // 从枚举获取成功提示"操作成功"
        return tResult;
    }

    /**
     * 成功响应（带数据）
     * 用于查询场景，需要返回具体数据
     * 示例：return Result.success(userList);
     */
    public static Result success(Object data) {
        Result tResult = new Result (data);             // 将查询结果封装到data字段
        tResult.setCode(ResultCodeEnum.SUCCESS.code);
        tResult.setMsg(ResultCodeEnum.SUCCESS.msg);
        return tResult;
    }

    /**
     * 错误响应（默认系统错误）
     * 用于捕获未知异常时的通用错误返回
     */
    public static Result error() {
        Result tResult = new Result();
        tResult.setCode(ResultCodeEnum.SYSTEM_ERROR.code);  // 系统错误码"500"
        tResult.setMsg(ResultCodeEnum.SYSTEM_ERROR.msg);    // "系统错误"
        return tResult;
    }

    /**
     * 错误响应（自定义状态码和消息）
     * 用于业务校验失败，需要返回特定错误信息
     * 示例：return Result.error("400", "用户名不能为空");
     */
    public static Result error(String code, String msg) {
        Result tResult = new Result();
        tResult.setCode(code);
        tResult.setMsg(msg);
        return tResult;
    }

    /**
     * 错误响应（使用预定义的错误枚举）
     * 推荐方式，统一维护所有错误码
     * 示例：return Result.error(ResultCodeEnum.USER_EXIST_ERROR);
     */
    public static Result error(ResultCodeEnum resultCodeEnum) {
        Result tResult = new Result();
        tResult.setCode(resultCodeEnum.code);
        tResult.setMsg(resultCodeEnum.msg);
        return tResult;
    }

    // ==================== Getter/Setter 方法 ====================
    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getMsg() {
        return msg;
    }

    public void setMsg(String msg) {
        this.msg = msg;
    }

    public Object getData() {
        return data;
    }

    public void setData(Object data) {
        this.data = data;
    }
}
