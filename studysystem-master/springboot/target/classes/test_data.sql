-- 学习系统测试数据
USE manager;

-- 1. 插入测试用户
INSERT INTO `user` (`username`, `password`, `name`, `role`, `phone`, `email`, `member`, `score`, `account`) VALUES
('user1', '123', '张三', 'USER', '13800138001', 'user1@test.com', '是', 500, 1000),
('user2', '123', '李四', 'USER', '13800138002', 'user2@test.com', '否', 300, 500),
('user3', '123', '王五', 'USER', '13800138003', 'user3@test.com', '是', 800, 2000),
('user4', '123', '赵六', 'USER', '13800138004', 'user4@test.com', '否', 150, 300),
('user5', '123', '钱七', 'USER', '13800138005', 'user5@test.com', '否', 200, 400);

-- 2. 插入课程数据
INSERT INTO `course` (`img`, `name`, `content`, `type`, `price`, `video`, `file`, `discount`, `recommend`, `time`) VALUES
('https://picsum.photos/300/200?random=1', 'Java入门到精通', '<p>Java基础教程，适合零基础学员</p>', 'VIDEO', 99, 'http://example.com/java.mp4', 'http://example.com/java.pdf', 0.9, '是', '2024-01-01'),
('https://picsum.photos/300/200?random=2', 'SpringBoot实战', '<p>SpringBoot框架实战开发</p>', 'VIDEO', 199, 'http://example.com/spring.mp4', 'http://example.com/spring.pdf', 0.8, '否', '2024-01-05'),
('https://picsum.photos/300/200?random=3', 'Vue前端开发', '<p>Vue3全家桶实战教程</p>', 'VIDEO', 149, 'http://example.com/vue.mp4', 'http://example.com/vue.pdf', 1.0, '否', '2024-01-10'),
('https://picsum.photos/300/200?random=4', 'MySQL数据库', '<p>MySQL从入门到优化</p>', 'TEXT', 79, NULL, 'http://example.com/mysql.pdf', 0.85, '否', '2024-01-15'),
('https://picsum.photos/300/200?random=5', 'Redis缓存技术', '<p>Redis实战与应用场景</p>', 'VIDEO', 129, 'http://example.com/redis.mp4', 'http://example.com/redis.pdf', 1.0, '否', '2024-01-20'),
('https://picsum.photos/300/200?random=6', 'Python数据分析', '<p>Python数据处理与分析</p>', 'VIDEO', 169, 'http://example.com/python.mp4', 'http://example.com/python.pdf', 0.9, '是', '2024-02-01'),
('https://picsum.photos/300/200?random=7', 'Docker容器技术', '<p>Docker与K8s实战</p>', 'TEXT', 89, NULL, 'http://example.com/docker.pdf', 1.0, '否', '2024-02-05'),
('https://picsum.photos/300/200?random=8', '微服务架构', '<p>微服务设计与实践</p>', 'VIDEO', 299, 'http://example.com/micro.mp4', 'http://example.com/micro.pdf', 0.75, '否', '2024-02-10');

-- 3. 插入订单数据（用于协同过滤）
INSERT INTO `orders` (`course_id`, `price`, `order_id`, `time`, `user_id`) VALUES
(1, 89.1, 'ORD001', '2024-01-10', 1), (2, 159.2, 'ORD002', '2024-01-11', 1),
(1, 89.1, 'ORD003', '2024-01-12', 2), (3, 149, 'ORD004', '2024-01-13', 2),
(2, 159.2, 'ORD005', '2024-01-14', 3), (4, 67.15, 'ORD006', '2024-01-15', 3),
(1, 89.1, 'ORD007', '2024-01-16', 4), (5, 129, 'ORD008', '2024-01-17', 4),
(3, 149, 'ORD009', '2024-01-18', 5), (6, 152.1, 'ORD010', '2024-01-19', 5),
(2, 159.2, 'ORD011', '2024-01-20', 1), (6, 152.1, 'ORD012', '2024-01-21', 2),
(7, 89, 'ORD013', '2024-01-22', 3), (8, 224.25, 'ORD014', '2024-01-23', 3),
(4, 67.15, 'ORD015', '2024-01-24', 1), (5, 129, 'ORD016', '2024-01-25', 2);

-- 4. 插入积分商品
INSERT INTO `score` (`img`, `name`, `content`, `type`, `price`, `video`, `file`, `recommend`, `time`) VALUES
('https://picsum.photos/300/200?random=9', '设计模式精讲', '<p>23种设计模式详解</p>', 'VIDEO', 200, 'http://example.com/pattern.mp4', 'http://example.com/pattern.pdf', '是', '2024-01-01'),
('https://picsum.photos/300/200?random=10', 'Git版本控制', '<p>Git使用技巧与团队协作</p>', 'TEXT', 100, NULL, 'http://example.com/git.pdf', '否', '2024-01-05'),
('https://picsum.photos/300/200?random=11', 'Linux运维基础', '<p>Linux常用命令与脚本</p>', 'TEXT', 150, NULL, 'http://example.com/linux.pdf', '否', '2024-01-10');

-- 5. 插入积分兑换记录
INSERT INTO `scoreorder` (`score_id`, `score`, `order_id`, `time`, `user_id`) VALUES
(1, 200, 'SCO001', '2024-01-15', 1), (2, 100, 'SCO002', '2024-01-16', 2),
(1, 200, 'SCO003', '2024-01-17', 3), (3, 150, 'SCO004', '2024-01-18', 4);

-- 6. 插入资料
INSERT INTO `information` (`name`, `content`, `file`, `img`, `score`, `time`, `recommend`, `user_id`, `status`, `descr`) VALUES
('Java面试题汇总', '<p>高频Java面试题整理</p>', 'http://example.com/java-interview.pdf', 'https://picsum.photos/300/200?random=12', 50, '2024-01-01', '是', 1, '审核通过', ''),
('SpringBoot笔记', '<p>SpringBoot学习笔记</p>', 'http://example.com/spring-note.pdf', 'https://picsum.photos/300/200?random=13', 30, '2024-01-05', '否', 2, '审核通过', ''),
('前端开发手册', '<p>前端开发规范文档</p>', 'http://example.com/frontend.pdf', 'https://picsum.photos/300/200?random=14', 0, '2024-01-10', '否', 3, '审核通过', '');

-- 7. 插入公告
INSERT INTO `notice` (`title`, `content`, `time`, `user`) VALUES
('系统上线公告', '学习平台正式上线，欢迎体验！', '2024-01-01', 'admin'),
('签到送积分', '每日签到可获得10积分奖励', '2024-01-05', 'admin');
