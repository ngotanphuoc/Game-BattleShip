-- Migration: Add statistics columns to users table
-- Run this SQL in your MySQL database

USE battleship;

-- Add statistics columns to users table
ALTER TABLE `users` 
ADD COLUMN `wins` INT DEFAULT 0 AFTER `password`,
ADD COLUMN `losses` INT DEFAULT 0 AFTER `wins`,
ADD COLUMN `draws` INT DEFAULT 0 AFTER `losses`,
ADD COLUMN `total_games` INT DEFAULT 0 AFTER `draws`;

-- Update existing users to calculate their stats from game_history
UPDATE users u
SET 
    wins = (
        SELECT COUNT(*) 
        FROM game_history 
        WHERE user_id = u.id AND result = 'win'
    ),
    losses = (
        SELECT COUNT(*) 
        FROM game_history 
        WHERE user_id = u.id AND result = 'lose'
    ),
    total_games = (
        SELECT COUNT(*) 
        FROM game_history 
        WHERE user_id = u.id
    );

-- Verify the changes
SELECT id, username, wins, losses, draws, total_games 
FROM users;
