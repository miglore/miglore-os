-- Miglore OS — Linux Engineer Roadmap V2 seed (L0 阶段)
-- 目标: 仅开发库 miglore_os | 执行需 --default-character-set=utf8mb4 (防 latin1 污染)
USE miglore_os;

-- 新主路线 (与现有 "Linux → DevOps" 并行, 不删不改)
INSERT INTO learning_tracks (id, user_id, title, description, status, progress, started_at, sort_order)
VALUES (2, 1, 'Linux Engineer Roadmap V2',
        'L0-L15 Linux 工程师路线（职业目标：Linux 工程师）。L0 基础操作 → L1 文件系统 → … → L15 Kubernetes',
        'active', 0, '2026-08-16', 2);

-- L0 Linux 基础操作 (15 个任务, skill_id=1 复用 Linux 技能)
INSERT INTO tasks (id, user_id, type, title, description, status, priority, track_id, skill_id, sort_order) VALUES
(11, 1, 'learning', '01 认识 Linux', '在终端执行 uname -a 与 cat /etc/os-release，了解内核版本与发行版信息。', 'todo', 2, 2, 1, 1),
(12, 1, 'learning', '02 pwd', '执行 pwd 确认当前目录，理解绝对路径的概念。', 'todo', 2, 2, 1, 2),
(13, 1, 'learning', '03 ls', '执行 ls -lah / 查看根目录结构，认识 /etc /var /home /tmp 等目录。', 'todo', 2, 2, 1, 3),
(14, 1, 'learning', '04 cd', '执行 cd /tmp && pwd 切换目录，再 cd - 回到原目录。', 'todo', 2, 2, 1, 4),
(15, 1, 'learning', '05 mkdir', '执行 mkdir -p /tmp/miglab 创建实验目录，用 ls -ld 确认。', 'todo', 2, 2, 1, 5),
(16, 1, 'learning', '06 touch', '执行 touch /tmp/miglab/hello.txt 创建空文件，用 ls -l 查看。', 'todo', 2, 2, 1, 6),
(17, 1, 'learning', '07 cp', '执行 echo hello > /tmp/miglab/hello.txt 写入内容，再 cp /tmp/miglab/hello.txt /tmp/miglab/copy.txt 复制。', 'todo', 2, 2, 1, 7),
(18, 1, 'learning', '08 mv', '执行 mv /tmp/miglab/copy.txt /tmp/miglab/moved.txt 重命名/移动文件。', 'todo', 2, 2, 1, 8),
(19, 1, 'learning', '09 rm', '执行 touch /tmp/miglab/old.txt 后，用 rm /tmp/miglab/old.txt 删除，再确认文件不存在。', 'todo', 2, 2, 1, 9),
(20, 1, 'learning', '10 cat', '执行 cat /tmp/miglab/hello.txt 查看文件内容。', 'todo', 2, 2, 1, 10),
(21, 1, 'learning', '11 less', '了解 less 用于大文件分页查看（无 TTY 环境下用 cat/head 体验），执行 head -1 /tmp/miglab/hello.txt。', 'todo', 2, 2, 1, 11),
(22, 1, 'learning', '12 head / tail', '执行 head -3 /tmp/miglab/hello.txt 查看头部，tail -2 /tmp/miglab/hello.txt 查看尾部。', 'todo', 2, 2, 1, 12),
(23, 1, 'learning', '13 grep', '执行 grep hello /tmp/miglab/hello.txt 搜索文件内容，再试 grep -n -i。', 'todo', 2, 2, 1, 13),
(24, 1, 'learning', '14 find', '执行 find /tmp/miglab -name "*.txt" 按名称查找文件。', 'todo', 2, 2, 1, 14),
(25, 1, 'learning', '15 综合文件操作实验', '完整流程：mkdir -p /tmp/miglab 创建目录、echo 写入内容、cp 复制、mv 移动、rm 删除、grep 搜索、find 查找，串起 05-14 全部命令。', 'todo', 2, 2, 1, 15);
