package com.example.controller;

import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletResponse;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 * 图片代理接口
 * 解决外部图片（如B站）防盗链导致前端无法直接显示的问题
 * 前端通过 /proxy/image?url=xxx 请求图片，后端代理获取后返回
 */
@RestController
@RequestMapping("/proxy")
public class ProxyController {

    /**
     * 代理获取外部图片
     * @param url 外部图片URL
     * @param response HTTP响应
     */
    @GetMapping("/image")
    public void proxyImage(@RequestParam String url, HttpServletResponse response) {
        HttpURLConnection connection = null;
        InputStream inputStream = null;
        OutputStream outputStream = null;

        try {
            URL imageUrl = new URL(url);
            connection = (HttpURLConnection) imageUrl.openConnection();
            connection.setRequestMethod("GET");
            connection.setConnectTimeout(5000);
            connection.setReadTimeout(10000);
            // 伪装 Referer，绕过防盗链
            connection.setRequestProperty("Referer", extractReferer(url));
            connection.setRequestProperty("User-Agent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36");

            int responseCode = connection.getResponseCode();
            if (responseCode == 200) {
                String contentType = connection.getContentType();
                if (contentType != null) {
                    response.setContentType(contentType);
                } else {
                    response.setContentType("image/jpeg");
                }
                // 内联显示，不下载
                response.setHeader("Content-Disposition", "inline");
                // 缓存7天
                response.setHeader("Cache-Control", "max-age=604800");

                inputStream = connection.getInputStream();
                outputStream = response.getOutputStream();

                byte[] buffer = new byte[4096];
                int bytesRead;
                while ((bytesRead = inputStream.read(buffer)) != -1) {
                    outputStream.write(buffer, 0, bytesRead);
                }
                outputStream.flush();
            } else {
                response.setStatus(responseCode);
            }
        } catch (Exception e) {
            try {
                response.setStatus(500);
            } catch (Exception ignored) {}
        } finally {
            try { if (inputStream != null) inputStream.close(); } catch (Exception ignored) {}
            try { if (outputStream != null) outputStream.close(); } catch (Exception ignored) {}
            if (connection != null) connection.disconnect();
        }
    }

    /**
     * 从图片URL提取 Referer（取域名部分）
     */
    private String extractReferer(String url) {
        try {
            URL u = new URL(url);
            return u.getProtocol() + "://" + u.getHost() + "/";
        } catch (Exception e) {
            return "";
        }
    }
}
