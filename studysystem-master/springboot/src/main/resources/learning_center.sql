-- 学习中心相关表

-- 学习记录表
CREATE TABLE IF NOT EXISTS learning_record (
  id int(11) NOT NULL AUTO_INCREMENT,
  user_id int(11) NOT NULL COMMENT '用户ID',
  course_id int(11) DEFAULT NULL COMMENT '课程ID',
  course_name varchar(255) DEFAULT NULL COMMENT '课程名称',
  course_type varchar(50) DEFAULT NULL COMMENT '课程类型',
  duration int(11) DEFAULT 0 COMMENT '学习时长(分钟)',
  progress int(11) DEFAULT 0 COMMENT '学习进度(%)',
  last_position varchar(255) DEFAULT NULL COMMENT '上次播放位置',
  create_time varchar(50) DEFAULT NULL COMMENT '创建时间',
  update_time varchar(50) DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习记录表';

-- 学习计划表
CREATE TABLE IF NOT EXISTS learning_plan (
  id int(11) NOT NULL AUTO_INCREMENT,
  user_id int(11) NOT NULL COMMENT '用户ID',
  title varchar(255) NOT NULL COMMENT '计划标题',
  content text COMMENT '计划内容',
  target_course_id int(11) DEFAULT NULL COMMENT '目标课程ID',
  daily_goal int(11) DEFAULT 30 COMMENT '每日目标(分钟)',
  start_date varchar(50) DEFAULT NULL COMMENT '开始日期',
  end_date varchar(50) DEFAULT NULL COMMENT '结束日期',
  status varchar(50) DEFAULT '进行中' COMMENT '状态',
  progress int(11) DEFAULT 0 COMMENT '完成进度(%)',
  create_time varchar(50) DEFAULT NULL COMMENT '创建时间',
  update_time varchar(50) DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习计划表';

-- 课堂笔记表
CREATE TABLE IF NOT EXISTS note (
  id int(11) NOT NULL AUTO_INCREMENT,
  user_id int(11) NOT NULL COMMENT '用户ID',
  course_id int(11) DEFAULT NULL COMMENT '课程ID',
  course_name varchar(255) DEFAULT NULL COMMENT '课程名称',
  title varchar(255) DEFAULT NULL COMMENT '笔记标题',
  content text COMMENT '笔记内容',
  video_time varchar(50) DEFAULT NULL COMMENT '视频时间点',
  create_time varchar(50) DEFAULT NULL COMMENT '创建时间',
  update_time varchar(50) DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课堂笔记表';
