/*
 Navicat Premium Data Transfer

 Source Server         : test1007
 Source Server Type    : MySQL
 Source Server Version : 80033
 Source Host           : localhost:3306
 Source Schema         : smartfinance

 Target Server Type    : MySQL
 Target Server Version : 80033
 File Encoding         : 65001

 Date: 20/01/2026 17:46:46
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for alerts
-- ----------------------------
DROP TABLE IF EXISTS `alerts`;
CREATE TABLE `alerts`  (
  `alert_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `event_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `alert_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `alert_level` enum('高','中','低') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `triggered_at` datetime NULL DEFAULT NULL,
  `status` enum('待处理','处理中','已解决','已忽略') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '待处理',
  `handler` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `operation_log` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `remark` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`alert_id`) USING BTREE,
  INDEX `event_id`(`event_id` ASC) USING BTREE,
  INDEX `idx_alert_status`(`status` ASC) USING BTREE,
  CONSTRAINT `alerts_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `risk_events` (`event_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of alerts
-- ----------------------------
INSERT INTO `alerts` VALUES ('al_test_001', 'ev_test_001', '异常交易告警', '高', '2026-01-13 14:34:29', '待处理', NULL, NULL, NULL, '2026-01-13 14:38:29', '2026-01-13 14:38:29');
INSERT INTO `alerts` VALUES ('al_test_002', 'ev_test_002', '设备异常告警', '中', '2026-01-13 14:18:49', '待处理', NULL, NULL, NULL, '2026-01-13 14:38:49', '2026-01-13 14:38:49');

-- ----------------------------
-- Table structure for auth_accounts
-- ----------------------------
DROP TABLE IF EXISTS `auth_accounts`;
CREATE TABLE `auth_accounts`  (
  `auth_id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`auth_id`) USING BTREE,
  UNIQUE INDEX `uniq_user`(`user_id` ASC) USING BTREE,
  CONSTRAINT `fk_auth_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of auth_accounts
-- ----------------------------
INSERT INTO `auth_accounts` VALUES (2, '58b84e778dff4ea48413c2a3b2ca1f59', 'scrypt:32768:8:1$qkePbOSdBE1AevF7$ae17aabae3961c98beaaf60959a561d57c5cf519f2528a0896c49199735d1ba136dfe91f44add6d677a34c91858852565ab23bcc1d2b13a1f401c22b42671ce8', '2026-01-13 07:41:18');
INSERT INTO `auth_accounts` VALUES (3, 'f3eb5f1e21a5432487c1f48918e4f36f', 'scrypt:32768:8:1$bxdLOtzGGrH5vKZq$12829af7721e5f9edea3356fa0de4421440647ab9bf2053f65037d9b68dd51203e347eface3908fdc9cb8fbe549d937ce1770ecb9e72fa5af3d774f6648912a7', '2026-01-20 09:07:31');

-- ----------------------------
-- Table structure for data_quality_issues
-- ----------------------------
DROP TABLE IF EXISTS `data_quality_issues`;
CREATE TABLE `data_quality_issues`  (
  `issue_id` bigint NOT NULL AUTO_INCREMENT,
  `source_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `issue_type` enum('缺失字段','格式错误','值异常','数据不一致') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `affected_records_count` int NULL DEFAULT NULL,
  `example_record` json NULL,
  `severity` enum('高','中','低') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `resolved_at` timestamp NULL DEFAULT NULL,
  `resolved_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `status` enum('未处理','处理中','已解决') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`issue_id`) USING BTREE,
  INDEX `source_id`(`source_id` ASC) USING BTREE,
  CONSTRAINT `data_quality_issues_ibfk_1` FOREIGN KEY (`source_id`) REFERENCES `data_sources` (`source_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of data_quality_issues
-- ----------------------------
INSERT INTO `data_quality_issues` VALUES (1, 'src_login', '缺失字段', '部分登录记录缺失地理位置信息', 50, NULL, '中', '2026-01-13 14:38:04', NULL, NULL, '未处理');

-- ----------------------------
-- Table structure for data_sources
-- ----------------------------
DROP TABLE IF EXISTS `data_sources`;
CREATE TABLE `data_sources`  (
  `source_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `source_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `source_type` enum('数据库','API','文件','消息队列') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `connection_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `status` enum('正常','异常','中断') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '正常',
  `last_sync_time` datetime NULL DEFAULT NULL,
  `sync_progress` decimal(5, 2) NULL DEFAULT 0.00,
  `error_count` int NULL DEFAULT 0,
  `last_error_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `collection_status` enum('running','stopped','paused') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'running',
  `today_collected` int NULL DEFAULT 0,
  `estimated_completion` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`source_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of data_sources
-- ----------------------------
INSERT INTO `data_sources` (`source_id`, `source_name`, `source_type`, `connection_url`, `status`, `last_sync_time`, `sync_progress`, `error_count`, `last_error_message`, `created_at`, `updated_at`) VALUES ('src_login', '登录日志源', 'API', NULL, '异常', '2026-01-13 11:37:58', 80.00, 3, '网络超时', '2026-01-13 14:37:58', '2026-01-13 14:37:58');
INSERT INTO `data_sources` (`source_id`, `source_name`, `source_type`, `connection_url`, `status`, `last_sync_time`, `sync_progress`, `error_count`, `last_error_message`, `created_at`, `updated_at`) VALUES ('src_tx', '交易日志源', '数据库', NULL, '正常', '2026-01-13 14:37:58', 100.00, 0, NULL, '2026-01-13 14:37:58', '2026-01-13 14:37:58');

-- ----------------------------
-- Table structure for devices
-- ----------------------------
DROP TABLE IF EXISTS `devices`;
CREATE TABLE `devices`  (
  `device_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `user_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `device_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `os_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `ip_address` varchar(39) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `is_normal` tinyint(1) NULL DEFAULT 1,
  `last_login_time` datetime NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`device_id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_ip_address`(`ip_address` ASC) USING BTREE,
  CONSTRAINT `devices_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of devices
-- ----------------------------
INSERT INTO `devices` VALUES ('d_test_001', 'u_test_001', 'Alice iPhone', 'iOS', '1.1.1.1', '武汉', 1, '2026-01-13 13:37:52', '2026-01-13 14:37:52', '2026-01-13 14:37:52');
INSERT INTO `devices` VALUES ('d_test_002', 'u_test_002', 'Bob Android', 'Android', '2.2.2.2', '北京', 0, '2026-01-13 12:37:52', '2026-01-13 14:37:52', '2026-01-13 14:37:52');

-- ----------------------------
-- Table structure for event_timeline
-- ----------------------------
DROP TABLE IF EXISTS `event_timeline`;
CREATE TABLE `event_timeline`  (
  `timeline_id` bigint NOT NULL AUTO_INCREMENT,
  `event_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `step_no` int NULL DEFAULT NULL,
  `step_title` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `step_description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `timestamp` datetime NULL DEFAULT NULL,
  `type` enum('登录','验证','交易','异常','处理') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `related_entity` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`timeline_id`) USING BTREE,
  INDEX `event_id`(`event_id` ASC) USING BTREE,
  CONSTRAINT `event_timeline_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `risk_events` (`event_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of event_timeline
-- ----------------------------
INSERT INTO `event_timeline` VALUES (1, 'ev_test_001', 1, '登录', '用户在武汉登录', '2026-01-13 13:38:25', '登录', 'log_1', '2026-01-13 14:38:25');
INSERT INTO `event_timeline` VALUES (2, 'ev_test_001', 2, '异地登录', '用户在上海再次登录', '2026-01-13 14:28:25', '登录', 'log_2', '2026-01-13 14:38:25');
INSERT INTO `event_timeline` VALUES (3, 'ev_test_001', 3, '大额交易', '发生一笔 20000 元转账(tx_test_002)', '2026-01-13 14:33:25', '交易', 'tx_test_002', '2026-01-13 14:38:25');

-- ----------------------------
-- Table structure for financial_transactions
-- ----------------------------
DROP TABLE IF EXISTS `financial_transactions`;
CREATE TABLE `financial_transactions`  (
  `tx_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `user_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `amount` decimal(15, 2) NULL DEFAULT NULL,
  `currency` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'CNY',
  `transaction_time` datetime NULL DEFAULT NULL,
  `status` enum('成功','失败','处理中') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `ip_address` varchar(39) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `device_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`tx_id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `device_id`(`device_id` ASC) USING BTREE,
  INDEX `idx_tx_time`(`transaction_time` ASC) USING BTREE,
  CONSTRAINT `financial_transactions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `financial_transactions_ibfk_2` FOREIGN KEY (`device_id`) REFERENCES `devices` (`device_id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of financial_transactions
-- ----------------------------
INSERT INTO `financial_transactions` VALUES ('tx_test_001', 'u_test_001', 500.00, 'CNY', '2026-01-13 14:08:15', '成功', '消费', '1.1.1.1', 'd_test_001', '2026-01-13 14:38:15');
INSERT INTO `financial_transactions` VALUES ('tx_test_002', 'u_test_001', 20000.00, 'CNY', '2026-01-13 14:33:15', '成功', '转账', '3.3.3.3', 'd_test_001', '2026-01-13 14:38:15');

-- ----------------------------
-- Table structure for handling_records
-- ----------------------------
DROP TABLE IF EXISTS `handling_records`;
CREATE TABLE `handling_records`  (
  `record_id` bigint NOT NULL AUTO_INCREMENT,
  `event_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `operator` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `action` enum('冻结账户','发送验证码','标记已处理','忽略','联系用户') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `action_time` datetime NULL DEFAULT NULL,
  `comment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`record_id`) USING BTREE,
  INDEX `event_id`(`event_id` ASC) USING BTREE,
  CONSTRAINT `handling_records_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `risk_events` (`event_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of handling_records
-- ----------------------------

-- ----------------------------
-- Table structure for login_logs
-- ----------------------------
DROP TABLE IF EXISTS `login_logs`;
CREATE TABLE `login_logs`  (
  `log_id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `device_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `ip_address` varchar(39) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `login_time` datetime NULL DEFAULT NULL,
  `login_status` enum('成功','失败') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `login_location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `client_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `session_token` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `device_id`(`device_id` ASC) USING BTREE,
  INDEX `idx_login_time`(`login_time` ASC) USING BTREE,
  CONSTRAINT `login_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `login_logs_ibfk_2` FOREIGN KEY (`device_id`) REFERENCES `devices` (`device_id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of login_logs
-- ----------------------------
INSERT INTO `login_logs` VALUES (1, 'u_test_001', 'd_test_001', '1.1.1.1', '2026-01-13 13:38:08', '成功', '武汉', 'APP', 'token1', '2026-01-13 14:38:08');
INSERT INTO `login_logs` VALUES (2, 'u_test_001', 'd_test_001', '3.3.3.3', '2026-01-13 14:28:08', '成功', '上海', 'WEB', 'token2', '2026-01-13 14:38:08');
INSERT INTO `login_logs` VALUES (3, '58b84e778dff4ea48413c2a3b2ca1f59', 'd_test_001', '1.2.3.4', '2026-01-13 07:42:40', '成功', '武汉', 'WEB', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1OGI4NGU3NzhkZmY0ZWE0ODQxM2MyYTNiMmNhMWY1OSIsImlhdCI6MTc2ODI5MDE1OSwiZXhwIjoxNzY4MzMzMzU5fQ.pBezuCpQKg_TWNayK0pV1BIPhLmwg8sMWesHUvVBLhE', '2026-01-13 07:42:40');
INSERT INTO `login_logs` VALUES (4, 'f3eb5f1e21a5432487c1f48918e4f36f', NULL, NULL, '2026-01-20 09:11:42', '成功', NULL, 'WEB', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmM2ViNWYxZTIxYTU0MzI0ODdjMWY0ODkxOGU0ZjM2ZiIsImlhdCI6MTc2ODkwMDMwMiwiZXhwIjoxNzY4OTQzNTAyfQ.o3KSM0gCLG6hi8zaV2kI-zCJGOypHFEtpux3Mm0Bkt8', '2026-01-20 09:11:42');
INSERT INTO `login_logs` VALUES (5, 'f3eb5f1e21a5432487c1f48918e4f36f', NULL, NULL, '2026-01-20 09:17:16', '成功', NULL, 'WEB', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmM2ViNWYxZTIxYTU0MzI0ODdjMWY0ODkxOGU0ZjM2ZiIsImlhdCI6MTc2ODkwMDYzNSwiZXhwIjoxNzY4OTQzODM1fQ.aaPZ0G14Bns5qdedypASNqBny0FAkLQi9ilUxpw_Q_k', '2026-01-20 09:17:16');
INSERT INTO `login_logs` VALUES (6, 'f3eb5f1e21a5432487c1f48918e4f36f', NULL, NULL, '2026-01-20 09:22:43', '成功', NULL, 'WEB', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmM2ViNWYxZTIxYTU0MzI0ODdjMWY0ODkxOGU0ZjM2ZiIsImlhdCI6MTc2ODkwMDk2MywiZXhwIjoxNzY4OTQ0MTYzfQ.6DFOm8o56_Y3i0lrV31AMVh2PaC8nnG9MjR4_gex_l4', '2026-01-20 09:22:43');
INSERT INTO `login_logs` VALUES (7, 'f3eb5f1e21a5432487c1f48918e4f36f', NULL, NULL, '2026-01-20 09:27:37', '成功', NULL, 'WEB', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmM2ViNWYxZTIxYTU0MzI0ODdjMWY0ODkxOGU0ZjM2ZiIsImlhdCI6MTc2ODkwMTI1NiwiZXhwIjoxNzY4OTQ0NDU2fQ.o8vDDqu0pYxHummTt-gLsu7CdcIpnenCNrYLWeMv7F0', '2026-01-20 09:27:37');
INSERT INTO `login_logs` VALUES (8, 'f3eb5f1e21a5432487c1f48918e4f36f', NULL, NULL, '2026-01-20 09:34:58', '成功', NULL, 'WEB', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmM2ViNWYxZTIxYTU0MzI0ODdjMWY0ODkxOGU0ZjM2ZiIsImlhdCI6MTc2ODkwMTY5OCwiZXhwIjoxNzY4OTQ0ODk4fQ.6MaA3VewRCqhMuqPgHgdmXWi0HGLxXLpeEokjcC82hk', '2026-01-20 09:34:58');

-- ----------------------------
-- Table structure for related_users
-- ----------------------------
DROP TABLE IF EXISTS `related_users`;
CREATE TABLE `related_users`  (
  `relation_id` bigint NOT NULL AUTO_INCREMENT,
  `event_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `user_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `relationship_type` enum('关联账户','同IP注册','共用设备') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `risk_score` int NULL DEFAULT 0,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`relation_id`) USING BTREE,
  INDEX `event_id`(`event_id` ASC) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `related_users_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `risk_events` (`event_id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `related_users_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of related_users
-- ----------------------------
INSERT INTO `related_users` VALUES (1, 'ev_test_001', 'u_test_002', '同IP注册', 70, '2026-01-13 14:38:33');

-- ----------------------------
-- Table structure for risk_analysis_recommendations
-- ----------------------------
DROP TABLE IF EXISTS `risk_analysis_recommendations`;
CREATE TABLE `risk_analysis_recommendations`  (
  `rec_id` bigint NOT NULL AUTO_INCREMENT,
  `event_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `risk_assessment` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `recommendation_text` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `priority` enum('高','中','低') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`rec_id`) USING BTREE,
  INDEX `event_id`(`event_id` ASC) USING BTREE,
  CONSTRAINT `risk_analysis_recommendations_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `risk_events` (`event_id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of risk_analysis_recommendations
-- ----------------------------
INSERT INTO `risk_analysis_recommendations` VALUES (1, 'ev_test_001', '该用户近期存在多次异地登录和大额交易，疑似账户被盗用。', '建议立即冻结账户，联系用户进行身份核验。', '高', '2026-01-13 14:38:39', '2026-01-13 14:38:39');

-- ----------------------------
-- Table structure for risk_events
-- ----------------------------
DROP TABLE IF EXISTS `risk_events`;
CREATE TABLE `risk_events`  (
  `event_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `event_type` enum('账户盗用','异常交易','证件伪造','批量注册','设备异常') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `risk_level` enum('高','中','低') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `score` int NULL DEFAULT 0,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `detection_time` datetime NULL DEFAULT NULL,
  `duration` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `status` enum('待处理','处理中','已解决','已忽略') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '待处理',
  `user_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `device_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `ip_address` varchar(39) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `trigger_rule` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `severity_scope` enum('个人','机构','平台') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '个人',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`event_id`) USING BTREE,
  INDEX `device_id`(`device_id` ASC) USING BTREE,
  INDEX `idx_user_id`(`user_id` ASC) USING BTREE,
  INDEX `idx_detection_time`(`detection_time` ASC) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE,
  CONSTRAINT `risk_events_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL ON UPDATE RESTRICT,
  CONSTRAINT `risk_events_ibfk_2` FOREIGN KEY (`device_id`) REFERENCES `devices` (`device_id`) ON DELETE SET NULL ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of risk_events
-- ----------------------------
INSERT INTO `risk_events` VALUES ('ev_test_001', '异常交易', '高', 90, '大额异地交易，短时间内多笔交易', '2026-01-13 14:34:20', '2h 15m', '处理中', 'u_test_001', 'd_test_001', '3.3.3.3', '规则引擎', '个人', '2026-01-13 14:38:20', '2026-01-13 07:29:19');
INSERT INTO `risk_events` VALUES ('ev_test_002', '设备异常', '中', 55, '绑定设备存在异常标记且近期更换频繁', '2026-01-13 14:18:44', NULL, '待处理', 'u_test_002', 'd_test_002', '2.2.2.2', '规则引擎', '个人', '2026-01-13 14:38:44', '2026-01-13 14:38:44');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `user_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `gender` enum('男','女','未知') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `birthday` date NULL DEFAULT NULL,
  `bio` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `avatar` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `department` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `role` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `employee_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `registration_time` datetime NULL DEFAULT NULL,
  `account_level` enum('普通','VIP') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '普通',
  `status` enum('正常','冻结','注销') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '正常',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` (`user_id`, `username`, `phone`, `email`, `registration_time`, `account_level`, `status`, `created_at`, `updated_at`) VALUES ('58b84e778dff4ea48413c2a3b2ca1f59', 'test_user1', '13800000010', 'test_user1@example.com', '2026-01-13 07:41:18', '普通', '正常', '2026-01-13 07:41:18', '2026-01-13 07:41:18');
INSERT INTO `users` (`user_id`, `username`, `phone`, `email`, `department`, `role`, `employee_id`, `registration_time`, `account_level`, `status`, `created_at`, `updated_at`) VALUES ('f3eb5f1e21a5432487c1f48918e4f36f', 'adon', '13800000000', 'alice@example.com', '风险管理部', 'manager', 'EMP-2023001', '2026-01-20 09:07:31', '普通', '正常', '2026-01-20 09:07:31', '2026-01-20 17:22:23');
INSERT INTO `users` (`user_id`, `username`, `phone`, `email`, `registration_time`, `account_level`, `status`, `created_at`, `updated_at`) VALUES ('u_test_001', 'alice', '13800000001', 'alice@test.com', '2025-10-05 14:37:47', '普通', '正常', '2026-01-13 14:37:47', '2026-01-13 14:37:47');
INSERT INTO `users` (`user_id`, `username`, `phone`, `email`, `registration_time`, `account_level`, `status`, `created_at`, `updated_at`) VALUES ('u_test_002', 'bob', '13800000002', 'bob@test.com', '2025-06-27 14:37:47', 'VIP', '正常', '2026-01-13 14:37:47', '2026-01-13 14:37:47');

SET FOREIGN_KEY_CHECKS = 1;
