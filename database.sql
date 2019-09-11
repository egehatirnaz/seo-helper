-- phpMyAdmin SQL Dump
-- version 4.9.0.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:8889
-- Generation Time: Sep 11, 2019 at 10:25 AM
-- Server version: 5.7.26
-- PHP Version: 7.3.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `seo-helper`
--

-- --------------------------------------------------------

--
-- Table structure for table `analysed_url`
--

CREATE TABLE `analysed_url` (
  `id` int(10) NOT NULL,
  `url` text NOT NULL,
  `subdomain` varchar(255) NOT NULL,
  `domain` varchar(255) NOT NULL,
  `time_accessed` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `analysed_url_href_404`
--

CREATE TABLE `analysed_url_href_404` (
  `id` int(10) NOT NULL,
  `url_id` int(11) NOT NULL,
  `href` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `analysed_url_meta`
--

CREATE TABLE `analysed_url_meta` (
  `id` int(10) NOT NULL,
  `url_id` int(10) NOT NULL,
  `tag` varchar(255) NOT NULL,
  `attribute` text,
  `value` text,
  `content` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `analysis_errors`
--

CREATE TABLE `analysis_errors` (
  `id` int(11) NOT NULL,
  `url_id` int(11) NOT NULL,
  `error_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `analysis_user`
--

CREATE TABLE `analysis_user` (
  `id` int(11) NOT NULL,
  `url_id` int(10) NOT NULL,
  `user_id` int(10) NOT NULL,
  `time` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `api_key`
--

CREATE TABLE `api_key` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `api_key` varchar(64) NOT NULL,
  `timestamp` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `seo_errors`
--

CREATE TABLE `seo_errors` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `tag` varchar(255) NOT NULL,
  `attribute` text,
  `value` text,
  `content` text,
  `description` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `name_surname` varchar(255) NOT NULL,
  `password` varchar(60) NOT NULL,
  `email` varchar(255) NOT NULL,
  `created_at` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `user_access_control`
--

CREATE TABLE `user_access_control` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `is_admin` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `analysed_url`
--
ALTER TABLE `analysed_url`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `analysed_url_href_404`
--
ALTER TABLE `analysed_url_href_404`
  ADD PRIMARY KEY (`id`),
  ADD KEY `analysed_url_href_404fk0` (`url_id`);

--
-- Indexes for table `analysed_url_meta`
--
ALTER TABLE `analysed_url_meta`
  ADD PRIMARY KEY (`id`) USING BTREE,
  ADD KEY `analysed_url_meta_fk0` (`url_id`) USING BTREE;

--
-- Indexes for table `analysis_errors`
--
ALTER TABLE `analysis_errors`
  ADD PRIMARY KEY (`id`),
  ADD KEY `analysis_errors_fk0` (`url_id`),
  ADD KEY `analysis_errors_fk1` (`error_id`);

--
-- Indexes for table `analysis_user`
--
ALTER TABLE `analysis_user`
  ADD PRIMARY KEY (`id`),
  ADD KEY `analysis_user_fk1` (`user_id`),
  ADD KEY `analysis_user_fk0` (`url_id`) USING BTREE;

--
-- Indexes for table `api_key`
--
ALTER TABLE `api_key`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `api_key` (`api_key`),
  ADD KEY `api_key_fk0` (`user_id`);

--
-- Indexes for table `seo_errors`
--
ALTER TABLE `seo_errors`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `user_access_control`
--
ALTER TABLE `user_access_control`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_access_control_fk0` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `analysed_url`
--
ALTER TABLE `analysed_url`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `analysed_url_href_404`
--
ALTER TABLE `analysed_url_href_404`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `analysed_url_meta`
--
ALTER TABLE `analysed_url_meta`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `analysis_errors`
--
ALTER TABLE `analysis_errors`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `analysis_user`
--
ALTER TABLE `analysis_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `api_key`
--
ALTER TABLE `api_key`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `seo_errors`
--
ALTER TABLE `seo_errors`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user_access_control`
--
ALTER TABLE `user_access_control`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `analysed_url_href_404`
--
ALTER TABLE `analysed_url_href_404`
  ADD CONSTRAINT `analysed_url_href_404fk0` FOREIGN KEY (`url_id`) REFERENCES `analysed_url` (`id`);

--
-- Constraints for table `analysed_url_meta`
--
ALTER TABLE `analysed_url_meta`
  ADD CONSTRAINT `analysed_url_meta_fk0` FOREIGN KEY (`url_id`) REFERENCES `analysed_url` (`id`);

--
-- Constraints for table `analysis_errors`
--
ALTER TABLE `analysis_errors`
  ADD CONSTRAINT `analysis_errors_fk0` FOREIGN KEY (`url_id`) REFERENCES `analysed_url` (`id`),
  ADD CONSTRAINT `analysis_errors_fk1` FOREIGN KEY (`error_id`) REFERENCES `seo_errors` (`id`);

--
-- Constraints for table `analysis_user`
--
ALTER TABLE `analysis_user`
  ADD CONSTRAINT `analysis_user_fk0` FOREIGN KEY (`url_id`) REFERENCES `analysed_url` (`id`),
  ADD CONSTRAINT `analysis_user_fk1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

--
-- Constraints for table `api_key`
--
ALTER TABLE `api_key`
  ADD CONSTRAINT `api_key_fk0` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

--
-- Constraints for table `user_access_control`
--
ALTER TABLE `user_access_control`
  ADD CONSTRAINT `user_access_control_fk0` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
