-- 管理员演示数据 SQL
-- 为 admin 账号生成完整的演示数据

-- 先清空 admin 现有数据（admin ID = 1）
DELETE FROM orders WHERE user_id = 1;
DELETE FROM learning_record WHERE user_id = 1;
DELETE FROM learning_plan WHERE user_id = 1;
DELETE FROM note WHERE user_id = 1;

-- 设置 admin ID
SET @admin_id = 1;

-- 插入订单数据（8条）
INSERT INTO orders (order_id, course_id, price, time, user_id, course_type) VALUES
('ORD202503160001', 1, 99.00, DATE_SUB(NOW(), INTERVAL 5 DAY), @admin_id, 'VIDEO'),
('ORD202503160002', 2, 49.90, DATE_SUB(NOW(), INTERVAL 12 DAY), @admin_id, 'VIDEO'),
('ORD202503160003', 3, 199.00, DATE_SUB(NOW(), INTERVAL 8 DAY), @admin_id, 'VIDEO'),
('ORD202503160004', 4, 29.90, DATE_SUB(NOW(), INTERVAL 20 DAY), @admin_id, 'VIDEO'),
('ORD202503160005', 5, 0.00, DATE_SUB(NOW(), INTERVAL 15 DAY), @admin_id, 'VIDEO'),
('ORD202503160006', 6, 49.90, DATE_SUB(NOW(), INTERVAL 25 DAY), @admin_id, 'TEXT'),
('ORD202503160007', 7, 29.90, DATE_SUB(NOW(), INTERVAL 30 DAY), @admin_id, 'TEXT'),
('ORD202503160008', 8, 99.00, DATE_SUB(NOW(), INTERVAL 3 DAY), @admin_id, 'VIDEO');

-- 插入学习记录（24条）
INSERT INTO learning_record (user_id, course_id, course_name, course_type, duration, progress, last_position, create_time, update_time) VALUES
(@admin_id, 1, 'Python', 'VIDEO', 45, 100, '05:30', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY)),
(@admin_id, 1, 'Python', 'VIDEO', 30, 100, '03:15', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 4 DAY)),
(@admin_id, 2, 'Java', 'VIDEO', 25, 85, '04:20', DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY)),
(@admin_id, 2, 'Java', 'VIDEO', 20, 85, '02:45', DATE_SUB(NOW(), INTERVAL 8 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY)),
(@admin_id, 3, 'Vue', 'VIDEO', 50, 72, '06:10', DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY)),
(@admin_id, 3, 'Vue', 'VIDEO', 40, 72, '05:00', DATE_SUB(NOW(), INTERVAL 6 DAY), DATE_SUB(NOW(), INTERVAL 5 DAY)),
(@admin_id, 4, 'MySQL', 'VIDEO', 20, 60, '03:30', DATE_SUB(NOW(), INTERVAL 4 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY)),
(@admin_id, 5, 'SpringBoot', 'VIDEO', 35, 45, '04:45', DATE_SUB(NOW(), INTERVAL 7 DAY), DATE_SUB(NOW(), INTERVAL 6 DAY)),
(@admin_id, 6, 'Docker', 'TEXT', 15, 100, '02:00', DATE_SUB(NOW(), INTERVAL 10 DAY), DATE_SUB(NOW(), INTERVAL 9 DAY)),
(@admin_id, 7, 'Linux', 'TEXT', 18, 80, '02:30', DATE_SUB(NOW(), INTERVAL 12 DAY), DATE_SUB(NOW(), INTERVAL 11 DAY)),
(@admin_id, 8, 'React', 'VIDEO', 40, 30, '05:20', DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY)),
(@admin_id, 1, 'Python', 'VIDEO', 35, 100, '04:00', DATE_SUB(NOW(), INTERVAL 15 DAY), DATE_SUB(NOW(), INTERVAL 14 DAY)),
(@admin_id, 2, 'Java', 'VIDEO', 28, 85, '04:50', DATE_SUB(NOW(), INTERVAL 18 DAY), DATE_SUB(NOW(), INTERVAL 17 DAY)),
(@admin_id, 3, 'Vue', 'VIDEO', 45, 72, '05:30', DATE_SUB(NOW(), INTERVAL 10 DAY), DATE_SUB(NOW(), INTERVAL 9 DAY)),
(@admin_id, 4, 'MySQL', 'VIDEO', 22, 60, '03:45', DATE_SUB(NOW(), INTERVAL 14 DAY), DATE_SUB(NOW(), INTERVAL 13 DAY)),
(@admin_id, 5, 'SpringBoot', 'VIDEO', 30, 45, '04:00', DATE_SUB(NOW(), INTERVAL 20 DAY), DATE_SUB(NOW(), INTERVAL 19 DAY)),
(@admin_id, 6, 'Docker', 'TEXT', 12, 100, '01:45', DATE_SUB(NOW(), INTERVAL 22 DAY), DATE_SUB(NOW(), INTERVAL 21 DAY)),
(@admin_id, 7, 'Linux', 'TEXT', 20, 80, '02:50', DATE_SUB(NOW(), INTERVAL 25 DAY), DATE_SUB(NOW(), INTERVAL 24 DAY)),
(@admin_id, 8, 'React', 'VIDEO', 35, 30, '04:30', DATE_SUB(NOW(), INTERVAL 8 DAY), DATE_SUB(NOW(), INTERVAL 7 DAY)),
(@admin_id, 1, 'Python', 'VIDEO', 40, 100, '04:45', DATE_SUB(NOW(), INTERVAL 28 DAY), DATE_SUB(NOW(), INTERVAL 27 DAY)),
(@admin_id, 2, 'Java', 'VIDEO', 32, 85, '05:10', DATE_SUB(NOW(), INTERVAL 22 DAY), DATE_SUB(NOW(), INTERVAL 21 DAY)),
(@admin_id, 3, 'Vue', 'VIDEO', 55, 72, '06:30', DATE_SUB(NOW(), INTERVAL 12 DAY), DATE_SUB(NOW(), INTERVAL 11 DAY)),
(@admin_id, 4, 'MySQL', 'VIDEO', 18, 60, '03:15', DATE_SUB(NOW(), INTERVAL 16 DAY), DATE_SUB(NOW(), INTERVAL 15 DAY)),
(@admin_id, 5, 'SpringBoot', 'VIDEO', 25, 45, '03:30', DATE_SUB(NOW(), INTERVAL 24 DAY), DATE_SUB(NOW(), INTERVAL 23 DAY));

-- 插入学习计划（3条）
INSERT INTO learning_plan (title, content, start_date, end_date, daily_goal, progress, status, user_id, target_course_id) VALUES
('Python Study', 'Learn Python basics', DATE_SUB(NOW(), INTERVAL 10 DAY), DATE_ADD(NOW(), INTERVAL 80 DAY), 60, 75, 'Active', @admin_id, 1),
('Frontend', 'Learn Vue and React', DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_ADD(NOW(), INTERVAL 55 DAY), 45, 45, 'Active', @admin_id, 3),
('Database', 'Learn MySQL', DATE_SUB(NOW(), INTERVAL 15 DAY), DATE_ADD(NOW(), INTERVAL 45 DAY), 30, 20, 'Active', @admin_id, 4);

-- 插入笔记（5条）
INSERT INTO note (title, content, create_time, user_id, course_id, course_name, video_time) VALUES
('Python Decorator', 'Python decorator usage', DATE_SUB(NOW(), INTERVAL 3 DAY), @admin_id, 1, 'Python', '05:30'),
('Vue Component', 'Vue component communication', DATE_SUB(NOW(), INTERVAL 5 DAY), @admin_id, 3, 'Vue', '06:10'),
('MySQL Index', 'MySQL index optimization', DATE_SUB(NOW(), INTERVAL 7 DAY), @admin_id, 4, 'MySQL', '03:30'),
('Docker Cmd', 'Docker basic commands', DATE_SUB(NOW(), INTERVAL 10 DAY), @admin_id, 6, 'Docker', '02:00'),
('SpringBoot', 'SpringBoot auto config', DATE_SUB(NOW(), INTERVAL 12 DAY), @admin_id, 5, 'SpringBoot', '04:45');
