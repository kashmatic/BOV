--#########################################################
--## Copyright 2008 The Trustees of Indiana University
--##
--## Licensed under the Apache License, Version 2.0 (the "License");
--## you may not use this file except in compliance with the License.
--## You may obtain a copy of the License at
--##
--##      http://www.apache.org/licenses/LICENSE-2.0
--##
--## Unless required by applicable law or agreed to in writing, software
--## distributed under the License is distributed on an "AS IS" BASIS,
--## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
--## See the License for the specific language governing permissions and
--## limitations under the License.
--#########################################################

-- MySQL dump 10.10
--
-- Host: localhost    Database: microbial
-- ------------------------------------------------------
-- Server version	5.0.22-Debian_0nexenta6.07-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `BOV_hit`
--

DROP TABLE IF EXISTS `BOV_hit`;
CREATE TABLE `BOV_hit` (
  `id` int(11) NOT NULL auto_increment,
  `result_id` int(11) NOT NULL,
  `hit_name` varchar(200) NOT NULL,
  `query_length` int(11) NOT NULL,
  `hit_length` int(11) NOT NULL,
  `score` int(11) default NULL,
  `evalue` varchar(11) default NULL,
  PRIMARY KEY  (`id`),
  KEY `result_id` (`result_id`),
  CONSTRAINT `BOV_hit_ibfk_1` FOREIGN KEY (`result_id`) REFERENCES `BOV_result` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `BOV_hsp`
--

DROP TABLE IF EXISTS `BOV_hsp`;
CREATE TABLE `BOV_hsp` (
  `id` int(11) NOT NULL auto_increment,
  `hit_id` int(11) NOT NULL,
  `rank` int(11) NOT NULL,
  `object` text NOT NULL,
  `query_start` int(11) default NULL,
  `query_end` int(11) default NULL,
  `hit_start` int(11) default NULL,
  `hit_end` int(11) default NULL,
  PRIMARY KEY  (`id`),
  KEY `hit_id` (`hit_id`),
  CONSTRAINT `BOV_hsp_ibfk_1` FOREIGN KEY (`hit_id`) REFERENCES `BOV_hit` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `BOV_project`
--

DROP TABLE IF EXISTS `BOV_project`;
CREATE TABLE `BOV_project` (
  `id` int(11) NOT NULL auto_increment,
  `hash` char(32) NOT NULL,
  `file_size` int(11) NOT NULL,
  `created_on` timestamp NOT NULL default CURRENT_TIMESTAMP,
  `email` text NOT NULL,
`file_name` varchar(30) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `BOV_result`
--

DROP TABLE IF EXISTS `BOV_result`;
CREATE TABLE `BOV_result` (
  `id` int(11) NOT NULL auto_increment,
  `project_id` int(11) NOT NULL,
  `query_name` varchar(200) NOT NULL,
  `query_description` text NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `BOV_result_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `BOV_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

