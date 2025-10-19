-- User
CREATE TABLE user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,          -- Assuming 'id' is an auto-incremented primary key
    uuid VARCHAR(50) NOT NULL UNIQUE,              -- 'uuid' column with a unique constraint
    username VARCHAR(50) NOT NULL UNIQUE,          -- 'username' column with a unique constraint and index
    nickname VARCHAR(20) UNIQUE,                   -- 'nickname' column with a unique constraint
    password VARCHAR(255),                         -- 'password' column (nullable)
    salt VARCHAR(5),                               -- 'salt' column (nullable)
    email VARCHAR(50) NOT NULL UNIQUE,             -- 'email' column with unique constraint and index
    is_superuser BOOLEAN DEFAULT FALSE,            -- 'is_superuser' column with default value 'false'
    is_staff BOOLEAN DEFAULT FALSE,                -- 'is_staff' column with default value 'false'
    status INT DEFAULT 1,                          -- 'status' column with default value '1' (normal)
    is_multi_login BOOLEAN DEFAULT FALSE,          -- 'is_multi_login' column with default value 'false'
    avatar VARCHAR(255),                           -- 'avatar' column (nullable)
    phone VARCHAR(11),                             -- 'phone' column (nullable)
    join_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 'join_time' column with default current timestamp
    last_login_time TIMESTAMP DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP, -- 'last_login_time' column with automatic update
    INDEX (username),                              -- Index for 'username'
    INDEX (email),                              -- Index for 'email'
    `created_time` datetime     NOT NULL COMMENT '创建时间',
    `updated_time` datetime DEFAULT NULL COMMENT '更新时间'
);

INSERT INTO `user` (id, uuid, username, nickname, password, salt, email, is_superuser, is_staff, status, is_multi_login, avatar, phone, join_time, last_login_time, created_time, updated_time)
VALUES (1, 'af4c804f-3966-4949-ace2-3bb7416ea926', 'admin', '用户88888', '$2b$12$RJXAtJodRw37ZQGxTPlu0OH.aN5lNXG6yvC4Tp9GIQEBmMY/YCc.m', 'bcNjV', 'admin@example.com', 1, 1, 1, 0, null, null, NOW(), NOW(), NOW(), NOW());

INSERT INTO `user` (id, uuid, username, nickname, password, salt, email, is_superuser, is_staff, status, is_multi_login, avatar, phone, join_time, last_login_time, created_time, updated_time)
VALUES (2, 'bf4c804f-3966-4949-ace2-3bb7416ea829', 'cheng', '用户66666', '$2b$12$RJXAtJodRw37ZQGxTPlu0OH.aN5lNXG6yvC4Tp9GIQEBmMY/YCc.m', 'bcNjV', 'cy@example.com', 1, 1, 1, 0, null, null, NOW(), NOW(), NOW(), NOW());

-- User 和 Agent 使用多对多关系中间表
CREATE TABLE `user_agent_map` (
    `user_uuid` VARCHAR(50) NOT NULL,
    `agent_uuid` VARCHAR(50) NOT NULL,
    `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',  -- Automatically set the current timestamp when a record is created
    `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',  -- Automatically set and update the timestamp when a record is modified
    FOREIGN KEY (`user_uuid`) REFERENCES `user`(`uuid`),
    FOREIGN KEY (`agent_uuid`) REFERENCES `agent`(`uuid`),
    PRIMARY KEY (`user_uuid`, `agent_uuid`)
);

-- Agent 表
CREATE TABLE `agent` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `uuid` VARCHAR(50) UNIQUE NOT NULL DEFAULT (UUID()),
    `user_uuid` VARCHAR(50) NOT NULL,
    `name` VARCHAR(32),
    `cover_image` VARCHAR(255),
    `description` TEXT,
    `spl` TEXT,
    `spl_form` TEXT,
    `spl_chain` TEXT,
    `welcome_info` TEXT,
    `sample_query` TEXT,
    `variables` Text,
    `type` INT DEFAULT 1,
    `status` INT DEFAULT 1,
    `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',  -- Automatically set the current timestamp when a record is created
    `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',  -- Automatically set and update the timestamp when a record is modified
    FOREIGN KEY (`user_uuid`) REFERENCES `user`(`uuid`)
);

-- Conservation 表
CREATE TABLE `conversation` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `uuid` VARCHAR(50) UNIQUE NOT NULL DEFAULT (UUID()),
    `name` VARCHAR(32),
    `chat_history` TEXT,
    `chat_parameters` TEXT,
    `short_memory` TEXT,
    `long_memory` TEXT,
    `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',  -- Automatically set the current timestamp when a record is created
    `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',  -- Automatically set and update the timestamp when a record is modified
    `user_uuid` VARCHAR(50) NOT NULL,
    `agent_uuid` VARCHAR(50) NOT NULL,
    `knowledge_base_uuid` VARCHAR(50) NOT NULL,
    FOREIGN KEY (`user_uuid`) REFERENCES `user`(`uuid`),
    FOREIGN KEY (`agent_uuid`) REFERENCES `agent`(`uuid`),
    FOREIGN KEY (`knowledge_base_uuid`) REFERENCES `knowledge_base`(`uuid`)
);

-- KnowledgeBase 表
CREATE TABLE `knowledge_base` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `uuid` VARCHAR(50) UNIQUE NOT NULL DEFAULT (UUID()),
    `user_uuid` VARCHAR(50) NOT NULL,
    `name` VARCHAR(32),
    `cover_image` VARCHAR(255),
    `description` TEXT,
    `embedding_model` TEXT,
    `status` INT DEFAULT 1,
    `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',  -- Automatically set the current timestamp when a record is created
    `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',  -- Automatically set and update the timestamp when a record is modified
    FOREIGN KEY (`user_uuid`) REFERENCES `user`(`uuid`)
);

-- Agent 和 KnowledgeBase 多对多关系中间表
CREATE TABLE `agent_knowledge_map` (
    `agent_uuid` VARCHAR(50) NOT NULL,
    `knowledge_base_uuid` VARCHAR(50) NOT NULL,
    `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',  -- Automatically set the current timestamp when a record is created
    `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',  -- Automatically set and update the timestamp when a record is modified
    FOREIGN KEY (`agent_uuid`) REFERENCES `agent`(`uuid`),
    FOREIGN KEY (`knowledge_base_uuid`) REFERENCES `knowledge_base`(`uuid`),
    PRIMARY KEY (`agent_uuid`, `knowledge_base_uuid`)
);

-- Plugin 表
CREATE TABLE `plugin` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `uuid` VARCHAR(50) UNIQUE NOT NULL DEFAULT (UUID()),
    `user_uuid` VARCHAR(50) NOT NULL,
    `name` VARCHAR(32),
    `cover_image` VARCHAR(255),
    `description` TEXT,
    `server_url` TEXT,
    `header_info` TEXT,
    `return_info` TEXT,
    `api_parameter` TEXT,
    `status` INT DEFAULT 1,
    `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',  -- Automatically set the current timestamp when a record is created
    `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',  -- Automatically set and update the timestamp when a record is modified
    FOREIGN KEY (`user_uuid`) REFERENCES `user`(`uuid`)
);

-- Agent 和 Plugin 多对多关系中间表
CREATE TABLE `agent_plugin_map` (
    `agent_uuid` VARCHAR(50) NOT NULL,
    `plugin_uuid` VARCHAR(50) NOT NULL,
    `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',  -- Automatically set the current timestamp when a record is created
    `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',  -- Automatically set and update the timestamp when a record is modified
    FOREIGN KEY (`agent_uuid`) REFERENCES `agent`(`uuid`),
    FOREIGN KEY (`plugin_uuid`) REFERENCES `plugin`(`uuid`),
    PRIMARY KEY (`agent_uuid`, `plugin_uuid`)
);

-- Collection 表
CREATE TABLE `collection` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `uuid` VARCHAR(50) UNIQUE NOT NULL DEFAULT (UUID()),
    `name` VARCHAR(32),
    `file_url` TEXT,
    `processing_method` VARCHAR(32),
    `training_mode` VARCHAR(32),
    `status` INT DEFAULT 1,
    `knowledge_base_uuid` VARCHAR(50) NOT NULL,
    `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',  -- Automatically set the current timestamp when a record is created
    `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',  -- Automatically set and update the timestamp when a record is modified
    FOREIGN KEY (`knowledge_base_uuid`) REFERENCES `knowledge_base`(`uuid`)
);

-- GraphCollection 表
CREATE TABLE `graph_collection` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `uuid` VARCHAR(50) UNIQUE NOT NULL DEFAULT (UUID()),
    `name` VARCHAR(32),
    `entities` LONGTEXT,
    `relationships` LONGTEXT,
    `communities` LONGTEXT,
    `status` INT DEFAULT 1,
    `knowledge_base_uuid` VARCHAR(50) NOT NULL,
    `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',  -- Automatically set the current timestamp when a record is created
    `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',  -- Automatically set and update the timestamp when a record is modified
    FOREIGN KEY (`knowledge_base_uuid`) REFERENCES `knowledge_base`(`uuid`)
);

-- TextBlock 表
CREATE TABLE `text_block` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `uuid` VARCHAR(50) UNIQUE NOT NULL DEFAULT (UUID()),
    `content` TEXT,
    `collection_uuid` VARCHAR(50) NOT NULL,
    `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',  -- Automatically set the current timestamp when a record is created
    `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',  -- Automatically set and update the timestamp when a record is modified
    FOREIGN KEY (`collection_uuid`) REFERENCES `collection`(`uuid`)
);

-- Embedding 表
CREATE TABLE `embedding` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `uuid` VARCHAR(50) UNIQUE NOT NULL DEFAULT (UUID()),
    `vector` TEXT,
    `text_block_uuid` VARCHAR(50) NOT NULL,
    `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',  -- Automatically set the current timestamp when a record is created
    `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',  -- Automatically set and update the timestamp when a record is modified
    FOREIGN KEY (`text_block_uuid`) REFERENCES `text_block`(`uuid`)
);

CREATE TABLE llm_provider (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `uuid` VARCHAR(50) UNIQUE NOT NULL DEFAULT (UUID()),
    user_uuid VARCHAR(50) NOT NULL,
    `name` VARCHAR(255) NOT NULL UNIQUE,         -- 名称（唯一约束）
    api_key VARCHAR(255),             -- API密钥（建议加密存储）
    api_url VARCHAR(512),             -- API地址
    document_url VARCHAR(512),                 -- 文档URL
    `status` INT DEFAULT 1,
    llm_model_url VARCHAR(512),                    -- 模型URL
    `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',  -- Automatically set the current timestamp when a record is created
    `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',  -- Automatically set and update the timestamp when a record is modified
    FOREIGN KEY (user_uuid) REFERENCES user(`uuid`)
);

CREATE TABLE llm_model (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `uuid` VARCHAR(50) UNIQUE NOT NULL DEFAULT (UUID()),
    type VARCHAR(50) NOT NULL,           -- 模型类型（如：text-generation/image-generation）
    `name` VARCHAR(255) NOT NULL,          -- 模型名称
    group_name VARCHAR(100),                   -- 分组名称
    `status` INT DEFAULT 1,
    provider_uuid VARCHAR(50) NOT NULL,                  -- 外键关联提供商
    `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',  -- Automatically set the current timestamp when a record is created
    `updated_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',  -- Automatically set and update the timestamp when a record is modified
    FOREIGN KEY (provider_uuid) REFERENCES llm_provider(`uuid`)
);


INSERT INTO llm_provider (
    user_uuid,
    name,
    api_key,
    api_url,
    document_url,
    llm_model_url
) VALUES
    ('user-1234', 'OpenAI', 'sk-1234567890abcdef', 'https://api.openai.com/v1', 'https://platform.openai.com/docs', 'https://api.openai.com/v1/models'),
    ('user-5678', 'Anthropic', 'sk-abcdef1234567890', 'https://api.anthropic.com/v1', 'https://docs.anthropic.com', 'https://api.anthropic.com/v1/models'),
    ('user-9101', 'Cohere', 'sk-0987654321abcdef', 'https://api.cohere.ai/v1', 'https://docs.cohere.ai', 'https://api.cohere.ai/v1/models');
