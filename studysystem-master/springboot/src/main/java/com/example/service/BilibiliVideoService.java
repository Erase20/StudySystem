package com.example.service;

import com.example.entity.Course;
import com.example.mapper.CourseMapper;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.util.List;

/**
 * B站视频服务
 * 根据课程名称搜索B站视频，获取BV号并更新到课程表
 */
@Service
public class BilibiliVideoService {

    private static final Logger log = LoggerFactory.getLogger(BilibiliVideoService.class);

    @Resource
    private CourseMapper courseMapper;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * 批量更新所有课程的B站视频链接
     * 遍历所有 video 为空的课程，用课程名搜索B站，取第一个结果
     *
     * @return 更新的课程数量
     */
    public int batchUpdateVideoLinks() {
        List<Course> allCourses = courseMapper.selectAll(new Course());
        int updated = 0;

        for (Course course : allCourses) {
            // 跳过已有视频的课程
            if (course.getVideo() != null && !course.getVideo().isEmpty()) {
                continue;
            }
            // 跳过TEXT类型课程（无需视频）
            if ("TEXT".equals(course.getType())) {
                continue;
            }

            try {
                String bvid = searchBilibiliVideo(course.getName());
                if (bvid != null) {
                    String embedUrl = "https://player.bilibili.com/player.html?bvid=" + bvid + "&high_quality=1&danmaku=0";
                    course.setVideo(embedUrl);
                    courseMapper.updateById(course);
                    updated++;
                    log.info("更新课程视频: id={}, name={}, bvid={}", course.getId(), course.getName(), bvid);
                } else {
                    log.warn("未找到视频: id={}, name={}", course.getId(), course.getName());
                }
                // 间隔1秒，避免触发B站反爬
                Thread.sleep(1000);
            } catch (Exception e) {
                log.error("更新课程视频失败: id={}, name={}, error={}", course.getId(), course.getName(), e.getMessage());
            }
        }

        return updated;
    }

    /**
     * 通过B站搜索API根据关键词查找视频BV号
     *
     * @param keyword 搜索关键词（课程名）
     * @return BV号，如 "BV1xx411c7mD"，未找到返回 null
     */
    public String searchBilibiliVideo(String keyword) {
        HttpURLConnection connection = null;
        try {
            String encodedKeyword = URLEncoder.encode(keyword, "UTF-8");
            String urlStr = "https://api.bilibili.com/x/web-interface/search/type?keyword=" + encodedKeyword + "&search_type=video&page=1&page_size=3";

            URL url = new URL(urlStr);
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setConnectTimeout(5000);
            connection.setReadTimeout(10000);
            connection.setRequestProperty("User-Agent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36");
            connection.setRequestProperty("Referer", "https://www.bilibili.com/");
            connection.setRequestProperty("Accept", "application/json");

            int responseCode = connection.getResponseCode();
            if (responseCode != 200) {
                log.warn("B站搜索API返回非200状态: {}", responseCode);
                return null;
            }

            BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream(), "UTF-8"));
            StringBuilder response = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                response.append(line);
            }
            reader.close();

            JsonNode root = objectMapper.readTree(response.toString());
            int code = root.path("code").asInt(-1);
            if (code != 0) {
                log.warn("B站搜索API返回错误: code={}, message={}", code, root.path("message").asText());
                return null;
            }

            JsonNode results = root.path("data").path("result");
            if (results.isArray() && results.size() > 0) {
                // 取第一个搜索结果的bvid
                return results.get(0).path("bvid").asText(null);
            }

            return null;
        } catch (Exception e) {
            log.error("搜索B站视频失败: keyword={}, error={}", keyword, e.getMessage());
            return null;
        } finally {
            if (connection != null) {
                connection.disconnect();
            }
        }
    }
}
