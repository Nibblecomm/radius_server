CREATE DATABASE  IF NOT EXISTS `spotipo` /*!40100 DEFAULT CHARACTER SET utf8 */;
USE `spotipo`;
-- MySQL dump 10.13  Distrib 5.7.17, for macos10.12 (x86_64)
--
-- Host: localhost    Database: spotipo_py3
-- ------------------------------------------------------
-- Server version	5.6.47

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
-- Table structure for table `radiusnas`
--

DROP TABLE IF EXISTS `radiusnas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `radiusnas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `account_id` int(11) DEFAULT NULL,
  `siteid` int(11) DEFAULT NULL,
  `secret` varchar(50) DEFAULT NULL,
  `extip` varchar(50) DEFAULT NULL,
  `identity` varchar(50) DEFAULT NULL,
  `vendor_id` int(11) DEFAULT NULL,
  `demo` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_radiusnas_identity` (`identity`),
  KEY `account_id` (`account_id`),
  KEY `siteid` (`siteid`),
  KEY `ix_radiusnas_extip` (`extip`),
  KEY `ix_radiusnas_secret` (`secret`),
  CONSTRAINT `radiusnas_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `account` (`id`),
  CONSTRAINT `radiusnas_ibfk_2` FOREIGN KEY (`siteid`) REFERENCES `wifisite` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `radiusnas`
--

LOCK TABLES `radiusnas` WRITE;
/*!40000 ALTER TABLE `radiusnas` DISABLE KEYS */;
INSERT INTO `radiusnas` VALUES (1,1,1,'br2xn9kex1o79dk70aw1pa1hxwargn','1.1.1.1','247e7d8mh5z44adqf38m_deadbeefcafe',14988,0),(2,1,1,'56rmkuri92d8a0wvi9divyxvn1nku3',NULL,'cnrpbyro9058cwy1k1ybbeugco5glp',NULL,1);
/*!40000 ALTER TABLE `radiusnas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `radiussessions`
--

DROP TABLE IF EXISTS `radiussessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `radiussessions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nas_id` int(11) DEFAULT NULL,
  `radiususer_id` int(11) DEFAULT NULL,
  `assoc_time` datetime DEFAULT NULL,
  `disassoc_time` datetime DEFAULT NULL,
  `lastseen_time` datetime DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `data_used` varchar(20) DEFAULT NULL,
  `mac` varchar(30) DEFAULT NULL,
  `accnt_sessionid` varchar(100) DEFAULT NULL,
  `framed_ip_address` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `nas_id` (`nas_id`),
  KEY `radiususer_id` (`radiususer_id`),
  KEY `ix_radiussessions_accnt_sessionid` (`accnt_sessionid`),
  KEY `ix_radiussessions_assoc_time` (`assoc_time`),
  KEY `ix_radiussessions_disassoc_time` (`disassoc_time`),
  KEY `ix_radiussessions_framed_ip_address` (`framed_ip_address`),
  KEY `ix_radiussessions_lastseen_time` (`lastseen_time`),
  KEY `ix_radiussessions_mac` (`mac`),
  CONSTRAINT `radiussessions_ibfk_1` FOREIGN KEY (`nas_id`) REFERENCES `radiusnas` (`id`),
  CONSTRAINT `radiussessions_ibfk_2` FOREIGN KEY (`radiususer_id`) REFERENCES `radiususer` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `radiussessions`
--

LOCK TABLES `radiussessions` WRITE;
/*!40000 ALTER TABLE `radiussessions` DISABLE KEYS */;
/*!40000 ALTER TABLE `radiussessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `radiususer`
--

DROP TABLE IF EXISTS `radiususer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `radiususer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `account_id` int(11) DEFAULT NULL,
  `nas_id` int(11) DEFAULT NULL,
  `guestsessionid` int(11) DEFAULT NULL,
  `radiususer` varchar(50) DEFAULT NULL,
  `radiuspass` varchar(50) DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `data_limit` bigint(20) DEFAULT NULL,
  `speed_ul` int(11) DEFAULT NULL,
  `speed_dl` int(11) DEFAULT NULL,
  `active` int(11) DEFAULT NULL,
  `mac` varchar(30) DEFAULT NULL,
  `starttime` datetime DEFAULT NULL,
  `stoptime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_radiususer_radiususer` (`radiususer`),
  KEY `account_id` (`account_id`),
  KEY `guestsessionid` (`guestsessionid`),
  KEY `nas_id` (`nas_id`),
  KEY `ix_radiususer_mac` (`mac`),
  KEY `ix_radiususer_radiuspass` (`radiuspass`),
  KEY `ix_radiususer_starttime` (`starttime`),
  KEY `ix_radiususer_stoptime` (`stoptime`),
  CONSTRAINT `radiususer_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `account` (`id`),
  CONSTRAINT `radiususer_ibfk_2` FOREIGN KEY (`guestsessionid`) REFERENCES `guestsession` (`id`),
  CONSTRAINT `radiususer_ibfk_3` FOREIGN KEY (`nas_id`) REFERENCES `radiusnas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `radiususer`
--

LOCK TABLES `radiususer` WRITE;
/*!40000 ALTER TABLE `radiususer` DISABLE KEYS */;
INSERT INTO `radiususer` VALUES (1,NULL,2,1,'43SKVT0RUMYBNXMRH8IGCSI4X8FN1I75PBC89Y9X','VUF696D4TG6VD26L67NCZEM20KK3WGF1TV4P617Q',0,10000,0,0,1,'f2:ff:11:22:33:44','2020-08-17 20:49:52','2021-08-17 21:49:52'),(2,NULL,2,1,'JL1TWJT9833JOKMP5ZNJZNJ5DC6F2SFOXKRT5S29','IRWDBZD1QSTB98PHSHHIDUQ17LLA05XGH2WJEVSB',0,10000,0,0,1,'f2:ff:11:22:33:44','2020-08-17 20:50:42','2021-08-17 21:49:42'),(3,NULL,2,1,'VZJ9VTB662KI7F1ZHFF8YBW8PNV1ECEQD3FZAMSY','GHRZ88B1QMWPV6GKI91DHZFTZBKC0NDZBMVKJ36R',0,10000,0,0,1,'f2:ff:11:22:33:44','2020-08-17 20:52:07','2021-08-17 21:49:07');
/*!40000 ALTER TABLE `radiususer` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-08-18 22:25:36
