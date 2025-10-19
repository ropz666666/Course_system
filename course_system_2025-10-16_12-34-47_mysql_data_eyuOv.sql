-- MySQL dump 10.13  Distrib 8.0.36, for Linux (x86_64)
--
-- Host: localhost    Database: course_system
-- ------------------------------------------------------
-- Server version	8.0.36

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
-- Table structure for table `agent`
--

DROP TABLE IF EXISTS `agent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `agent` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL DEFAULT (uuid()),
  `user_uuid` varchar(50) NOT NULL,
  `name` varchar(32) DEFAULT NULL,
  `cover_image` varchar(255) DEFAULT NULL,
  `description` text,
  `spl` longtext,
  `spl_form` longtext,
  `spl_chain` longtext,
  `welcome_info` text,
  `sample_query` text,
  `type` int DEFAULT '1',
  `status` int DEFAULT '1',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `parameters` text,
  `deploy_plugin_uuid` varchar(50) DEFAULT NULL,
  `long_memory` int DEFAULT '0',
  `short_memory` int DEFAULT '0',
  `suggestion` tinyint(1) DEFAULT '0',
  `output_chaining` tinyint(1) DEFAULT '1',
  `tags` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `user_uuid` (`user_uuid`),
  CONSTRAINT `agent_ibfk_1` FOREIGN KEY (`user_uuid`) REFERENCES `user` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=199 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `agent`
--

LOCK TABLES `agent` WRITE;
/*!40000 ALTER TABLE `agent` DISABLE KEYS */;
/*!40000 ALTER TABLE `agent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `agent_knowledge_map`
--

DROP TABLE IF EXISTS `agent_knowledge_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `agent_knowledge_map` (
  `agent_uuid` varchar(50) NOT NULL,
  `knowledge_base_uuid` varchar(50) NOT NULL,
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`agent_uuid`,`knowledge_base_uuid`),
  KEY `knowledge_base_uuid` (`knowledge_base_uuid`),
  CONSTRAINT `agent_knowledge_map_ibfk_1` FOREIGN KEY (`agent_uuid`) REFERENCES `agent` (`uuid`),
  CONSTRAINT `agent_knowledge_map_ibfk_2` FOREIGN KEY (`knowledge_base_uuid`) REFERENCES `knowledge_base` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `agent_knowledge_map`
--

LOCK TABLES `agent_knowledge_map` WRITE;
/*!40000 ALTER TABLE `agent_knowledge_map` DISABLE KEYS */;
/*!40000 ALTER TABLE `agent_knowledge_map` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `agent_plugin_map`
--

DROP TABLE IF EXISTS `agent_plugin_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `agent_plugin_map` (
  `agent_uuid` varchar(50) NOT NULL,
  `plugin_uuid` varchar(50) NOT NULL,
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`agent_uuid`,`plugin_uuid`),
  KEY `plugin_uuid` (`plugin_uuid`),
  CONSTRAINT `agent_plugin_map_ibfk_1` FOREIGN KEY (`agent_uuid`) REFERENCES `agent` (`uuid`),
  CONSTRAINT `agent_plugin_map_ibfk_2` FOREIGN KEY (`plugin_uuid`) REFERENCES `plugin` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `agent_plugin_map`
--

LOCK TABLES `agent_plugin_map` WRITE;
/*!40000 ALTER TABLE `agent_plugin_map` DISABLE KEYS */;
/*!40000 ALTER TABLE `agent_plugin_map` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `agent_publishment`
--

DROP TABLE IF EXISTS `agent_publishment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `agent_publishment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL DEFAULT (uuid()),
  `agent_uuid` varchar(50) NOT NULL,
  `channel_uuid` varchar(50) NOT NULL,
  `status` enum('pending','success','failed') DEFAULT 'pending',
  `publish_config` json DEFAULT NULL,
  `published_at` timestamp NULL DEFAULT NULL,
  `published_by` varchar(50) NOT NULL,
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `agent_uuid` (`agent_uuid`),
  KEY `channel_uuid` (`channel_uuid`),
  KEY `published_by` (`published_by`),
  CONSTRAINT `agent_publishment_ibfk_1` FOREIGN KEY (`agent_uuid`) REFERENCES `agent` (`uuid`),
  CONSTRAINT `agent_publishment_ibfk_2` FOREIGN KEY (`channel_uuid`) REFERENCES `publish_channel` (`uuid`),
  CONSTRAINT `agent_publishment_ibfk_3` FOREIGN KEY (`published_by`) REFERENCES `user` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `agent_publishment`
--

LOCK TABLES `agent_publishment` WRITE;
/*!40000 ALTER TABLE `agent_publishment` DISABLE KEYS */;
/*!40000 ALTER TABLE `agent_publishment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `collection`
--

DROP TABLE IF EXISTS `collection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `collection` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL DEFAULT (uuid()),
  `name` varchar(225) DEFAULT NULL,
  `file_url` text,
  `processing_method` varchar(32) DEFAULT NULL,
  `training_mode` varchar(32) DEFAULT NULL,
  `status` int DEFAULT '1',
  `knowledge_base_uuid` varchar(50) NOT NULL,
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `knowledge_base_uuid` (`knowledge_base_uuid`),
  CONSTRAINT `collection_ibfk_1` FOREIGN KEY (`knowledge_base_uuid`) REFERENCES `knowledge_base` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=494 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `collection`
--

LOCK TABLES `collection` WRITE;
/*!40000 ALTER TABLE `collection` DISABLE KEYS */;
/*!40000 ALTER TABLE `collection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `conversation`
--

DROP TABLE IF EXISTS `conversation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `conversation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL DEFAULT (uuid()),
  `name` varchar(32) DEFAULT NULL,
  `chat_history` longtext,
  `chat_parameters` text,
  `short_memory` text,
  `long_memory` text,
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `user_uuid` varchar(50) NOT NULL,
  `agent_uuid` varchar(50) NOT NULL,
  `knowledge_base_uuid` varchar(50) DEFAULT NULL,
  `collection_uuid` varchar(50) DEFAULT NULL,
  `status` int DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `user_uuid` (`user_uuid`),
  KEY `agent_uuid` (`agent_uuid`),
  KEY `conservation_knowledge_base_uuid_fk` (`knowledge_base_uuid`),
  KEY `conservation_collection_uuid_fk` (`collection_uuid`),
  CONSTRAINT `conservation_collection_uuid_fk` FOREIGN KEY (`collection_uuid`) REFERENCES `collection` (`uuid`),
  CONSTRAINT `conservation_knowledge_base_uuid_fk` FOREIGN KEY (`knowledge_base_uuid`) REFERENCES `knowledge_base` (`uuid`) ON DELETE CASCADE,
  CONSTRAINT `conversation_ibfk_1` FOREIGN KEY (`user_uuid`) REFERENCES `user` (`uuid`),
  CONSTRAINT `conversation_ibfk_2` FOREIGN KEY (`agent_uuid`) REFERENCES `agent` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=453 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `conversation`
--

LOCK TABLES `conversation` WRITE;
/*!40000 ALTER TABLE `conversation` DISABLE KEYS */;
/*!40000 ALTER TABLE `conversation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `embedding`
--

DROP TABLE IF EXISTS `embedding`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `embedding` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL DEFAULT (uuid()),
  `vector` text,
  `text_block_uuid` varchar(50) NOT NULL,
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `text_block_uuid` (`text_block_uuid`),
  CONSTRAINT `embedding_ibfk_1` FOREIGN KEY (`text_block_uuid`) REFERENCES `text_block` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=277 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `embedding`
--

LOCK TABLES `embedding` WRITE;
/*!40000 ALTER TABLE `embedding` DISABLE KEYS */;
/*!40000 ALTER TABLE `embedding` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `graph_collection`
--

DROP TABLE IF EXISTS `graph_collection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `graph_collection` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL DEFAULT (uuid()),
  `name` varchar(32) DEFAULT NULL,
  `entities` longtext,
  `relationships` longtext,
  `communities` longtext,
  `status` int DEFAULT '1',
  `knowledge_base_uuid` varchar(50) NOT NULL,
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `knowledge_base_uuid` (`knowledge_base_uuid`),
  CONSTRAINT `graph_collection_ibfk_1` FOREIGN KEY (`knowledge_base_uuid`) REFERENCES `knowledge_base` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `graph_collection`
--

LOCK TABLES `graph_collection` WRITE;
/*!40000 ALTER TABLE `graph_collection` DISABLE KEYS */;
/*!40000 ALTER TABLE `graph_collection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `knowledge_base`
--

DROP TABLE IF EXISTS `knowledge_base`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `knowledge_base` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL DEFAULT (uuid()),
  `user_uuid` varchar(50) NOT NULL,
  `name` varchar(32) DEFAULT NULL,
  `cover_image` varchar(255) DEFAULT NULL,
  `description` text,
  `embedding_model` text,
  `status` int DEFAULT '1',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `user_uuid` (`user_uuid`),
  CONSTRAINT `knowledge_base_ibfk_1` FOREIGN KEY (`user_uuid`) REFERENCES `user` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=468 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `knowledge_base`
--

LOCK TABLES `knowledge_base` WRITE;
/*!40000 ALTER TABLE `knowledge_base` DISABLE KEYS */;
/*!40000 ALTER TABLE `knowledge_base` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `llm_model`
--

DROP TABLE IF EXISTS `llm_model`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `llm_model` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL DEFAULT (uuid()),
  `type` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL,
  `group_name` varchar(100) DEFAULT NULL,
  `status` int DEFAULT '1',
  `provider_uuid` varchar(50) NOT NULL,
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `provider_uuid` (`provider_uuid`),
  CONSTRAINT `llm_model_ibfk_1` FOREIGN KEY (`provider_uuid`) REFERENCES `llm_provider` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `llm_model`
--

LOCK TABLES `llm_model` WRITE;
/*!40000 ALTER TABLE `llm_model` DISABLE KEYS */;
/*!40000 ALTER TABLE `llm_model` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `llm_provider`
--

DROP TABLE IF EXISTS `llm_provider`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `llm_provider` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL DEFAULT (uuid()),
  `user_uuid` varchar(50) NOT NULL,
  `name` varchar(255) NOT NULL,
  `api_key` varchar(255) NOT NULL,
  `api_url` varchar(512) NOT NULL,
  `document_url` varchar(512) DEFAULT NULL,
  `status` int DEFAULT '1',
  `llm_model_url` varchar(512) DEFAULT NULL,
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `name` (`name`),
  KEY `user_uuid` (`user_uuid`),
  CONSTRAINT `llm_provider_ibfk_1` FOREIGN KEY (`user_uuid`) REFERENCES `user` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `llm_provider`
--

LOCK TABLES `llm_provider` WRITE;
/*!40000 ALTER TABLE `llm_provider` DISABLE KEYS */;
/*!40000 ALTER TABLE `llm_provider` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `plugin`
--

DROP TABLE IF EXISTS `plugin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plugin` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL DEFAULT (uuid()),
  `user_uuid` varchar(50) NOT NULL,
  `name` varchar(32) DEFAULT NULL,
  `cover_image` varchar(255) DEFAULT NULL,
  `description` text,
  `server_url` text,
  `header_info` text,
  `return_info` text,
  `api_parameter` text,
  `status` int DEFAULT '1',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `user_uuid` (`user_uuid`),
  CONSTRAINT `plugin_ibfk_1` FOREIGN KEY (`user_uuid`) REFERENCES `user` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=107 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plugin`
--

LOCK TABLES `plugin` WRITE;
/*!40000 ALTER TABLE `plugin` DISABLE KEYS */;
/*!40000 ALTER TABLE `plugin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `publish_channel`
--

DROP TABLE IF EXISTS `publish_channel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `publish_channel` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL DEFAULT (uuid()),
  `name` varchar(50) NOT NULL,
  `description` text,
  `is_active` tinyint(1) DEFAULT '1',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `publish_channel`
--

LOCK TABLES `publish_channel` WRITE;
/*!40000 ALTER TABLE `publish_channel` DISABLE KEYS */;
/*!40000 ALTER TABLE `publish_channel` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `text_block`
--

DROP TABLE IF EXISTS `text_block`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `text_block` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL DEFAULT (uuid()),
  `content` text,
  `collection_uuid` varchar(50) NOT NULL,
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `collection_uuid` (`collection_uuid`),
  CONSTRAINT `text_block_ibfk_1` FOREIGN KEY (`collection_uuid`) REFERENCES `collection` (`uuid`)
) ENGINE=InnoDB AUTO_INCREMENT=294 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `text_block`
--

LOCK TABLES `text_block` WRITE;
/*!40000 ALTER TABLE `text_block` DISABLE KEYS */;
/*!40000 ALTER TABLE `text_block` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL,
  `username` varchar(50) NOT NULL,
  `nickname` varchar(20) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `salt` varchar(5) DEFAULT NULL,
  `email` varchar(50) NOT NULL,
  `is_superuser` tinyint(1) DEFAULT '0',
  `is_staff` tinyint(1) DEFAULT '0',
  `status` int DEFAULT '1',
  `is_multi_login` tinyint(1) DEFAULT '0',
  `avatar` varchar(255) DEFAULT NULL,
  `phone` varchar(11) DEFAULT NULL,
  `join_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_login_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `created_time` datetime NOT NULL COMMENT '创建时间',
  `updated_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `nickname` (`nickname`),
  KEY `username_2` (`username`),
  KEY `email_2` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_agent_interaction`
--

DROP TABLE IF EXISTS `user_agent_interaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_agent_interaction` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL DEFAULT (uuid()),
  `user_uuid` varchar(50) NOT NULL,
  `agent_uuid` varchar(50) NOT NULL,
  `rating_value` decimal(2,1) DEFAULT NULL,
  `is_favorite` tinyint(1) DEFAULT '0',
  `usage_count` int DEFAULT '0',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  UNIQUE KEY `user_uuid` (`user_uuid`,`agent_uuid`),
  KEY `agent_uuid` (`agent_uuid`),
  CONSTRAINT `user_agent_interaction_ibfk_1` FOREIGN KEY (`user_uuid`) REFERENCES `user` (`uuid`),
  CONSTRAINT `user_agent_interaction_ibfk_2` FOREIGN KEY (`agent_uuid`) REFERENCES `agent` (`uuid`),
  CONSTRAINT `user_agent_interaction_chk_1` CHECK ((`rating_value` between 0 and 5))
) ENGINE=InnoDB AUTO_INCREMENT=147 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_agent_interaction`
--

LOCK TABLES `user_agent_interaction` WRITE;
/*!40000 ALTER TABLE `user_agent_interaction` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_agent_interaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_agent_map`
--

DROP TABLE IF EXISTS `user_agent_map`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_agent_map` (
  `user_uuid` varchar(50) NOT NULL,
  `agent_uuid` varchar(50) NOT NULL,
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`user_uuid`,`agent_uuid`),
  KEY `agent_uuid` (`agent_uuid`),
  CONSTRAINT `user_agent_map_ibfk_1` FOREIGN KEY (`user_uuid`) REFERENCES `user` (`uuid`),
  CONSTRAINT `user_agent_map_ibfk_2` FOREIGN KEY (`agent_uuid`) REFERENCES `agent` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_agent_map`
--

LOCK TABLES `user_agent_map` WRITE;
/*!40000 ALTER TABLE `user_agent_map` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_agent_map` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'course_system'
--

--
-- Dumping routines for database 'course_system'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-16 12:34:48
