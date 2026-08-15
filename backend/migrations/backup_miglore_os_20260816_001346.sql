-- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
--
-- Host: localhost    Database: miglore_os
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `career_directions`
--

DROP TABLE IF EXISTS `career_directions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `career_directions` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `target_role` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` enum('active','paused','closed') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `sort_order` int NOT NULL DEFAULT '0',
  `deleted_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_directions_user` (`user_id`),
  KEY `idx_directions_user_status` (`user_id`,`status`),
  CONSTRAINT `fk_directions_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `career_directions`
--

LOCK TABLES `career_directions` WRITE;
/*!40000 ALTER TABLE `career_directions` DISABLE KEYS */;
INSERT INTO `career_directions` VALUES (1,1,'DevOps / è¿ç»´å¼€å‘','äº‘åŽŸç”Ÿæ–¹å‘ï¼šå®¹å™¨åŒ–ã€CI/CDã€ç›‘æŽ§å‘Šè­¦','DevOps å·¥ç¨‹å¸ˆ','active',1,NULL,'2026-08-15 15:15:03','2026-08-15 15:15:03');
/*!40000 ALTER TABLE `career_directions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interview_evidence`
--

DROP TABLE IF EXISTS `interview_evidence`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `interview_evidence` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `project_id` bigint unsigned NOT NULL,
  `evidence_id` bigint unsigned DEFAULT NULL COMMENT 'å…³è”æŠ€æœ¯è¯æ® (å¯ç©º)',
  `skill_id` bigint unsigned DEFAULT NULL COMMENT 'å…³è”çŽ°æœ‰ skills è¡¨ (skills.id = BIGINT UNSIGNED, å·²éªŒè¯)',
  `question` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `answer` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_interview_evidence_user` (`user_id`),
  KEY `idx_interview_evidence_project` (`project_id`),
  KEY `idx_interview_evidence_skill` (`skill_id`),
  KEY `fk_iev_evidence` (`evidence_id`),
  CONSTRAINT `fk_iev_evidence` FOREIGN KEY (`evidence_id`) REFERENCES `project_evidence` (`id`),
  CONSTRAINT `fk_iev_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`),
  CONSTRAINT `fk_iev_skill` FOREIGN KEY (`skill_id`) REFERENCES `skills` (`id`),
  CONSTRAINT `fk_iev_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interview_evidence`
--

LOCK TABLES `interview_evidence` WRITE;
/*!40000 ALTER TABLE `interview_evidence` DISABLE KEYS */;
INSERT INTO `interview_evidence` VALUES (1,1,1,1,5,'ä½  Docker ç”¨åˆ°ä»€ä¹ˆç¨‹åº¦ï¼Ÿ','åŸºäºŽ Miglore OS å®žé™…éƒ¨ç½²ï¼šå‰ç«¯ multi-stage æž„å»ºï¼ˆnode æž„å»ºå±‚ â†’ nginx è¿è¡Œå±‚ï¼Œé•œåƒåªä¿ç•™ dist äº§ç‰©ï¼‰ï¼ŒåŽç«¯ python slim é•œåƒä»¥éž root ç”¨æˆ·è¿è¡Œï¼›Docker Compose ç¼–æŽ’ 5 ä¸ªæœåŠ¡ï¼ŒMySQL ç”¨ç‹¬ç«‹ volume æŒä¹…åŒ–ã€æ— å®¿ä¸»ç«¯å£æ˜ å°„ï¼›æ¯ä¸ªæœåŠ¡é…äº† healthcheckï¼Œmysql ç”¨ mysqladmin ping åšä¾èµ–å°±ç»ªæŽ’åºã€‚',NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50'),(2,1,1,3,6,'CI/CD æ€Žä¹ˆä¿è¯ä»£ç è´¨é‡ï¼Ÿ','GitHub Actions ä¸‰ job æµæ°´çº¿ï¼šbackend ç”¨ services.mysql èµ·ç‹¬ç«‹æµ‹è¯•åº“è·‘ 40+ pytest ç”¨ä¾‹ï¼Œfrontend è·‘ svelte-check ç±»åž‹æ£€æŸ¥ + vite buildï¼Œæœ€åŽ docker build éªŒè¯é•œåƒå¯æž„å»ºã€‚é‡åˆ°è¿‡ä¸€æ¬¡çœŸå®žå¤±è´¥ï¼šlockfile é”äº†å†…ç½‘é•œåƒæºå¯¼è‡´æµ·å¤– runner æ‹‰ä¸åˆ°åŒ…ï¼Œé€šè¿‡é‡å»º lockfile æ”¹ç”¨å…¬ç½‘ npmmirror ä¿®å¤ï¼Œæ²¡æœ‰ç»•è¿‡æµ‹è¯•ã€‚',NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50');
/*!40000 ALTER TABLE `interview_evidence` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interviews`
--

DROP TABLE IF EXISTS `interviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `interviews` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `application_id` bigint unsigned NOT NULL,
  `round` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'ä¸€é¢',
  `scheduled_at` datetime DEFAULT NULL,
  `interviewer` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `result` enum('pending','passed','failed','offered') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'pending',
  `review` text COLLATE utf8mb4_unicode_ci COMMENT 'å¤ç›˜',
  `note` text COLLATE utf8mb4_unicode_ci,
  `deleted_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_interviews_user` (`user_id`),
  KEY `idx_interviews_app` (`application_id`),
  KEY `idx_interviews_app_sched` (`application_id`,`scheduled_at`),
  CONSTRAINT `fk_interviews_app` FOREIGN KEY (`application_id`) REFERENCES `job_applications` (`id`),
  CONSTRAINT `fk_interviews_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interviews`
--

LOCK TABLES `interviews` WRITE;
/*!40000 ALTER TABLE `interviews` DISABLE KEYS */;
INSERT INTO `interviews` VALUES (1,1,1,'ä¸€é¢','2026-08-13 14:00:00','å¼ å·¥','passed','Linux/ç½‘ç»œåŸºç¡€æ‰Žå®ž',NULL,NULL,'2026-08-15 15:15:03','2026-08-15 15:15:03'),(2,1,2,'ä¸€é¢','2026-08-18 10:30:00','æŽå·¥','pending',NULL,NULL,NULL,'2026-08-15 15:15:03','2026-08-15 15:15:03'),(3,1,1,'äºŒé¢','2026-08-20 15:00:00','çŽ‹æ€»','pending',NULL,'å¾…é¢è¯•',NULL,'2026-08-15 15:15:03','2026-08-15 15:15:03');
/*!40000 ALTER TABLE `interviews` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `job_applications`
--

DROP TABLE IF EXISTS `job_applications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `job_applications` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `direction_id` bigint unsigned DEFAULT NULL,
  `company` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `position` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `city` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `salary` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `channel` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` enum('draft','applied','interviewing','offer','rejected','withdrawn') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'applied',
  `applied_at` date DEFAULT NULL,
  `note` text COLLATE utf8mb4_unicode_ci,
  `deleted_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_apps_user` (`user_id`),
  KEY `idx_apps_user_status` (`user_id`,`status`),
  KEY `idx_apps_direction` (`direction_id`),
  KEY `idx_apps_applied_at` (`applied_at`),
  CONSTRAINT `fk_apps_direction` FOREIGN KEY (`direction_id`) REFERENCES `career_directions` (`id`),
  CONSTRAINT `fk_apps_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `job_applications`
--

LOCK TABLES `job_applications` WRITE;
/*!40000 ALTER TABLE `job_applications` DISABLE KEYS */;
INSERT INTO `job_applications` VALUES (1,1,1,'æŸæŸäº‘ç§‘æŠ€','è¿ç»´å·¥ç¨‹å¸ˆ','ä¸Šæµ·','15-20K','BOSSç›´è˜',NULL,'interviewing','2026-08-10','ä¸€é¢é€šè¿‡ï¼Œç­‰äºŒé¢',NULL,'2026-08-15 15:15:03','2026-08-15 15:15:03'),(2,1,1,'æŸæŸæ•°æ®','DevOps å·¥ç¨‹å¸ˆ','æ­å·ž','18-25K','å†…æŽ¨',NULL,'interviewing','2026-08-08',NULL,NULL,'2026-08-15 15:15:03','2026-08-15 15:15:03'),(3,1,1,'æŸæŸç½‘ç»œ','äº‘è®¡ç®—è¿ç»´','ä¸Šæµ·','13-18K','BOSSç›´è˜',NULL,'applied','2026-08-12',NULL,NULL,'2026-08-15 15:15:03','2026-08-15 15:15:03'),(4,1,1,'æŸæŸä¿¡æ¯','è¿ç»´å¼€å‘','è¿œç¨‹','14-20K','æ‹‰å‹¾',NULL,'rejected','2026-08-01','å²—ä½è¦æ±‚ k8s ç”Ÿäº§ç»éªŒ',NULL,'2026-08-15 15:15:03','2026-08-15 15:15:03');
/*!40000 ALTER TABLE `job_applications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `learning_tracks`
--

DROP TABLE IF EXISTS `learning_tracks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `learning_tracks` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `title` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `status` enum('active','paused','completed') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `progress` int NOT NULL DEFAULT '0' COMMENT '0-100',
  `started_at` date DEFAULT NULL,
  `sort_order` int NOT NULL DEFAULT '0',
  `deleted_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_tracks_user` (`user_id`),
  KEY `idx_tracks_user_status` (`user_id`,`status`),
  CONSTRAINT `fk_tracks_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `learning_tracks`
--

LOCK TABLES `learning_tracks` WRITE;
/*!40000 ALTER TABLE `learning_tracks` DISABLE KEYS */;
INSERT INTO `learning_tracks` VALUES (1,1,'Linux â†’ DevOps','DevOps å·¥ç¨‹å¸ˆæˆé•¿è·¯çº¿ï¼Œå…± 8 é˜¶æ®µï¼š\n1. Linux åŸºç¡€\n2. ç½‘ç»œåŸºç¡€\n3. systemd\n4. Nginx\n5. Docker\n6. CI/CD\n7. Monitoring\n8. Kubernetes','active',50,'2026-06-01',1,NULL,'2026-08-15 14:09:51','2026-08-15 14:09:51');
/*!40000 ALTER TABLE `learning_tracks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_evidence`
--

DROP TABLE IF EXISTS `project_evidence`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_evidence` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `project_id` bigint unsigned NOT NULL,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `category` enum('architecture','linux','docker','network','ci_cd','monitoring','database','security','troubleshooting') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'docker',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT 'åšäº†ä»€ä¹ˆ',
  `technical_detail` text COLLATE utf8mb4_unicode_ci COMMENT 'æŠ€æœ¯ç»†èŠ‚',
  `result` text COLLATE utf8mb4_unicode_ci COMMENT 'ç»“æžœ/é‡åŒ–æŒ‡æ ‡',
  `deleted_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_evidence_user` (`user_id`),
  KEY `idx_evidence_project` (`project_id`),
  CONSTRAINT `fk_evidence_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`),
  CONSTRAINT `fk_evidence_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_evidence`
--

LOCK TABLES `project_evidence` WRITE;
/*!40000 ALTER TABLE `project_evidence` DISABLE KEYS */;
INSERT INTO `project_evidence` VALUES (1,1,1,'Docker å®¹å™¨åŒ– (multi-stage + éž root)','docker','å°† Flask åŽç«¯ä¸Ž Svelte å‰ç«¯å®¹å™¨åŒ–ï¼Œå‰ç«¯é‡‡ç”¨ multi-stage æž„å»ºã€‚','backend: python:3.12-slim + gunicorn éž root appuserï¼Œé¢„å»º /generated-posts å¹¶ chownï¼›frontend: node:22-alpine æž„å»º â†’ nginx:alpine æ‰˜ç®¡ distï¼ŒSPA fallback + /api åä»£åˆ° backend æœåŠ¡åã€‚','é•œåƒæž„å»ºæˆåŠŸï¼Œå®¹å™¨å†…ä»¥éž root è¿è¡Œï¼Œå†™ volume æƒé™æ­£å¸¸',NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50'),(2,1,1,'Docker Compose ç¼–æŽ’ (5 æœåŠ¡)','docker','backend/frontend/mysql/prometheus/grafana äº”æœåŠ¡ compose ç¼–æŽ’ã€‚','æ‰€æœ‰å®¿ä¸»ç«¯å£ä»…ç»‘å®š 127.0.0.1ï¼›mysql ç‹¬ç«‹ volume ä¸”æ— å®¿ä¸»ç«¯å£æ˜ å°„ï¼ˆä»…å®¹å™¨ç½‘ç»œï¼‰ï¼›ä¾èµ–å¥åº·æ£€æŸ¥æŽ’åºï¼ˆmysql healthy â†’ backendï¼‰ï¼›MySQL initdb è‡ªåŠ¨æ‰§è¡Œ schema+seedï¼›è¸©å‘ï¼šæŒ‚è½½ SQL 600 æƒé™å¯¼è‡´ entrypoint Permission deniedï¼Œchmod 644 ä¿®å¤ã€‚','5 å®¹å™¨å…¨éƒ¨ healthyï¼Œç”Ÿäº§ 3306/5000 å®Œå…¨éš”ç¦»',NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50'),(3,1,1,'GitHub Actions CI æµæ°´çº¿','ci_cd','ä¸‰ job CIï¼šbackend pytestï¼ˆmysql serviceï¼‰+ frontend check/build + docker åŒé•œåƒæž„å»ºã€‚','.github/workflows/ci.ymlï¼šbackend job ç”¨ services.mysql ç‹¬ç«‹æµ‹è¯•åº“ miglore_os_testï¼›frontend job npm ci + svelte-check + vite buildï¼›docker job ä¸²è¡Œæž„å»º backend/frontend é•œåƒã€‚','CI GREENï¼Œæ¯æ¬¡ push è‡ªåŠ¨éªŒè¯ 40+ åŽç«¯æµ‹è¯•ä¸Žå‰ç«¯æž„å»º',NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50'),(4,1,1,'Prometheus ç›‘æŽ§æŽ¥å…¥','monitoring','Prometheus æŠ“å– backend /metrics ä¸Žè‡ªèº«æŒ‡æ ‡ã€‚','prometheus.yml é™æ€é…ç½®ä¸¤ä¸ª jobï¼ˆprometheusã€backend:5001ï¼‰ï¼›backend é€šè¿‡ prometheus-client æš´éœ² http_requests_total Counter ä¸Ž latency Histogramã€‚','æ•…éšœå®žéªŒéªŒè¯ï¼šstop backend â†’ up=0 DOWNï¼Œstart â†’ æ¢å¤ UP=1',NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50'),(5,1,1,'Grafana å¯è§†åŒ– (provisioning)','monitoring','Grafana è‡ªåŠ¨æ³¨å†Œ Prometheus æ•°æ®æºå¹¶åŠ è½½ Miglore OS Overview ä»ªè¡¨ç›˜ã€‚','å£°æ˜Žå¼ provisioningï¼ˆdatasources.yml + dashboards providerï¼‰ï¼›ä»ªè¡¨ç›˜ 5 é¢æ¿ï¼šrequest rate / p95 latency / 5xx error rate / uptime / target statusï¼›grafana.ini çŽ¯å¢ƒå˜é‡é…ç½®å¼€å‘ä¸“ç”¨è´¦å·ã€‚','Grafanaâ†’Prometheus æŸ¥è¯¢é“¾è·¯å®žæµ‹ up è¿”å›ž backend=1/prometheus=1',NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50'),(6,1,1,'Flask åº”ç”¨æŒ‡æ ‡ (prometheus-client)','monitoring','ç»™ Flask API å¢žåŠ åŸºç¡€ Prometheus æŒ‡æ ‡ä¸Ž /metrics ç«¯ç‚¹ã€‚','before/after_request é’©å­ï¼šhttp_requests_total{method,path,status} Counter + http_request_duration_seconds Histogramï¼›path ç”¨ Flask url_rule æ¨¡æ¿é¿å…é«˜åŸºæ•°ã€‚','åŽ‹æµ‹éªŒè¯ï¼š60 æ¬¡ /api/health åŽ request rate 0.055â†’0.198 req/sï¼ˆ3.6x å¢žé•¿ï¼ŒæŒ‡æ ‡çœŸå®žï¼‰',NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50'),(7,1,1,'systemd æœåŠ¡å•å…ƒä¸Žå®ˆæŠ¤å…³ç³»','linux','ç”Ÿäº§ miglore.service ç»“æž„ä¸Ž systemd å¯¹ Gunicorn MainPID çš„å®ˆæŠ¤ã€‚','ç”Ÿäº§ systemd å•å…ƒï¼šWorkingDirectory=/var/www/miglore.funï¼ŒExecStart gunicorn --workers 2 --bind 127.0.0.1:5000ï¼ŒRestart=always + RestartSec=5ï¼ŒUser=ubuntuï¼›å¯¹æ¯” Docker restart policyï¼ˆunless-stopped å°Šé‡æ‰‹åŠ¨ stopã€always ä¼šæ‹‰èµ·ï¼‰ã€‚','æœåŠ¡è‡ª 6 æœˆèµ·è¿žç»­è¿è¡Œæœªä¸­æ–­ï¼Œç³»ç»Ÿé‡å¯å¯è‡ªåŠ¨æ‹‰èµ·',NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50'),(8,1,1,'Nginx åå‘ä»£ç†ä¸Ž SPA éƒ¨ç½²','architecture','Nginx æ‰¿è½½ç”Ÿäº§ç«™ç‚¹ä¸Žå¼€å‘å®¹å™¨å‰ç«¯ã€‚','ç”Ÿäº§ï¼š/static alias ç¼“å­˜ 30d + åŠ¨æ€ / proxy_pass 5000 + gzipï¼›å®¹å™¨å‰ç«¯ï¼šnginx.conf SPA try_files fallback + /api/ proxy_pass backend:5001 + é™æ€èµ„æº immutable ç¼“å­˜ã€‚','æœ¬åœ°ç›´è¿ž 127.0.0.1:80 HTTP 200ï¼ŒSPA è·¯ç”±ä¸Ž API ä»£ç†æ­£å¸¸',NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50'),(9,1,1,'å®¹å™¨æƒé™æ•…éšœæŽ’æŸ¥ (Linux)','troubleshooting','æŽ’æŸ¥ docker-entrypoint-initdb.d ä¸Ž provisioning æ–‡ä»¶æƒé™å¯¼è‡´çš„å®¹å™¨å¯åŠ¨å¤±è´¥ã€‚','ç—‡çŠ¶ï¼šmysql initdb Permission deniedã€prometheus config permission deniedã€grafana provisioning è¯»å–å¤±è´¥ï¼›ç”¨ ls -la å®šä½æ–‡ä»¶ 600 æƒé™ï¼Œå®¹å™¨å†…è¿›ç¨‹ï¼ˆmysql/nobody/appuserï¼‰æ— æ³•è¯»å–ï¼›ä¿®å¤ï¼šæ–‡ä»¶ 644 + ç›®å½• 755ï¼Œé‡å»ºå®¹å™¨éªŒè¯ã€‚','åŒç±»é—®é¢˜ä¸€æ¬¡å®šä½ï¼Œå®¹å™¨å…¨éƒ¨æ¢å¤ healthy',NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50'),(10,1,1,'CI é¦–æ¬¡å¤±è´¥åˆ†æžä¸Žä¿®å¤','ci_cd','CI é¦–è½®å¤±è´¥æ ¹å› å®šä½ï¼šnpm lockfile é”å®šè…¾è®¯å†…ç½‘é•œåƒï¼ŒGitHub æµ·å¤– runner æ— æ³•æ‹‰åŒ…ã€‚','æŽ’æŸ¥ï¼šæœ¬åœ°å…¨æµç¨‹é€šè¿‡ä½† CI å¤±è´¥ â†’ æ£€æŸ¥ package-lock.json å‘çŽ° 74 ä¸ª resolved æŒ‡å‘ http://mirrors.tencentyun.com/npm/ï¼›ä¿®å¤ï¼šé‡å»º lockfile + frontend/.npmrc å›ºå®š registry.npmmirror.comï¼ˆå…¬ç½‘å¯è¾¾ï¼‰ï¼›æœ¬åœ°æ¨¡æ‹Ÿ npm ci å…¨æµç¨‹éªŒè¯åŽé‡æŽ¨ã€‚','CI ç¬¬äºŒè½® GREENï¼Œæœªåˆ é™¤/é™ä½Žä»»ä½•æµ‹è¯•',NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50');
/*!40000 ALTER TABLE `project_evidence` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_milestones`
--

DROP TABLE IF EXISTS `project_milestones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_milestones` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `project_id` bigint unsigned NOT NULL,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` enum('done','current','todo') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'todo',
  `sort_order` int NOT NULL DEFAULT '0',
  `achieved_at` date DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_milestones_user` (`user_id`),
  KEY `idx_milestones_project` (`project_id`),
  CONSTRAINT `fk_milestones_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`),
  CONSTRAINT `fk_milestones_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_milestones`
--

LOCK TABLES `project_milestones` WRITE;
/*!40000 ALTER TABLE `project_milestones` DISABLE KEYS */;
INSERT INTO `project_milestones` VALUES (1,1,1,'Stage 1 Â· Architecture','done',1,'2026-08-15',NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50'),(2,1,1,'Stage 2 Â· Learning','done',2,'2026-08-15',NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50'),(3,1,1,'Stage 3 Â· Study Logs','done',3,'2026-08-15',NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50'),(4,1,1,'Stage 4 Â· Docker + Testing + CI','done',4,'2026-08-15',NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50'),(5,1,1,'Stage 5 Â· Prometheus + Grafana','done',5,'2026-08-15',NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50'),(6,1,1,'Stage 6 Â· Career + JD Analyzer','current',6,NULL,NULL,'2026-08-15 15:30:50','2026-08-15 15:30:50');
/*!40000 ALTER TABLE `project_milestones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `projects`
--

DROP TABLE IF EXISTS `projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projects` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `tech_stack` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `repo_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` enum('planning','active','paused','done','archived') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'active',
  `progress` int NOT NULL DEFAULT '0' COMMENT '0-100',
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `featured` tinyint NOT NULL DEFAULT '0' COMMENT 'é¦–é¡µ Featured æ ‡è®°',
  `deleted_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_projects_user` (`user_id`),
  KEY `idx_projects_user_featured` (`user_id`,`featured`),
  KEY `idx_projects_user_status` (`user_id`,`status`),
  CONSTRAINT `fk_projects_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `projects`
--

LOCK TABLES `projects` WRITE;
/*!40000 ALTER TABLE `projects` DISABLE KEYS */;
INSERT INTO `projects` VALUES (1,1,'Miglore OS','ä¸ªäººæˆé•¿æ“ä½œç³»ç»Ÿ â€” å­¦ä¹ ã€æ±‚èŒã€é¡¹ç›®ã€ä»»åŠ¡ä¸€ä½“åŒ–','Svelte 5 Â· Flask Â· MySQL Â· Docker Â· Prometheus Â· Grafana',NULL,'active',20,NULL,NULL,1,NULL,'2026-08-15 14:09:51','2026-08-15 15:30:50'),(2,1,'DevOps Lab','Nginx / systemd / Docker Compose å®žæ“å®žéªŒå®¤','Nginx Â· Docker Â· MySQL',NULL,'active',80,NULL,NULL,1,NULL,'2026-08-15 14:09:51','2026-08-15 14:09:51');
/*!40000 ALTER TABLE `projects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `skills`
--

DROP TABLE IF EXISTS `skills`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `skills` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `track_id` bigint unsigned DEFAULT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `level` tinyint NOT NULL DEFAULT '1' COMMENT '1-5',
  `target_level` tinyint NOT NULL DEFAULT '5' COMMENT '1-5',
  `status` enum('learning','learned','idle') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'learning',
  `deleted_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_skills_user` (`user_id`),
  KEY `idx_skills_track` (`track_id`),
  CONSTRAINT `fk_skills_track` FOREIGN KEY (`track_id`) REFERENCES `learning_tracks` (`id`),
  CONSTRAINT `fk_skills_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `skills`
--

LOCK TABLES `skills` WRITE;
/*!40000 ALTER TABLE `skills` DISABLE KEYS */;
INSERT INTO `skills` VALUES (1,1,1,'Linux',4,5,'learned',NULL,'2026-08-15 14:09:51','2026-08-15 15:15:19'),(2,1,1,'è®¡ç®—æœºç½‘ç»œ',3,5,'learning',NULL,'2026-08-15 14:09:51','2026-08-15 14:09:51'),(3,1,1,'systemd',4,5,'learned',NULL,'2026-08-15 14:09:51','2026-08-15 15:15:19'),(4,1,1,'Nginx',4,5,'learned',NULL,'2026-08-15 14:09:51','2026-08-15 15:15:19'),(5,1,1,'Docker',4,5,'learned',NULL,'2026-08-15 14:09:51','2026-08-15 15:15:19'),(6,1,1,'CI/CD',2,5,'learning',NULL,'2026-08-15 14:09:51','2026-08-15 14:09:51'),(7,1,1,'Monitoring',1,5,'learning',NULL,'2026-08-15 14:09:51','2026-08-15 14:09:51'),(8,1,1,'Kubernetes',1,5,'learning',NULL,'2026-08-15 14:09:51','2026-08-15 14:09:51');
/*!40000 ALTER TABLE `skills` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `study_logs`
--

DROP TABLE IF EXISTS `study_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `study_logs` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `log_date` date NOT NULL,
  `task_id` bigint unsigned DEFAULT NULL COMMENT 'å…³è”å­¦ä¹ ä»»åŠ¡ (migration 002)',
  `title` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'è®°å½•æ ‡é¢˜, é»˜è®¤å–ä»»åŠ¡æ ‡é¢˜',
  `content` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `duration_min` int DEFAULT NULL,
  `mood` tinyint DEFAULT NULL COMMENT '1-5',
  `track_id` bigint unsigned DEFAULT NULL,
  `project_id` bigint unsigned DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_logs_user` (`user_id`),
  KEY `idx_logs_user_date` (`user_id`,`log_date`),
  KEY `idx_logs_task` (`task_id`),
  KEY `idx_logs_track` (`track_id`),
  KEY `idx_logs_project` (`project_id`),
  CONSTRAINT `fk_logs_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`),
  CONSTRAINT `fk_logs_task` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`),
  CONSTRAINT `fk_logs_track` FOREIGN KEY (`track_id`) REFERENCES `learning_tracks` (`id`),
  CONSTRAINT `fk_logs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `study_logs`
--

LOCK TABLES `study_logs` WRITE;
/*!40000 ALTER TABLE `study_logs` DISABLE KEYS */;
INSERT INTO `study_logs` VALUES (1,1,'2026-08-15',2,'systemd','容器环境测试：systemd 对 Gunicorn MainPID 的守护。',NULL,NULL,1,NULL,NULL,'2026-08-15 14:10:33','2026-08-15 14:10:33');
/*!40000 ALTER TABLE `study_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tasks`
--

DROP TABLE IF EXISTS `tasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tasks` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL,
  `type` enum('learning','project','daily') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'daily',
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `status` enum('todo','in_progress','done','cancelled') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'todo',
  `priority` tinyint NOT NULL DEFAULT '2' COMMENT '1ä½Ž 2ä¸­ 3é«˜',
  `due_date` date DEFAULT NULL,
  `track_id` bigint unsigned DEFAULT NULL,
  `skill_id` bigint unsigned DEFAULT NULL,
  `project_id` bigint unsigned DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `sort_order` int NOT NULL DEFAULT '0',
  `deleted_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_tasks_user` (`user_id`),
  KEY `idx_tasks_user_status` (`user_id`,`status`),
  KEY `idx_tasks_user_due` (`user_id`,`due_date`),
  KEY `idx_tasks_project` (`project_id`),
  KEY `idx_tasks_track` (`track_id`),
  KEY `fk_tasks_skill` (`skill_id`),
  CONSTRAINT `fk_tasks_project` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`),
  CONSTRAINT `fk_tasks_skill` FOREIGN KEY (`skill_id`) REFERENCES `skills` (`id`),
  CONSTRAINT `fk_tasks_track` FOREIGN KEY (`track_id`) REFERENCES `learning_tracks` (`id`),
  CONSTRAINT `fk_tasks_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tasks`
--

LOCK TABLES `tasks` WRITE;
/*!40000 ALTER TABLE `tasks` DISABLE KEYS */;
INSERT INTO `tasks` VALUES (1,1,'learning','Linux è¿›ç¨‹ç®¡ç†','é˜¶æ®µ1 Â· Linux åŸºç¡€','done',2,'2026-06-10',1,1,NULL,'2026-06-10 20:00:00',1,NULL,'2026-08-15 14:09:51','2026-08-15 14:09:51'),(2,1,'learning','systemd','é˜¶æ®µ3 Â· systemd','done',3,'2026-07-05',1,3,NULL,'2026-07-05 21:00:00',2,NULL,'2026-08-15 14:09:51','2026-08-15 14:09:51'),(3,1,'learning','journalctl','é˜¶æ®µ3 Â· systemd','done',2,'2026-07-08',1,3,NULL,'2026-07-08 19:30:00',3,NULL,'2026-08-15 14:09:51','2026-08-15 14:09:51'),(4,1,'learning','Nginx Reverse Proxy','é˜¶æ®µ4 Â· Nginx','done',3,'2026-07-20',1,4,NULL,'2026-07-20 22:00:00',4,NULL,'2026-08-15 14:09:51','2026-08-15 14:09:51'),(5,1,'learning','Docker Compose','é˜¶æ®µ5 Â· Docker','done',3,'2026-08-01',1,5,NULL,'2026-08-01 21:30:00',5,NULL,'2026-08-15 14:09:51','2026-08-15 14:09:51'),(6,1,'learning','Docker Network','é˜¶æ®µ5 Â· Docker','done',3,'2026-08-15',1,5,NULL,'2026-08-15 16:04:56',6,NULL,'2026-08-15 14:09:51','2026-08-15 16:04:56'),(7,1,'learning','GitHub Actions','é˜¶æ®µ6 Â· CI/CD','in_progress',2,'2026-08-16',1,6,NULL,NULL,7,NULL,'2026-08-15 14:09:51','2026-08-15 14:09:51'),(8,1,'learning','Prometheus','é˜¶æ®µ7 Â· Monitoring','todo',2,'2026-08-17',1,7,NULL,NULL,8,NULL,'2026-08-15 14:09:51','2026-08-15 14:09:51'),(9,1,'learning','Grafana','é˜¶æ®µ7 Â· Monitoring','todo',1,'2026-08-18',1,7,NULL,NULL,9,NULL,'2026-08-15 14:09:51','2026-08-15 14:09:51'),(10,1,'learning','Kubernetes åŸºç¡€','é˜¶æ®µ8 Â· Kubernetes','todo',2,'2026-08-20',1,8,NULL,NULL,10,NULL,'2026-08-15 14:09:51','2026-08-15 14:09:51');
/*!40000 ALTER TABLE `tasks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `display_name` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `avatar_url` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `career_goal` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'é¦–é¡µ Hero èŒä¸šç›®æ ‡',
  `deleted_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'miglore','miglore@miglore.fun','seed-only-no-login','miglore',NULL,'DevOps å·¥ç¨‹å¸ˆ',NULL,'2026-08-15 14:09:51','2026-08-15 14:09:51');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'miglore_os'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-15 16:13:47
