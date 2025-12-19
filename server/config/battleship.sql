-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 12, 2025 at 07:27 AM
-- Server version: 8.0.34
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `battleship`
--

-- --------------------------------------------------------

--
-- Table structure for table `game_history`
--

CREATE TABLE `game_history` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `opponent_id` int NOT NULL,
  `result` enum('win','lose') NOT NULL,
  `ships_sunk` int DEFAULT '0',
  `hits` int DEFAULT '0',
  `misses` int DEFAULT '0',
  `accuracy` decimal(5,2) DEFAULT '0.00',
  `max_streak` int DEFAULT '0',
  `played_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `game_history`
--

INSERT INTO `game_history` (`id`, `user_id`, `opponent_id`, `result`, `ships_sunk`, `hits`, `misses`, `accuracy`, `max_streak`, `played_at`) VALUES
(88, 1, 2, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 02:50:15'),
(89, 2, 1, 'win', 0, 0, 2, 0.00, 0, '2025-12-10 02:50:15'),
(90, 1, 2, 'win', 0, 0, 0, 0.00, 0, '2025-12-10 03:02:16'),
(91, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 03:02:16'),
(92, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 03:04:26'),
(93, 1, 2, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 03:04:28'),
(94, 1, 2, 'lose', 0, 0, 7, 0.00, 0, '2025-12-10 03:08:53'),
(95, 2, 1, 'lose', 0, 1, 7, 12.50, 1, '2025-12-10 03:08:55'),
(96, 1, 2, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 03:11:09'),
(97, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 03:11:12'),
(98, 1, 2, 'lose', 1, 0, 0, 0.00, 0, '2025-12-10 03:15:09'),
(99, 2, 1, 'win', 0, 3, 2, 60.00, 3, '2025-12-10 03:15:09'),
(100, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 03:20:03'),
(101, 1, 2, 'win', 0, 0, 1, 0.00, 0, '2025-12-10 03:20:16'),
(102, 1, 2, 'lose', 0, 3, 0, 100.00, 3, '2025-12-10 03:21:02'),
(103, 2, 1, 'win', 1, 0, 1, 0.00, 0, '2025-12-10 03:21:05'),
(104, 1, 2, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 03:24:57'),
(105, 2, 1, 'win', 0, 0, 0, 0.00, 0, '2025-12-10 03:25:11'),
(106, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 03:29:34'),
(107, 1, 2, 'win', 0, 0, 0, 0.00, 0, '2025-12-10 03:29:44'),
(108, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 03:33:51'),
(109, 1, 2, 'win', 0, 0, 0, 0.00, 0, '2025-12-10 03:34:00'),
(110, 1, 2, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 03:40:58'),
(111, 2, 1, 'win', 0, 0, 0, 0.00, 0, '2025-12-10 03:41:09'),
(112, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 03:44:46'),
(113, 1, 2, 'win', 0, 0, 0, 0.00, 0, '2025-12-10 03:44:55'),
(114, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 03:48:35'),
(115, 1, 2, 'win', 0, 0, 0, 0.00, 0, '2025-12-10 03:48:42'),
(116, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 03:53:50'),
(117, 1, 2, 'win', 0, 0, 0, 0.00, 0, '2025-12-10 03:53:52'),
(118, 1, 2, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 03:54:23'),
(119, 2, 1, 'win', 0, 0, 0, 0.00, 0, '2025-12-10 03:54:35'),
(120, 1, 2, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 03:54:53'),
(121, 2, 1, 'win', 0, 0, 0, 0.00, 0, '2025-12-10 03:55:00'),
(122, 1, 2, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 03:57:50'),
(123, 2, 1, 'win', 0, 0, 0, 0.00, 0, '2025-12-10 03:58:02'),
(124, 1, 2, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 04:02:44'),
(125, 2, 1, 'win', 0, 0, 0, 0.00, 0, '2025-12-10 04:02:49'),
(126, 1, 2, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 04:07:59'),
(127, 2, 1, 'win', 0, 0, 0, 0.00, 0, '2025-12-10 04:08:03'),
(128, 1, 2, 'lose', 1, 9, 0, 100.00, 9, '2025-12-10 04:10:35'),
(129, 2, 1, 'win', 2, 5, 1, 83.33, 5, '2025-12-10 04:10:38'),
(130, 2, 1, 'lose', 4, 0, 0, 0.00, 0, '2025-12-10 04:15:20'),
(131, 1, 2, 'win', 0, 17, 0, 100.00, 17, '2025-12-10 04:15:20'),
(132, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 04:15:37'),
(133, 1, 2, 'win', 0, 0, 0, 0.00, 0, '2025-12-10 04:15:42'),
(134, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 04:20:24'),
(135, 1, 2, 'win', 0, 0, 0, 0.00, 0, '2025-12-10 04:20:26'),
(136, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-10 04:20:44'),
(137, 1, 2, 'win', 0, 0, 0, 0.00, 0, '2025-12-10 04:20:46'),
(138, 1, 2, 'win', 0, 17, 0, 100.00, 17, '2025-12-11 12:46:11'),
(139, 2, 1, 'lose', 4, 0, 0, 0.00, 0, '2025-12-11 12:46:11'),
(140, 1, 2, 'win', 0, 17, 0, 100.00, 17, '2025-12-12 05:20:31'),
(141, 2, 1, 'lose', 4, 0, 0, 0.00, 0, '2025-12-12 05:20:31'),
(142, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-12 05:28:26'),
(143, 1, 2, 'win', 0, 0, 1, 0.00, 0, '2025-12-12 05:28:33'),
(144, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-12 05:29:06'),
(145, 1, 2, 'win', 0, 0, 0, 0.00, 0, '2025-12-12 05:29:09'),
(146, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-12 05:32:16'),
(147, 1, 2, 'win', 0, 0, 0, 0.00, 0, '2025-12-12 05:32:20'),
(148, 1, 2, 'lose', 0, 1, 1, 50.00, 1, '2025-12-12 05:41:19'),
(149, 2, 1, 'win', 0, 0, 0, 0.00, 0, '2025-12-12 05:41:23'),
(150, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-12 05:46:30'),
(151, 1, 2, 'win', 0, 0, 0, 0.00, 0, '2025-12-12 05:46:35'),
(152, 1, 2, 'lose', 0, 0, 0, 0.00, 0, '2025-12-12 05:57:17'),
(153, 2, 1, 'win', 0, 0, 0, 0.00, 0, '2025-12-12 05:57:22'),
(154, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-12 06:00:01'),
(155, 1, 2, 'win', 0, 0, 0, 0.00, 0, '2025-12-12 06:00:04'),
(156, 1, 2, 'lose', 0, 0, 0, 0.00, 0, '2025-12-12 06:05:29'),
(157, 1, 2, 'lose', 0, 0, 0, 0.00, 0, '2025-12-12 06:07:19'),
(158, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-12 06:07:22'),
(159, 1, 2, 'lose', 0, 0, 0, 0.00, 0, '2025-12-12 06:10:28'),
(160, 2, 1, 'win', 0, 0, 0, 0.00, 0, '2025-12-12 06:10:32'),
(161, 2, 1, 'lose', 0, 0, 0, 0.00, 0, '2025-12-12 06:13:29'),
(162, 1, 2, 'win', 0, 0, 0, 0.00, 0, '2025-12-12 06:13:36'),
(163, 1, 2, 'lose', 0, 0, 0, 0.00, 0, '2025-12-12 06:22:30'),
(164, 2, 1, 'win', 0, 0, 0, 0.00, 0, '2025-12-12 06:22:35'),
(165, 1, 2, 'lose', 0, 2, 0, 100.00, 2, '2025-12-12 06:27:02'),
(166, 2, 1, 'win', 1, 0, 0, 0.00, 0, '2025-12-12 06:27:04');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `is_online` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `is_online`, `created_at`) VALUES
(1, 'player1', '123', 0, '2025-11-30 07:16:20'),
(2, 'player2', '123', 0, '2025-11-30 07:16:20'),
(3, 'admin', 'admin123', 0, '2025-11-30 07:16:20'),
(4, 'player3', 'phuoc@2209', 1, '2025-12-09 12:35:20'),
(5, 'player4', 'phuoc@2209', 0, '2025-12-09 12:41:34');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `game_history`
--
ALTER TABLE `game_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_user_id` (`user_id`),
  ADD KEY `idx_opponent_id` (`opponent_id`),
  ADD KEY `idx_result` (`result`),
  ADD KEY `idx_played_at` (`played_at`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD KEY `idx_username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `game_history`
--
ALTER TABLE `game_history`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=167;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `game_history`
--
ALTER TABLE `game_history`
  ADD CONSTRAINT `game_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `game_history_ibfk_2` FOREIGN KEY (`opponent_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
