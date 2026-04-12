-- ============================================================
-- RapidAid Database Schema
-- MySQL Syntax
-- Run this in MySQL Workbench or CMD before starting app
-- ============================================================

-- Create database
CREATE DATABASE IF NOT EXISTS rapidaid_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE rapidaid_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(150) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Emergency contacts table
CREATE TABLE IF NOT EXISTS contacts (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT          NOT NULL,
    name       VARCHAR(100) NOT NULL,
    relation   VARCHAR(50)  NOT NULL DEFAULT 'Contact',
    phone      VARCHAR(20)  NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- First aid history table
CREATE TABLE IF NOT EXISTS history (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT          NOT NULL,
    emergency_type VARCHAR(100) NOT NULL,
    action         TEXT,
    language       VARCHAR(10)  DEFAULT 'en',
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
