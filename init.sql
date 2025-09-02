-- Multi-Agent Marketing System Database Initialization
-- This script creates the necessary database structure

-- Create database if it doesn't exist (for MySQL)
-- CREATE DATABASE IF NOT EXISTS marketing_system;
-- USE marketing_system;

-- Create extensions (for PostgreSQL only)
-- Uncomment the line below if using PostgreSQL
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance
-- These will be created automatically by SQLAlchemy, but we can add custom ones here

-- Example: Create a custom index for user activities
-- CREATE INDEX IF NOT EXISTS idx_user_activities_user_id_created_at 
-- ON user_activities(user_id, created_at DESC);

-- Example: Create a custom index for user sessions
-- CREATE INDEX IF NOT EXISTS idx_user_sessions_token_active 
-- ON user_sessions(session_token) WHERE is_active = true;

-- Add any custom database setup here
-- The main tables will be created by SQLAlchemy when the application starts
