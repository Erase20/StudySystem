package com.example.entity;

import java.io.Serializable;

/**
 * 课程章节表
 */
public class Chapter implements Serializable {

    private static final long serialVersionUID = 1L;

    private Integer id;
    private Integer courseId;
    private String title;
    private Integer sortOrder;
    private String type;
    private String video;
    private Integer duration;
    private Integer freePreview;

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public Integer getCourseId() { return courseId; }
    public void setCourseId(Integer courseId) { this.courseId = courseId; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public Integer getSortOrder() { return sortOrder; }
    public void setSortOrder(Integer sortOrder) { this.sortOrder = sortOrder; }
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    public String getVideo() { return video; }
    public void setVideo(String video) { this.video = video; }
    public Integer getDuration() { return duration; }
    public void setDuration(Integer duration) { this.duration = duration; }
    public Integer getFreePreview() { return freePreview; }
    public void setFreePreview(Integer freePreview) { this.freePreview = freePreview; }
}
