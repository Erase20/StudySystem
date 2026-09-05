package com.example.utils;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * 日期时间工具类
 * 提供统一的日期解析方法，消除各 Service 中的重复代码
 */
public class DateUtils {

    private static final DateTimeFormatter DATETIME_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd");

    /**
     * 解析日期时间字符串，支持 "yyyy-MM-dd HH:mm:ss" 和 "yyyy-MM-dd" 两种格式
     *
     * @param timeStr 日期字符串
     * @return LocalDateTime，解析失败返回 null
     */
    public static LocalDateTime parseDateTime(String timeStr) {
        if (timeStr == null || timeStr.isEmpty()) {
            return null;
        }
        try {
            if (timeStr.contains(":")) {
                return LocalDateTime.parse(timeStr, DATETIME_FORMATTER);
            } else {
                return LocalDate.parse(timeStr, DATE_FORMATTER).atStartOfDay();
            }
        } catch (Exception e) {
            return null;
        }
    }
}
