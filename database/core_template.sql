-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: crm
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `addresses`
--

DROP TABLE IF EXISTS `addresses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `addresses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `company_id` int DEFAULT NULL,
  `country_id` int DEFAULT NULL,
  `state_id` int DEFAULT NULL,
  `city_id` int DEFAULT NULL,
  `address_line1` text,
  `address_line2` text,
  `postal_code` varchar(10) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `company_id` (`company_id`),
  KEY `country_id` (`country_id`),
  KEY `state_id` (`state_id`),
  KEY `city_id` (`city_id`),
  CONSTRAINT `direcciones_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `direcciones_ibfk_2` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`),
  CONSTRAINT `direcciones_ibfk_3` FOREIGN KEY (`country_id`) REFERENCES `countries` (`id`),
  CONSTRAINT `direcciones_ibfk_4` FOREIGN KEY (`state_id`) REFERENCES `states` (`id`),
  CONSTRAINT `direcciones_ibfk_5` FOREIGN KEY (`city_id`) REFERENCES `cities` (`id`),
  CONSTRAINT `chk_dir_exclusiva` CHECK (((`user_id` is null) <> (`company_id` is null))),
  CONSTRAINT `chk_direccion_exclusiva` CHECK ((((`user_id` is not null) and (`company_id` is null)) or ((`user_id` is null) and (`company_id` is not null))))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cities`
--

DROP TABLE IF EXISTS `cities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cities` (
  `id` int NOT NULL AUTO_INCREMENT,
  `city_name` varchar(255) DEFAULT NULL,
  `state_id` int DEFAULT NULL,
  `area_km2` int unsigned DEFAULT NULL,
  `population` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `state_id` (`state_id`),
  CONSTRAINT `municipios_ibfk_1` FOREIGN KEY (`state_id`) REFERENCES `states` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cities`
--

LOCK TABLES `cities` WRITE;
/*!40000 ALTER TABLE `cities` DISABLE KEYS */;
INSERT INTO `cities` VALUES (1,'Bogotá',1,1578,8034649),(2,'Leticia',2,3695,32450),(3,'El Encanto',2,10724,4376),(4,'La Chorrera',2,12727,2027),(5,'La Pedrera',2,NULL,1187),(6,'La Victoria',2,NULL,880),(7,'Mirití-Paraná',2,1443,13),(8,'Puerto Alegría',2,1443,1277),(9,'Puerto Arica',2,NULL,1343),(10,'Puerto Nariño',2,1876,9744),(11,'Puerto Santander',2,NULL,565),(12,'Tarapacá',2,1443,4195),(13,'Medellín',3,381,2529403),(14,'Abejorral',3,502,17599),(15,'Abriaquí',3,290,4200),(16,'Alejandría',3,149,NULL),(17,'Amagá',3,84,29555),(18,'Amalfi',3,1210,22088),(19,'Andes',3,40342,43269),(20,'Angelópolis',3,86,8946),(21,'Angostura',3,387,10500),(22,'Anorí',3,1430,16447),(23,'Santa Fe de Antioquia',3,493,23216),(24,'Anzá',3,256,NULL),(25,'Apartadó',3,607,127744),(26,'Arboletes',3,718,45710),(27,'Argelia',3,254,8911),(28,'Armenia',3,29743,2780469),(29,'Barbosa',3,206,54347),(30,'Bello',3,142,561955),(31,'Belmira',3,296,NULL),(32,'Betania',3,168,9286),(33,'Betulia',3,252,17317),(34,'Ciudad Bolívar',3,282,23361),(35,'Briceño',3,64,2584),(36,'Buriticá',3,364,NULL),(37,'Cáceres',3,1996,37806),(38,'Caicedo',3,221,7608),(39,'Caldas',3,133,82234),(40,'Campamento',3,200,NULL),(41,'Cañasgordas',3,391,13595),(42,'Caracolí',3,260,NULL),(43,'Caramanta',3,86,7771),(44,'Carepa',3,380,47932),(45,'Carolina del Príncipe',3,166,NULL),(46,'Caucasia',3,1411,90213),(47,'Chigorodó',3,608,86239),(48,'Cisneros',3,46,11555),(49,'Cocorná',3,210,14743),(50,'Concepción',3,167,3463),(51,'Concordia',3,231,16095),(52,'Copacabana',3,70,77884),(53,'Dabeiba',3,1883,22717),(54,'Donmatías',3,181,14208),(55,'Ebéjico',3,235,12158),(56,'El Bagre',3,1563,53846),(57,'El Carmen de Viboral',3,448,59416),(58,'El Peñol',3,125,16223),(59,'El Retiro',3,273,20700),(60,'El Santuario',3,75,35422),(61,'Entrerríos',3,219,8820),(62,'Envigado',3,79,228848),(63,'Fredonia',3,247,18790),(64,'Frontino',3,1263,20156),(65,'Giraldo',3,239,4029),(66,'Gómez Plata',3,360,8235),(67,'Granada',3,183,9204),(68,'Guadalupe',3,87,6286),(69,'Guarne',3,151,52129),(70,'Guatapé',3,69,9121),(71,'Heliconia',3,117,6138),(72,'Hispania',3,58,NULL),(73,'Itagüí',3,21,276744),(74,'Ituango',3,2347,23784),(75,'Jardín',3,224,13748),(76,'Jericó',3,193,12103),(77,'La Ceja',3,131,64889),(78,'La Estrella',3,35,71545),(79,'La Pintada',3,55,NULL),(80,'La Unión',3,198,19119),(81,'Liborina',3,217,7928),(82,'Maceo',3,431,NULL),(83,'Marinilla',3,115,64645),(84,'Montebello',3,83,NULL),(85,'Murindó',3,1349,NULL),(86,'Mutatá',3,1106,12607),(87,'Nariño',3,33268,1630592),(88,'Nechí',3,914,24066),(89,'Necoclí',3,1361,70824),(90,'Olaya Herrera',3,NULL,33132),(91,'Peque',3,392,7155),(92,'Pueblorrico',3,86,8664),(93,'Puerto Berrío',3,1184,39314),(94,'Puerto Claver',3,NULL,NULL),(95,'Puerto Nare',3,660,12161),(96,'Puerto Triunfo',3,361,17231),(97,'Remedios',3,1985,29199),(98,'Rionegro',3,196,135465),(99,'Sabanalarga',3,265,NULL),(100,'Sabaneta',3,15,82375),(101,'Salgar',3,418,17804),(102,'San Andrés de Cuerquia',3,177,NULL),(103,'San Carlos',3,702,14480),(104,'San Francisco',3,601,808988),(105,'San Jerónimo',3,155,13158),(106,'San José de la Montaña',3,127,NULL),(107,'San Juan de Urabá',3,239,19992),(108,'San Luis Obispo',3,34,47063),(109,'San Pedro de los Milagros',3,229,17119),(110,'San Pedro de Urabá',3,476,30527),(111,'San Rafael',3,362,12578),(112,'San Roque',3,441,16789),(113,'San Vicente Ferrer',3,243,18051),(114,'Santa Bárbara',3,109,88665),(115,'Santa Rosa de Osos',3,812,37864),(116,'Santo Domingo',3,NULL,NULL),(117,'Segovia',3,1231,41000),(118,'Sonsón',3,1323,33598),(119,'Sopetrán',3,223,13748),(120,'Támesis',3,264,15218),(121,'Tarazá',3,1569,48926),(122,'Tarso',3,119,7542),(123,'Titiribí',3,142,14092),(124,'Toledo',3,139,6144),(125,'Turbo',3,3055,181000),(126,'Uramita',3,236,8253),(127,'Urrao',3,2556,44648),(128,'Valdivia',3,545,11511),(129,'Valparaíso',3,48,296655),(130,'Vegachí',3,512,9448),(131,'Venecia',3,141,10280),(132,'Vigía del Fuerte',3,1780,5624),(133,'Yalí',3,477,NULL),(134,'Yarumal',3,724,41542),(135,'Yolombó',3,941,23958),(136,'Yondó',3,1881,17597),(137,'Zaragoza',3,1064,29614),(138,'Arauca',4,23818,262174),(139,'Arauquita',4,3060,56209),(140,'Cravo Norte',4,5221,3331),(141,'Fortul',4,1125,17492),(142,'Puerto Rondón',4,2313,3844),(143,'Saravena',4,907,47203),(144,'Tame',4,1064,43932),(145,'Barranquilla',5,154,1327209),(146,'Baranoa',5,127,68383),(147,'Campo de la Cruz',5,105,22810),(148,'Candelaria',5,143,15631),(149,'Galapa',5,98,60708),(150,'Juan de Acosta',5,176,18828),(151,'Luruaco',5,246,27647),(152,'Malambo',5,108,99058),(153,'Manatí',5,206,13456),(154,'Palmar de Varela',5,94,28932),(155,'Piojó',5,258,11635),(156,'Polonuevo',5,73,19454),(157,'Ponedera',5,204,18430),(158,'Puerto Colombia',5,73,26932),(159,'Repelón',5,363,22196),(160,'Sabanagrande',5,43,24880),(161,'Sabanalarga',5,399,84410),(162,'Santa Lucía',5,50,12650),(163,'Santo Tomás',5,67,32000),(164,'Soledad',5,67,676014),(165,'Suan',5,42,9344),(166,'Tubará',5,176,12718),(167,'Usiacurí',5,103,9543),(168,'Cartagena de Indias',6,572,1036412),(169,'Achí',6,1471,23051),(170,'Altos del Rosario',6,249,13669),(171,'Arjona',6,566,69503),(172,'Arenal',6,534,18876),(173,'Arroyohondo',6,162,9907),(174,'Barranco de Loba',6,416,14435),(175,'Calamar',6,NULL,22202),(176,'Cantagallo',6,669,6874),(177,'El Carmen de Bolívar',6,945,66001),(178,'Cicuco',6,132,13120),(179,'Clemencia',6,235,13821),(180,'Córdoba',6,573,15012),(181,'El Guamo',6,NULL,NULL),(182,'El Peñón',6,NULL,7234),(183,'Hatillo de Loba',6,196,11770),(184,'Magangué',6,1568,123906),(185,'Mahates',6,NULL,26075),(186,'Margarita',6,295,9876),(187,'María La Baja',6,547,48079),(188,'Santa Cruz de Mompox',6,645,44124),(189,'Montecristo',6,2089,21229),(190,'Morales',6,1765,21182),(191,'Norosí',6,407,9850),(192,'Pinillos',6,NULL,23349),(193,'Regidor',6,396,10489),(194,'Río Viejo',6,NULL,8125),(195,'San Cristóbal',6,NULL,8054),(196,'San Estanislao',6,208,16518),(197,'San Fernando',6,288,9776),(198,'San Jacinto del Cauca',6,549,13426),(199,'San Jacinto del Cauca',6,549,13426),(200,'San Juan Nepomuceno',6,637,34110),(201,'San Martín de Loba',6,742,14504),(202,'San Pablo',6,1977,37160),(203,'Santa Catalina',6,223,14039),(204,'Santa Rosa del Sur',6,2360,18),(205,'Santa Rosa del Sur',6,2360,18),(206,'Simití',6,1345,20271),(207,'Soplaviento',6,131,NULL),(208,'Talaigua Nuevo',6,261,12845),(209,'Tiquisio',6,758,17939),(210,'Turbaco',6,185,105166),(211,'Turbaná',6,148,72168),(212,'Villanueva',6,135,21135),(213,'Zambrano',6,287,11367),(214,'Tunja',7,118,172548),(215,'Almeida',7,NULL,2171),(216,'Aquitania',7,943,15241),(217,'Arcabuco',7,155,5240),(218,'Belén',7,283,8070),(219,'Berbeo',7,NULL,NULL),(220,'Betéitiva',7,123,2069),(221,'Boavita',7,159,7079),(222,'Boyacá',7,23189,1217376),(223,'Briceño',7,64,2584),(224,'Buenavista',7,125,4732),(225,'Busbanzá',7,NULL,NULL),(226,'Caldas',7,84,3638),(227,'Campohermoso',7,NULL,3767),(228,'Cerinza',7,62,NULL),(229,'Chinavita',7,148,3528),(230,'Chiquinquirá',7,133,56054),(231,'Chiscas',7,659,4291),(232,'Chita',7,748,9542),(233,'Chitaraque',7,158,5687),(234,'Chivatá',7,56,6199),(235,'Chivor',7,108,1795),(236,'Ciénega',7,73,4754),(237,'Cómbita',7,149,14632),(238,'Coper',7,NULL,4047),(239,'Corrales',7,NULL,NULL),(240,'Covarachía',7,103,NULL),(241,'Cubará',7,1650,6725),(242,'Cucaita',7,44,4687),(243,'Cuítiva',7,43,1906),(244,'Duitama',7,267,131591),(245,'El Cocuy',7,253,5241),(246,'El Espino',7,70,4195),(247,'Firavitoba',7,110,NULL),(248,'Floresta',7,85,4523),(249,'Gachantivá',7,66,2654),(250,'Gámeza',7,88,4856),(251,'Garagoa',7,192,16944),(252,'Guacamayas',7,60,2132),(253,'Guateque',7,36,9603),(254,'Guayatá',7,112,5126),(255,'Güicán',7,934,6909),(256,'Iza',7,34,2349),(257,'Jenesano',7,59,7640),(258,'Jericó',7,NULL,NULL),(259,'La Capilla',7,57,2550),(260,'La Uvita',7,NULL,2523),(261,'La Victoria',7,110,1674),(262,'Labranzagrande',7,625,5099),(263,'Macanal',7,200,4821),(264,'Maní',7,3784,13291),(265,'Maripí',7,NULL,7480),(266,'Miraflores',7,NULL,8274),(267,'Mongua',7,366,4717),(268,'Monguí',7,NULL,NULL),(269,'Moniquirá',7,220,20848),(270,'Motavita',7,62,8067),(271,'Muzo',7,147,9040),(272,'Nobsa',7,55,16271),(273,'Nuevo Colón',7,0,6559),(274,'Oicatá',7,59,2834),(275,'Otanche',7,NULL,6997),(276,'Pachavita',7,68,2508),(277,'Páez',7,NULL,NULL),(278,'Paipa',7,306,31868),(279,'Pajarito',7,322,1719),(280,'Panqueba',7,42,1487),(281,'Pauna',7,NULL,6355),(282,'Paya',7,436,2550),(283,'Paz de Río',7,116,4680),(284,'Pesca',7,282,9322),(285,'Pisba',7,469,1344),(286,'Puerto Boyacá',7,1472,46736),(287,'Quípama',7,NULL,NULL),(288,'Ramiriquí',7,147,10015),(289,'Ráquira',7,233,13588),(290,'Recetor',7,179,NULL),(291,'Rondón',7,258,2934),(292,'Saboyá',7,247,12372),(293,'Sáchica',7,62,3791),(294,'Samacá',7,160,19907),(295,'San Eduardo',7,106,1862),(296,'San José de Pare',7,74,5221),(297,'San Luis de Gaceno',7,458,NULL),(298,'San Mateo',7,131,3682),(299,'San Miguel de Sema',7,90,4556),(300,'San Pablo de Borbur',7,194,5839),(301,'Santa María',7,532,NULL),(302,'Santa Rosa de Viterbo',7,NULL,11329),(303,'Santa Sofía',7,98,2704),(304,'Santana',7,67,7692),(305,'Sativanorte',7,184,2339),(306,'Sativasur',7,81,1110),(307,'Siachoque',7,125,8964),(308,'Soatá',7,136,7255),(309,'Socha',7,151,7140),(310,'Socotá',7,600,9812),(311,'Sogamoso',7,209,131105),(312,'Somondoco',7,59,3632),(313,'Sora',7,42,3025),(314,'Soracá',7,57,5353),(315,'Susacón',7,191,3095),(316,'Sutamarchán',7,102,5916),(317,'Sutatenza',7,41,4086),(318,'Tenza',7,51,4112),(319,'Tibaná',7,12176,9186),(320,'Tibasosa',7,94,14063),(321,'Tinjacá',7,79,3035),(322,'Tipacoque',7,72,3206),(323,'Toca',7,165,10157),(324,'Togüí',7,118,4966),(325,'Tópaga',7,37,3694),(326,'Tota',7,314,5386),(327,'Turmequé',7,106,NULL),(328,'Úmbita',7,148,10314),(329,'Ventaquemada',7,159,15442),(330,'Villa de Leyva',7,128,21953),(331,'Viracachá',7,68,3222),(332,'Zetaquira',7,262,4557),(333,'Manizales',8,572,434403),(334,'Aguadas',8,NULL,20712),(335,'Anserma',8,206,36149),(336,'Aranzazu',8,152,9854),(337,'Belalcázar',8,115,9690),(338,'Chinchiná',8,112,47929),(339,'Filadelfia',8,193,9630),(340,'La Dorada',8,574,71905),(341,'La Merced',8,NULL,NULL),(342,'La Victoria',8,110,1674),(343,'Manzanares',8,NULL,16532),(344,'Marmato',8,41,8485),(345,'Marquetalia',8,90,12146),(346,'Marulanda',8,NULL,NULL),(347,'Neira',8,NULL,20495),(348,'Norcasia',8,211,NULL),(349,'Pácora',8,234,13214),(350,'Palestina',8,118,13560),(351,'Pensilvania',8,530,26361),(352,'Riosucio',8,429,57220),(353,'Risaralda',8,172,NULL),(354,'Salamina',8,422,18704),(355,'Samaná',8,761,17466),(356,'San José',8,67,NULL),(357,'Supía',8,NULL,26571),(358,'Villamaría',8,480,64652),(359,'Viterbo',8,172,12432),(360,'Florencia',9,2292,191867),(361,'Albania',9,417,6429),(362,'Belén de los Andaquíes',9,NULL,NULL),(363,'Cartagena del Chairá',9,NULL,35993),(364,'Curillo',9,459,7518),(365,'El Doncello',9,NULL,17775),(366,'El Paujil',9,NULL,13014),(367,'La Montañita',9,NULL,15725),(368,'Milán',9,137,7507),(369,'Morelia',9,NULL,NULL),(370,'Puerto Rico',9,9104,3221789),(371,'San José del Fragua',9,1226,11364),(372,'San Vicente del Caguán',9,17875,50719),(373,'Solano',9,42178,10331),(374,'Solita',9,NULL,NULL),(375,'Valparaíso',9,48,296655),(376,'Yopal',10,2532,179355),(377,'Aguazul',10,NULL,44381),(378,'Monterrey',10,879,14828),(379,'Nunchía',10,NULL,NULL),(380,'Orocué',10,42,8102),(381,'Paz de Ariporo',10,NULL,34446),(382,'Pore',10,NULL,NULL),(383,'Recetor',10,179,NULL),(384,'Sabanalarga',10,408,NULL),(385,'Sácama',10,291,NULL),(386,'San Luis de Palenque',10,3057,NULL),(387,'Támara',10,1136,7044),(388,'Tauramena',10,2391,21709),(389,'Trinidad',10,2991,11734),(390,'Villanueva',10,135,21135),(391,'Popayán',11,825,31727),(392,'Almaguer',11,NULL,16523),(393,'Argelia',11,713,20136),(394,'Balboa',11,360,18910),(395,'Bolívar',11,746,44864),(396,'Buenos Aires',11,203,3120612),(397,'Cajibío',11,NULL,38932),(398,'Caldono',11,NULL,34348),(399,'Caloto',11,426,25416),(400,'Corinto',11,NULL,33846),(401,'El Tambo',11,NULL,48226),(402,'Florencia',11,56,NULL),(403,'Guachené',11,NULL,NULL),(404,'Guapi',11,NULL,24037),(405,'Inzá',11,9,26571),(406,'Jambaló',11,254,16353),(407,'La Sierra',11,217,9935),(408,'La Vega',11,NULL,47791),(409,'López de Micay',11,NULL,15154),(410,'Mercaderes',11,827,14824),(411,'Miranda',11,NULL,43333),(412,'Morales',11,NULL,29737),(413,'Padilla',11,100,9937),(414,'Páez',11,NULL,36977),(415,'Patía',11,NULL,37781),(416,'Piamonte',11,NULL,9259),(417,'Piendamó',11,197,44535),(418,'Puerto Tejada',11,NULL,46215),(419,'Puracé-Coconuco',11,783,14952),(420,'Rosas',11,130,9336),(421,'San Sebastián',11,61,186665),(422,'Santa Rosa',11,3198,5045),(423,'Santander de Quilichao',11,521,220000),(424,'Silvia',11,813,32769),(425,'Sotará',11,574,11958),(426,'Suárez',11,391,19690),(427,'Sucre',11,NULL,NULL),(428,'Timbío',11,180,33883),(429,'Timbiquí',11,1813,21618),(430,'Toribío',11,399,26616),(431,'Totoró',11,NULL,20870),(432,'Villa Rica',11,78,14378),(433,'Valledupar',12,4400,490075),(434,'Aguachica',12,976,118652),(435,'Astrea',12,563,18434),(436,'Becerril',12,1144,20477),(437,'Bosconia',12,609,40315),(438,'Chimichagua',12,1568,30289),(439,'Chiriguaná',12,1103,27006),(440,'Curumaní',12,890,34838),(441,'El Copey',12,968,28550),(442,'El Paso',12,823,34620),(443,'Gamarra',12,320,12444),(444,'La Gloria',12,736,14989),(445,'La Jagua de Ibirico',12,729,46722),(446,'Manaure Balcón del Cesar',12,1264,9313),(447,'Pailitas',12,512,22083),(448,'Pelaya',12,371,18497),(449,'Pueblo Bello',12,734,22929),(450,'Río de Oro',12,549,14041),(451,'San Alberto',12,611,23040),(452,'San Diego',12,687,18531),(453,'San Martín',12,789,20452),(454,'Tamalameque',12,511,13862),(455,'Teorama',12,852,21524),(456,'Urumita',12,329,10198),(457,'Quibdó',13,3338,130825),(458,'Acandí',13,1551,14),(459,'Alto Baudó',13,1532,NULL),(460,'El Atrato',13,725,5519),(461,'Bagadó',13,777,13174),(462,'Bahía Solano',13,1667,NULL),(463,'Bajo Baudó',13,4840,18561),(464,'Bojayá',13,3693,9941),(465,'Carmen del Darién',13,4700,5462),(466,'Cértegui',13,342,4683),(467,'Condoto',13,890,14660),(468,'Cantón de San Pablo',13,386,7970),(469,'El Carmen de Atrato',13,1017,14049),(470,'Litoral del San Juan',13,3755,11579),(471,'Istmina',13,2480,25351),(472,'Juradó',13,992,NULL),(473,'Lloró',13,905,11197),(474,'Medio Atrato',13,562,29487),(475,'Medio Baudó',13,NULL,13423),(476,'Medio San Juan',13,620,9073),(477,'Nóvita',13,NULL,NULL),(478,'Nuquí',13,NULL,8800),(479,'Riosucio',13,5822,28832),(480,'San José del Palmar',13,940,4768),(481,'Sipí',13,1274,408),(482,'Tadó',13,1013,18906),(483,'Unguía',13,1307,12192),(484,'Unión Panamericana',13,1600,6590),(485,'Montería',14,3141,490935),(486,'Ayapel',14,NULL,47247),(487,'Buenavista',14,846,18344),(488,'Canalete',14,394,14831),(489,'Cereté',14,352,94935),(490,'Chimá',14,335,13492),(491,'Chinú',14,NULL,50743),(492,'Ciénaga de Oro',14,751,64226),(493,'Cotorra',14,89,16215),(494,'La Apartada',14,271,15204),(495,'Santa Cruz de Lorica',14,960,115461),(496,'Los Córdobas',14,NULL,15886),(497,'Momil',14,152,16264),(498,'Montelíbano',14,1820,90450),(499,'Moñitos',14,NULL,25095),(500,'Planeta Rica',14,NULL,64776),(501,'Pueblo Nuevo',14,NULL,42446),(502,'Puerto Escondido',14,NULL,19474),(503,'Puerto Libertador',14,NULL,55622),(504,'Purísima',14,122,14705),(505,'Sahagún',14,993,90494),(506,'San Andrés de Sotavento',14,314,48404),(507,'San Antero',14,205,34196),(508,'San Bernardo del Viento',14,318,36512),(509,'San Carlos',14,505,23532),(510,'San Pelayo',14,481,45816),(511,'Tierralta',14,4728,78770),(512,'Tuchín',14,NULL,NULL),(513,'Valencia',14,135,825948),(514,'Agua de Dios',15,84,10995),(515,'Albán',15,57,NULL),(516,'Anapoima',15,124,14519),(517,'Anolaima',15,NULL,12911),(518,'Apulo',15,122,7812),(519,'Arbeláez',15,152,12292),(520,'Beltrán',15,NULL,NULL),(521,'Bituima',15,NULL,NULL),(522,'Bojacá',15,109,11254),(523,'Cabrera',15,NULL,NULL),(524,'Cachipay',15,56,9833),(525,'Cajicá',15,50,82244),(526,'Caparrapí',15,NULL,10301),(527,'Cáqueza',15,38,17048),(528,'Carmen de Carupa',15,228,9109),(529,'Chaguaní',15,142,3981),(530,'Chía',15,80,149570),(531,'Chipaque',15,139,8400),(532,'Choachí',15,223,10729),(533,'Chocontá',15,301,25257),(534,'Cogua',15,113,22361),(535,'Cota',15,55,32691),(536,'Cucunubá',15,112,7479),(537,'El Colegio',15,NULL,23886),(538,'El Peñón',15,132,4805),(539,'El Rosal',15,87,22065),(540,'Facatativá',15,158,117133),(541,'Fómeque',15,NULL,12214),(542,'Fosca',15,126,7524),(543,'Funza',15,70,80937),(544,'Fúquene',15,90,5617),(545,'Fusagasugá',15,239,170241),(546,'Gachalá',15,448,5715),(547,'Gachancipá',15,44,17026),(548,'Gachetá',15,262,11086),(549,'Gama',15,108,3996),(550,'Girardot',15,127,129834),(551,'Granada',15,NULL,NULL),(552,'Guachetá',15,177,11385),(553,'Guaduas',15,NULL,41838),(554,'Guasca',15,346,14759),(555,'Guataquí',15,87,2630),(556,'Guatavita',15,247,6898),(557,'Guayabal de Síquima',15,NULL,NULL),(558,'Guayabetal',15,NULL,NULL),(559,'Gutiérrez',15,NULL,NULL),(560,'Jerusalén',15,NULL,NULL),(561,'Junín',15,337,8610),(562,'La Calera',15,69,29868),(563,'La Mesa',15,148,32694),(564,'La Palma',15,NULL,NULL),(565,'La Peña',15,NULL,NULL),(566,'La Vega',15,153,13085),(567,'Lenguazaque',15,154,10268),(568,'Machetá',15,229,6316),(569,'Madrid',15,604,3223334),(570,'Manta',15,121,140000),(571,'Medina',15,NULL,7281),(572,'Mosquera',15,1770,10203),(573,'Nariño',15,33268,1630592),(574,'Nemocón',15,98,13488),(575,'Nilo',15,NULL,4456),(576,'Nimaima',15,59,6679),(577,'Nocaima',15,NULL,NULL),(578,'Pacho',15,403,24413),(579,'Paime',15,NULL,4502),(580,'Pandi',15,NULL,NULL),(581,'Paratebueno',15,NULL,7726),(582,'Pasca',15,264,12175),(583,'Puerto Salgar',15,NULL,15019),(584,'Pulí',15,NULL,NULL),(585,'Quebradanegra',15,NULL,4738),(586,'Quetame',15,138,7141),(587,'Quipile',15,128,8164),(588,'Ricaurte',15,130,12881),(589,'San Antonio del Tequendama',15,82,13084),(590,'San Bernardo',15,249,7417),(591,'San Cayetano',15,304,NULL),(592,'San Francisco',15,601,808988),(593,'San Juan de Rioseco',15,118,7547),(594,'Sasaima',15,114,9807),(595,'Sesquilé',15,141,13936),(596,'Sibaté',15,126,33491),(597,'Silvania',15,163,22020),(598,'Simijaca',15,107,13077),(599,'Soacha',15,184,660179),(600,'Sopó',15,112,26769),(601,'Subachoque',15,212,16117),(602,'Suesca',15,177,17318),(603,'Supatá',15,128,5022),(604,'Sutatausa',15,67,5564),(605,'Susa',15,86,12302),(606,'Sutatausa',15,67,5564),(607,'Tabio',15,75,27033),(608,'Tausa',15,204,8801),(609,'Tena',15,55,8941),(610,'Tenjo',15,108,18387),(611,'Tibacuy',15,84,4828),(612,'Tibirita',15,57,2950),(613,'Tocaima',15,150,13649),(614,'Tocancipá',15,246,39996),(615,'Topaipí',15,150,4529),(616,'Ubalá',15,505,10718),(617,'Ubaque',15,105,6166),(618,'Ubaté',15,102,42558),(619,'Une',15,233,9196),(620,'Útica',15,92,NULL),(621,'Venecia',15,121,4060),(622,'Vergara',15,146,NULL),(623,'Vianí',15,68,NULL),(624,'Villagómez',15,63,2171),(625,'Villapinzón',15,249,19742),(626,'Villeta',16,141,43574),(627,'Viotá',15,208,12589),(628,'Yacopí',15,1095,10887),(629,'Zipacón',15,70,5570),(630,'Zipaquirá',15,194,196409),(631,'Inírida',16,16165,19816),(632,'Barranco Minas',16,NULL,NULL),(633,'Cacahual',16,73,26932),(634,'La Guadalupe',16,6457,NULL),(635,'Mapiripán',17,11900,6036),(636,'Morichal Nuevo',16,NULL,NULL),(637,'Pana Pana',16,NULL,NULL),(638,'Puerto Colombia',16,73,26932),(639,'San Felipe',16,NULL,2050),(640,'San José del Guaviare',17,13912,52815),(641,'Calamar',17,16200,9091),(642,'El Retorno',17,11681,11340),(643,'Miraflores',17,11709,5007),(644,'Neiva',18,1553,380019),(645,'Acevedo',18,NULL,36649),(646,'Colombia',18,1141748,51874024),(647,'Aipe',18,801,26219),(648,'Algeciras',18,568,24499),(649,'Altamira',18,188,4293),(650,'Baraya',18,737,6679),(651,'Campoalegre',18,NULL,35057),(652,'Colombia',18,1141748,51874024),(653,'Guadalupe',18,NULL,15913),(654,'Garzón',18,580,74136),(655,'Gigante',18,NULL,36055),(656,'Hobo',18,NULL,NULL),(657,'Íquira',18,521,9064),(658,'Isnos',18,NULL,24593),(659,'La Argentina',18,626,12475),(660,'La Plata',18,1271,57381),(661,'Nátaga',18,NULL,NULL),(662,'Oporapa',18,150,11111),(663,'Paicol',18,NULL,NULL),(664,'Palermo',18,92,35569),(665,'Palestina',18,220,10454),(666,'El Pital',18,210,12246),(667,'Pitalito',18,666,128630),(668,'Rivera',18,NULL,22877),(669,'Saladoblanco',18,290,10076),(670,'San Agustín',18,1310,34420),(671,'Santa María',18,378,10215),(672,'Suaza',18,383,17376),(673,'Tarqui',18,347,16108),(674,'Tello',18,494,10273),(675,'Teruel',19,762,NULL),(676,'Tesalia',18,502,9767),(677,'Timaná',18,198,20315),(678,'Villavieja',18,719,NULL),(679,'Yaguará',18,389,8952),(680,'Riohacha',19,5020,167865),(681,'Albania',19,425,19429),(682,'Barrancas',19,1060,38232),(683,'Dibulla',19,1847,NULL),(684,'Distracción',19,220,11934),(685,'El Molino',19,190,5937),(686,'Fonseca',19,662,32220),(687,'Hatonuevo',19,347,24910),(688,'La Jagua del Pilar',19,267,2721),(689,'Maicao',19,1782,185072),(690,'Manaure',20,1971,67584),(691,'San Juan del Cesar',19,1415,49584),(692,'Uribia',19,7905,198890),(693,'Urumita',19,329,10198),(694,'Villanueva',19,265,356),(695,'Santa Marta',20,294,515556),(696,'Algarrobo',20,409,14294),(697,'Aracataca',20,1755,41872),(698,'Ariguaní',20,NULL,32758),(699,'Cerro de San Antonio',20,NULL,8058),(700,'Chibolo',20,619,15960),(701,'Ciénaga',20,1812,124339),(702,'Concordia',20,111,9681),(703,'El Banco',20,816,72131),(704,'El Piñón',20,547,17308),(705,'El Retén',20,268,19345),(706,'Fundación',20,1157,90514),(707,'Guamal',20,7812,25312),(708,'Nueva Granada',20,843,17470),(709,'Pedraza',20,445,7865),(710,'Santa Bárbara de Pinto',20,497,9345),(711,'Pivijay',20,NULL,33047),(712,'Plato',20,7812,61766),(713,'Puebloviejo',20,678,33030),(714,'Remolino',20,599,7840),(715,'Sabanas de San Ángel',20,977,14060),(716,'Salamina',20,175,8239),(717,'San Sebastián de Buenavista',20,421,18865),(718,'San Zenón',20,233,9107),(719,'Santa Ana',21,1479,22723),(720,'Sitionuevo',20,948,33440),(721,'Tenerife',20,694,12364),(722,'Zapayán',20,353,8464),(723,'Zona Bananera',20,503,56504),(724,'Villavicencio',21,1328,531275),(725,'Acacías',21,1149,88023),(726,'Barranca de Upía',21,815,3926),(727,'Cabuyaro',21,NULL,NULL),(728,'Castilla la Nueva',21,503,13611),(729,'Cubarral',21,576,11599),(730,'Cumaral',21,580,21397),(731,'El Calvario',21,NULL,NULL),(732,'El Castillo',21,NULL,NULL),(733,'El Dorado',21,NULL,NULL),(734,'Fuente de Oro',21,576,11599),(735,'Granada',21,350,68876),(736,'Guamal',21,NULL,25312),(737,'Mapiripán',21,11900,6036),(738,'Mesetas',21,1980,9751),(739,'La Macarena',21,11229,32861),(740,'Uribe',21,6037,8180),(741,'Lejanías',21,788,10576),(742,'Puerto Concordia',21,NULL,8086),(743,'Puerto Gaitán',21,17499,41513),(744,'Puerto Lleras',21,2061,8982),(745,'Puerto López',21,6740,33440),(746,'Puerto Rico',21,9104,3221789),(747,'Restrepo',21,289,17610),(748,'San Carlos de Guaroa',22,814,11512),(749,'San Juan de Arama',21,1163,NULL),(750,'San Juanito',21,162,NULL),(751,'San Martín',21,6454,22281),(752,'Vista Hermosa',21,4849,16525),(753,'Pasto',22,1181,410835),(754,'San José de Albán',22,43,8197),(755,'Aldana',22,52,6085),(756,'Ancuya',22,34,19951),(757,'Arboleda',22,148,NULL),(758,'Barbacoas',22,2324,38708),(759,'Belén',22,NULL,NULL),(760,'Arboleda',22,NULL,NULL),(761,'Buesaco',22,282,19951),(762,'Chachagüí',22,148,12419),(763,'Colón',22,82,41205),(764,'Consacá',22,280,NULL),(765,'Contadero',22,NULL,NULL),(766,'Córdoba',22,282,14006),(767,'Cuaspud',22,1092,6498),(768,'Cumbal',22,NULL,41205),(769,'Cumbitara',22,280,5096),(770,'El Charco',22,2485,38207),(771,'El Peñol',22,159,18845),(772,'El Rosario',22,1092,6498),(773,'El Tablón',22,315,13255),(774,'El Tambo',22,344,12457),(775,'Funes',22,NULL,NULL),(776,'Guachucal',22,159,18845),(777,'Guaitarilla',22,121,10774),(778,'Gualmatán',22,36,NULL),(779,'Iles',22,NULL,NULL),(780,'Imués',22,128,5847),(781,'Ipiales',22,1707,166079),(782,'La Cruz',22,257,16674),(783,'La Florida',22,139,9047),(784,'La Llanada',22,NULL,NULL),(785,'La Tola',22,128,5847),(786,'La Unión',22,NULL,28659),(787,'Leiva',22,316,8201),(788,'Linares',22,115,8974),(789,'Los Andes',22,NULL,8703),(790,'Magüí Payán',22,NULL,18262),(791,'Mallama',22,467,8149),(792,'Mosquera',22,1770,10203),(793,'Nariño',22,33268,1630592),(794,'Olaya Herrera',22,NULL,33132),(795,'Ospina',22,NULL,NULL),(796,'Policarpa',22,467,8149),(797,'Potosí',22,397,10186),(798,'Providencia',22,42,4619),(799,'Puerres',22,478,8384),(800,'Pupiales',22,NULL,16431),(801,'Ricaurte',22,1211,18067),(802,'Roberto Payán',22,1179,10473),(803,'Samaniego',22,239,49085),(804,'Sandoná',22,101,18859),(805,'San Bernardo',22,70,8874),(806,'San Lorenzo',22,249,16653),(807,'San Pablo',22,143,12929),(808,'San Pedro de Cartago',22,60,NULL),(809,'Santa Bárbara',22,3760,257052),(810,'Santacruz',22,560,NULL),(811,'Sapuyes',22,118,NULL),(812,'Taminango',23,284,20537),(813,'Tanguá',22,146,31086),(814,'Tumaco',22,3760,257052),(815,'Túquerres',22,172,41205),(816,'Yacuanquer',22,178,10579),(817,'Cúcuta',23,1176,806378),(818,'Ábrego',23,1582,38627),(819,'Arboledas',23,NULL,8984),(820,'Bochalema',23,172,6973),(821,'Bucarasica',23,NULL,4570),(822,'Cácota',23,140,1925),(823,'Cáchira',23,606,10970),(824,'Chinácota',23,1687,16348),(825,'Chitagá',23,1172,10554),(826,'Convención',23,907,18112),(827,'Cundinamarca',23,22623,3242999),(828,'Durania',23,NULL,3768),(829,'El Carmen',23,1687,12001),(830,'El Tarra',23,482,10957),(831,'El Zulia',23,449,26019),(832,'Gramalote',23,151,5567),(833,'Hacarí',23,597,9745),(834,'Herrán',23,NULL,NULL),(835,'La Esperanza',23,665,11040),(836,'La Playa de Belén',23,241,8546),(837,'Labateca',23,253,5867),(838,'Los Patios',23,133,81122),(839,'Lourdes',23,NULL,NULL),(840,'Mutiscua',23,159,3759),(841,'Ocaña',23,672,101158),(842,'Pamplona',23,24,205762),(843,'Pamplonita',23,176,4932),(844,'Puerto Santander',23,NULL,NULL),(845,'Ragonvalia',23,100,6891),(846,'Salazar de Las Palmas',23,34,10728),(847,'San Calixto',23,387,9961),(848,'San Cayetano',23,144,5424),(849,'Santiago',23,173,NULL),(850,'Sardinata',23,1431,22632),(851,'Santo Domingo de Silos',24,NULL,NULL),(852,'Teorama',23,852,21524),(853,'Toledo',23,1578,17283),(854,'Villa Caro',23,402,5192),(855,'Villa del Rosario',23,228,69833),(856,'Mocoa',24,1030,56398),(857,'Colón',24,NULL,NULL),(858,'Puerto Asís',24,26103,67211),(859,'Puerto Caicedo',24,864,11122),(860,'Puerto Guzmán',24,NULL,17495),(861,'Puerto Leguízamo',24,10617,20045),(862,'Sibundoy',24,64,14104),(863,'Orito',25,1862,57774),(864,'San Francisco',24,601,808988),(865,'San Miguel',24,358,NULL),(866,'Santiago de Chile',24,838,6257516),(867,'Villagarzón',24,1250,23700),(868,'Armenia',25,140,304314),(869,'Buenavista',25,NULL,2954),(870,'Calarcá',25,219,75979),(871,'Circasia',25,91,28162),(872,'Córdoba',25,NULL,5888),(873,'Filandia',25,109,12066),(874,'Génova',25,298,7516),(875,'La Tebaida',26,89,42163),(876,'Montenegro',25,149,41996),(877,'Pijao',25,NULL,NULL),(878,'Quimbaya',25,NULL,35276),(879,'Salento',25,376,7247),(880,'Pereira',26,702,481768),(881,'Apía',26,NULL,12613),(882,'Balboa',26,NULL,NULL),(883,'Belén de Umbría',26,NULL,25276),(884,'Dosquebradas',26,71,179301),(885,'Guática',26,95,12423),(886,'La Celia',26,NULL,9660),(887,'La Virginia',26,NULL,28488),(888,'Marsella',26,NULL,17208),(889,'Mistrató',27,690,17527),(890,'Pueblo Rico',26,561,14429),(891,'Quinchía',26,150,34069),(892,'Santa Rosa de Cabal',26,564,60018),(893,'Santuario',26,201,12826),(894,'San Andrés',27,26,55426),(895,'Bucaramanga',28,162,607428),(896,'Aguada',28,76,1855),(897,'Albania',28,1650,NULL),(898,'Aratoca',28,NULL,NULL),(899,'Barbosa',28,57,25768),(900,'Barichara',28,13,7063),(901,'Barrancabermeja',28,1274,300000),(902,'Betulia',28,413,5110),(903,'Bolívar',28,1419,9567),(904,'Cabrera',28,NULL,NULL),(905,'California',28,411,10540),(906,'Capitanejo',28,NULL,NULL),(907,'Carcasí',28,NULL,5039),(908,'Cepitá',28,139,1865),(909,'Cerrito',28,NULL,NULL),(910,'Charalá',28,411,10540),(911,'Charta',28,152,3209),(912,'Chimá',28,335,13492),(913,'Chipatá',28,94,5088),(914,'Cimitarra',28,238,50892),(915,'Concepción',28,NULL,NULL),(916,'Confines',28,NULL,NULL),(917,'Contratación',28,NULL,NULL),(918,'Coromoro',28,468,12966),(919,'Curití',28,238,11653),(920,'El Carmen de Chucurí',28,NULL,17638),(921,'El Guacamayo',28,NULL,NULL),(922,'El Peñón',28,NULL,NULL),(923,'El Playón',28,468,12966),(924,'Encino',28,417,2497),(925,'Enciso',28,475,3323),(926,'Florián',28,NULL,NULL),(927,'Florida Blanca',28,NULL,NULL),(928,'Galán',28,NULL,NULL),(929,'Gámbita',28,56,3679),(930,'San Juan de Girón',28,475,160403),(931,'Guaca',28,382,6916),(932,'Guadalupe',28,15581,3390),(933,'Guapotá',28,NULL,NULL),(934,'Guavatá',28,56,3679),(935,'Güepsa',28,270,4953),(936,'Hato',28,NULL,NULL),(937,'Jesús María',28,60,3390),(938,'Jordán',28,302,NULL),(939,'La Belleza',28,NULL,NULL),(940,'La Paz',28,270,4953),(941,'Landázuri',28,630,9238),(942,'Lebrija',28,488,42895),(943,'Los Santos',28,302,12433),(944,'Macaravita',28,84,NULL),(945,'Málaga',28,58,19884),(946,'Matanza',28,NULL,NULL),(947,'Mogotes',28,488,10165),(948,'Molagavita',28,NULL,NULL),(949,'Ocamonte',28,84,NULL),(950,'Oiba',28,287,11738),(951,'Onzaga',28,487,5054),(952,'Palmar',28,22,3330),(953,'Palmas del Socorro',28,57,2241),(954,'Páramo',28,NULL,NULL),(955,'Piedecuesta',28,380,117364),(956,'Pinchote',28,NULL,NULL),(957,'Puerto Parra',28,1452,6462),(958,'Puerto Wilches',28,1588,31698),(959,'Puente Nacional',28,315,12586),(960,'Rionegro',28,1064,27114),(961,'Sabana de Torres',28,1456,33055),(962,'San Andrés',28,222,NULL),(963,'San Benito',28,67,33133),(964,'San Gil',28,150,46152),(965,'San Joaquín',28,NULL,NULL),(966,'San José de Miranda',28,85,NULL),(967,'San Miguel',28,115,29997),(968,'San Vicente de Chucurí',28,2028,33133),(969,'Santa Bárbara',28,186,NULL),(970,'Santa Helena del Opón',28,198,NULL),(971,'Simacota',28,1413,NULL),(972,'El Socorro',28,136,29997),(973,'San José de Suaita',28,NULL,19376),(974,'Sucre',28,882,NULL),(975,'Suratá',28,261,NULL),(976,'Tona',28,342,NULL),(977,'Valle de San José',29,250,310456),(978,'Vélez',28,250,19376),(979,'Vetas',28,452,2435),(980,'Villanueva',28,48,NULL),(981,'Zapatoca',28,360,NULL),(982,'Sincelejo',29,275,310456),(983,'Betulia',29,413,5110),(984,'Buenavista',29,144,10829),(985,'Caimito',29,407,12077),(986,'Colosó',29,127,NULL),(987,'Coveñas',29,74,11270),(988,'Chalán',29,NULL,NULL),(989,'Corozal',29,264,70591),(990,'El Roble',29,NULL,9786),(991,'Galeras',29,326,20239),(992,'Guaranda',29,370,17422),(993,'La Unión',29,224,11510),(994,'Los Palmitos',29,125,21831),(995,'Majagual',29,826,33258),(996,'Morroa',29,161,14429),(997,'Ovejas',29,447,21091),(998,'San Antonio de Palmito',29,176,13682),(999,'Sampués',29,210,37925),(1000,'San Benito Abad',29,1428,25442),(1001,'San Juan de Betulia',29,199,13437),(1002,'San Marcos',29,881,60735),(1003,'San Onofre',29,1049,46383),(1004,'San Pedro',30,999,18029),(1005,'Sincé',29,407,30773),(1006,'Sucre',29,1139,23971),(1007,'Tolú',29,347,32922),(1008,'Toluviejo',29,277,20033),(1009,'Ibagué',30,1498,541101),(1010,'Alvarado',30,311,8873),(1011,'Ambalema',30,239,6683),(1012,'Estado Anzoátegui',30,43300,1469747),(1013,'Ataco',30,997,13470),(1014,'Cajamarca',30,520,17309),(1015,'Carmen de Apicalá',30,183,8880),(1016,'Casabianca',30,182,6639),(1017,'Chaparral',30,2124,50367),(1018,'Coello',30,333,9887),(1019,'Coyaima',30,664,28379),(1020,'Cunday',30,526,9544),(1021,'Dolores',30,NULL,NULL),(1022,'El Espinal',30,231,70494),(1023,'Falan',30,188,9204),(1024,'Flandes',30,95,28389),(1025,'Fresno',30,208,28920),(1026,'Guamo',30,561,30516),(1027,'Herveo',30,342,7893),(1028,'Honda',30,309,24693),(1029,'Icononzo',30,232,10801),(1030,'Lérida',30,270,17197),(1031,'Líbano',30,299,36231),(1032,'Melgar',30,196,37224),(1033,'Murillo',30,417,4953),(1034,'Natagaima',30,862,22455),(1035,'Ortega',30,946,45524),(1036,'Palocabildo',30,65,9120),(1037,'Piedras',30,355,5662),(1038,'Planadas',30,NULL,21557),(1039,'Prado',30,448,7607),(1040,'Purificación',30,422,29539),(1041,'Rioblanco',30,2,19090),(1042,'Roncesvalles',30,790,6340),(1043,'Rovira',30,733,20452),(1044,'Saldaña',30,214,14329),(1045,'San Antonio',30,1209,1434625),(1046,'San Luis',30,425,3015),(1047,'Santa Isabel',30,416,6382),(1048,'Suárez',31,190,4519),(1049,'Valle de San Juan',30,198,6178),(1050,'Venadillo',30,352,19586),(1051,'Villahermosa',30,80,340060),(1052,'Villarrica',30,204,5449),(1053,'Cali',31,564,2471474),(1054,'Alcalá',31,61,14062),(1055,'Andalucía',31,168,18132),(1056,'Ansermanuevo',31,NULL,19557),(1057,'Argelia',31,87,6440),(1058,'Bolívar',31,602,13954),(1059,'Buenaventura',31,6078,311827),(1060,'Buga',31,832,128945),(1061,'Bugalagrande',31,NULL,21167),(1062,'Caicedonia',31,219,28825),(1063,'Calima',31,219,16054),(1064,'Candelaria',31,NULL,87811),(1065,'Cartago',31,279,210558),(1066,'Dagua',31,886,36400),(1067,'El Águila',31,199,11069),(1068,'El Cairo',31,283,9976),(1069,'El Cerrito',31,NULL,56470),(1070,'El Dovio',31,NULL,8508),(1071,'Florida',31,170304,23372215),(1072,'Ginebra',31,313,21055),(1073,'Guacarí',31,200,33191),(1074,'Jamundí',31,577,167147),(1075,'La Cumbre',31,235,11512),(1076,'La Unión',31,125,41013),(1077,'La Victoria',31,276,13247),(1078,'Leiva',31,316,8201),(1079,'Obando',31,213,14980),(1080,'Palmira',31,1123,358895),(1081,'Pradera',31,407,45360),(1082,'Restrepo',31,135,16227),(1083,'Riofrío',31,280,14716),(1084,'Roldanillo',31,217,33697),(1085,'San Pedro',31,240,18128),(1086,'Sevilla',31,640,43738),(1087,'Toro',31,166,16394),(1088,'Tuluá',31,911,218812),(1089,'Tuluá',31,911,218812),(1090,'Ulloa',31,45,5457),(1091,'Versalles',32,352,7214),(1092,'Vijes',31,122,11010),(1093,'Yotoco',31,321,16263),(1094,'Yumbo',31,245,92192),(1095,'Zarzal',31,355,41925),(1096,'Mitú',33,16,29850),(1097,'Carurú',32,6982,3327),(1098,'Papunaua',32,5938,879),(1099,'Taraira',32,6619,NULL),(1101,'Puerto Carreño',33,12409,16763),(1102,'Cumaribo',33,65193,43138),(1103,'La Primavera',33,22159,9690);
/*!40000 ALTER TABLE `cities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `companies`
--

DROP TABLE IF EXISTS `companies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `companies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `agent_id` int DEFAULT NULL,
  `status_id` int DEFAULT NULL,
  `rut_nit` varchar(50) NOT NULL,
  `verification_digit` tinyint unsigned DEFAULT NULL,
  `legal_name` varchar(255) NOT NULL,
  `commercial_name` varchar(255) DEFAULT NULL,
  `description` text,
  `domain` varchar(255) DEFAULT NULL,
  `revenue` decimal(15,2) DEFAULT NULL,
  `employee_count` int DEFAULT '0',
  `company_department_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_rut_empresa` (`rut_nit`),
  KEY `status_id` (`status_id`),
  KEY `idx_legal_name` (`legal_name`),
  KEY `idx_commercial_name` (`commercial_name`),
  KEY `idx_companies_deleted_at` (`deleted_at`),
  CONSTRAINT `empresas_ibfk_1` FOREIGN KEY (`status_id`) REFERENCES `statuses` (`id`),
  CONSTRAINT `fk_company_dept` FOREIGN KEY (`company_department_id`) REFERENCES `company_departments` (`id`),
  CONSTRAINT `chk_domain_min` CHECK (((`domain` is null) or ((`domain` like _utf8mb4'%.%') and (not((`domain` like _utf8mb4'% '))) and (not((`domain` like _utf8mb4' %')))))),
  CONSTRAINT `chk_ingresos_pos` CHECK ((`revenue` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `company_activities`
--

DROP TABLE IF EXISTS `company_activities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `company_activities` (
  `id` int NOT NULL AUTO_INCREMENT,
  `company_id` int NOT NULL,
  `isic_code` smallint unsigned NOT NULL,
  `is_primary` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_empresa_ciiu` (`company_id`,`isic_code`),
  KEY `isic_code` (`isic_code`),
  CONSTRAINT `empresas_actividades_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`),
  CONSTRAINT `empresas_actividades_ibfk_2` FOREIGN KEY (`isic_code`) REFERENCES `economic_activities` (`isic_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--

--
-- Table structure for table `company_associations`
--

DROP TABLE IF EXISTS `company_associations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `company_associations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `parent_company_id` int NOT NULL,
  `child_company_id` int NOT NULL,
  `relation_type_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_asociacion` (`parent_company_id`,`child_company_id`),
  KEY `child_company_id` (`child_company_id`),
  KEY `relation_type_id` (`relation_type_id`),
  KEY `idx_orig_holding` (`parent_company_id`),
  KEY `idx_dest_holding` (`child_company_id`),
  CONSTRAINT `asociaciones_empresas_ibfk_1` FOREIGN KEY (`parent_company_id`) REFERENCES `companies` (`id`),
  CONSTRAINT `asociaciones_empresas_ibfk_2` FOREIGN KEY (`child_company_id`) REFERENCES `companies` (`id`),
  CONSTRAINT `asociaciones_empresas_ibfk_3` FOREIGN KEY (`relation_type_id`) REFERENCES `company_relation_types` (`id`),
  CONSTRAINT `fk_company_rel_type` FOREIGN KEY (`relation_type_id`) REFERENCES `company_relation_types` (`id`),
  CONSTRAINT `fk_holding_dest` FOREIGN KEY (`child_company_id`) REFERENCES `companies` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_holding_origin` FOREIGN KEY (`parent_company_id`) REFERENCES `companies` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `company_departments`
--

DROP TABLE IF EXISTS `company_departments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `company_departments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `department_name` varchar(255) NOT NULL,
  `description` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_nombre_depto_emp` (`department_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `company_departments`
--

LOCK TABLES `company_departments` WRITE;
/*!40000 ALTER TABLE `company_departments` DISABLE KEYS */;
INSERT INTO `company_departments` VALUES (1,'Administrativo',NULL),(2,'Comercial',NULL),(3,'Proyectos',NULL),(4,'Compras',NULL),(5,'Ventas',NULL),(6,'Recursos Humanos',NULL),(7,'Marketing',NULL),(8,'Producción',NULL),(9,'Contabilidad',NULL),(10,'Tecnología',NULL),(11,'Mantenimiento',NULL),(12,'Logística',NULL),(13,'Otro',NULL);
/*!40000 ALTER TABLE `company_departments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `company_relation_types`
--

DROP TABLE IF EXISTS `company_relation_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `company_relation_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `inverse_type_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_nombre_relacion` (`name`),
  KEY `fk_inverse_type` (`inverse_type_id`),
  CONSTRAINT `fk_comp_rel_inverse` FOREIGN KEY (`inverse_type_id`) REFERENCES `company_relation_types` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `company_relation_types`
--

LOCK TABLES `company_relation_types` WRITE;
/*!40000 ALTER TABLE `company_relation_types` DISABLE KEYS */;
-- ID 1: Matriz (Inv: 2) | ID 2: Filial (Inv: 1) | ID 3: Aliada (Inv: 3)
INSERT INTO `company_relation_types` VALUES (1,'Proveedor',2,'2026-01-15 23:38:17'),(2,'Cliente',1,'2026-01-15 23:38:17'),(3,'Socio',3,'2026-01-15 23:38:17'),(4,'Filial',5,'2026-01-15 23:38:17'),(5,'Matriz',4,'2026-01-15 23:38:17'),(6,'Competencia',6,'2026-01-15 23:38:17'),(7,'Partner',7,'2026-01-15 23:38:17'),(8,'Sede principal',9,'2026-01-16 21:14:13'),(9,'Sede secundaria',8,'2026-01-16 21:14:13');
/*!40000 ALTER TABLE `company_relation_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `countries`
--

DROP TABLE IF EXISTS `countries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `countries` (
  `id` int NOT NULL AUTO_INCREMENT,
  `country_name` varchar(255) DEFAULT NULL,
  `phone_code` varchar(10) DEFAULT NULL,
  `area_km2` int unsigned DEFAULT NULL,
  `population` bigint unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_pais` (`country_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `countries`
--

LOCK TABLES `countries` WRITE;
/*!40000 ALTER TABLE `countries` DISABLE KEYS */;
INSERT INTO `countries` VALUES (1,'Colombia','+57',1141748,51874024),(2,'España','+34',506030,49400000),(3,'Estados Unidos','1',0,0);
/*!40000 ALTER TABLE `countries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `custom_columns_metadata`
--

DROP TABLE IF EXISTS `custom_columns_metadata`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `custom_columns_metadata` (
  `id` int NOT NULL AUTO_INCREMENT,
  `table_name` varchar(100) NOT NULL,
  `column_name` varchar(100) NOT NULL,
  `display_name` varchar(100) NOT NULL,
  `data_type` varchar(50) NOT NULL,
  `is_protected` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_col` (`table_name`,`column_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_columns_metadata`
--

LOCK TABLES `custom_columns_metadata` WRITE;
/*!40000 ALTER TABLE `custom_columns_metadata` DISABLE KEYS */;
/*!40000 ALTER TABLE `custom_columns_metadata` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `economic_activities`
--

DROP TABLE IF EXISTS `economic_activities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `economic_activities` (
  `isic_code` smallint unsigned NOT NULL,
  `description` text,
  PRIMARY KEY (`isic_code`),
  CONSTRAINT `chk_ciiu_rango` CHECK ((`isic_code` between 1 and 9999))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `economic_activities`
--

LOCK TABLES `economic_activities` WRITE;
/*!40000 ALTER TABLE `economic_activities` DISABLE KEYS */;
INSERT INTO `economic_activities` VALUES (111,'Cultivo de cereales (excepto arroz), legumbres y semillas oleaginosas.'),(112,'Cultivo de arroz.'),(113,'Cultivo de hortalizas, raíces y tubérculos.'),(114,'Cultivo de tabaco.'),(115,'Cultivo de plantas textiles.'),(119,'Otros cultivos transitorios n.c.p.'),(121,'Cultivo de frutas tropicales y subtropicales.'),(122,'Cultivo de plátano y banano.'),(123,'Cultivo de café.'),(124,'Cultivo de caña de azúcar.'),(125,'Cultivo de flor de corte.'),(126,'Cultivo de palma para aceite (palma africana) y otros frutos oleaginosos.'),(127,'Cultivo de plantas con las que se preparan bebidas.'),(128,'Cultivo de especias y de plantas aromáticas y medicinales.'),(129,'Otros cultivos permanentes n.c.p.'),(130,'Propagación de plantas (actividades de los viveros, excepto viveros forestales).'),(141,'Cría de ganado bovino y bufalino.'),(142,'Cría de caballos y otros equinos.'),(143,'Cría de ovejas y cabras.'),(144,'Cría de ganado porcino.'),(145,'Cría de aves de corral.'),(149,'Cría de otros animales n.c.p.'),(150,'Explotación mixta (agrícola y pecuaria).'),(161,'Actividades de apoyo a la agricultura.'),(162,'Actividades de apoyo a la ganadería.'),(163,'Actividades posteriores a la cosecha.'),(164,'Tratamiento de semillas para propagación.'),(170,'Caza ordinaria y mediante trampas y actividades de servicios conexas.'),(210,'Silvicultura y otras actividades forestales.'),(220,'Extracción de madera.'),(230,'Recolección de productos forestales diferentes a la madera.'),(240,'Servicios de apoyo a la silvicultura.'),(311,'Pesca marítima.'),(312,'Pesca de agua dulce.'),(321,'Acuicultura marítima.'),(322,'Acuicultura de agua dulce.'),(510,'Extracción de hulla (carbón de piedra).'),(520,'Extracción de carbón lignito.'),(610,'Extracción de petróleo crudo.'),(620,'Extracción de gas natural.'),(710,'Extracción de minerales de hierro.'),(721,'Extracción de minerales de uranio y de torio.'),(722,'Extracción de oro y otros metales preciosos.'),(723,'Extracción de minerales de níquel.'),(729,'Extracción de otros minerales metalíferos no ferrosos n.c.p.'),(811,'Extracción de piedra, arena, arcillas comunes, yeso y anhidrita.'),(812,'Extracción de arcillas de uso industrial, caliza, caolín y bentonitas.'),(820,'Extracción de esmeraldas, piedras preciosas y semipreciosas.'),(891,'Extracción de minerales para la fabricación de abonos y productos químicos.'),(892,'Extracción de halita (sal).'),(899,'Extracción de otros minerales no metálicos n.c.p.'),(910,'Actividades de apoyo para la extracción de petróleo y de gas natural.'),(990,'Actividades de apoyo para otras actividades de explotación de minas y canteras.'),(1011,'Procesamiento y conservación de carne y productos cárnicos.'),(1012,'Procesamiento y conservación de pescados, crustáceos y moluscos.'),(1020,'Procesamiento y conservación de frutas, legumbres, hortalizas y tubérculos.'),(1030,'Elaboración de aceites y grasas de origen vegetal y animal.'),(1040,'Elaboración de productos lácteos.'),(1051,'Elaboración de productos de molinería.'),(1052,'Elaboración de almidones y productos derivados del almidón.'),(1061,'Trilla de café.'),(1062,'Descafeinado, tostión y molienda del café.'),(1063,'Otros derivados del café.'),(1071,'Elaboración y refinación de azúcar.'),(1072,'Elaboración de panela.'),(1081,'Elaboración de productos de panadería.'),(1082,'Elaboración de cacao, chocolate y productos de confitería.'),(1083,'Elaboración de macarrones, fideos, alcuzcuz y productos farináceos similares.'),(1084,'Elaboración de comidas y platos preparados.'),(1089,'Elaboración de otros productos alimenticios n.c.p.'),(1090,'Elaboración de alimentos preparados para animales.'),(1101,'Destilación, rectificación y mezcla de bebidas alcohólicas.'),(1102,'Elaboración de bebidas fermentadas no destiladas.'),(1103,'Producción de malta, elaboración de cervezas y otras bebidas malteadas.'),(1104,'Elaboración de bebidas no alcohólicas, producción de aguas minerales y de otras aguas embotelladas.'),(1200,'Elaboración de productos de tabaco.'),(1311,'Preparación e hilatura de fibras textiles.'),(1312,'Tejeduría de productos textiles.'),(1313,'Acabado de productos textiles.'),(1391,'Fabricación de tejidos de punto y ganchillo.'),(1392,'Confección de artículos con materiales textiles, excepto prendas de vestir.'),(1393,'Fabricación de tapetes y alfombras para pisos.'),(1394,'Fabricación de cuerdas, cordeles, cables, bramantes y redes.'),(1399,'Fabricación de otros artículos textiles n.c.p.'),(1410,'Confección de prendas de vestir, excepto prendas de piel.'),(1420,'Fabricación de artículos de piel.'),(1430,'Fabricación de artículos de punto y ganchillo.'),(1511,'Curtido y recurtido de cueros; recurtido y teñido de pieles.'),(1512,'Fabricación de artículos de viaje, bolsos de mano y artículos similares elaborados en cuero, y fabricación de artículos de talabartería y guarnicionería.'),(1513,'Fabricación de artículos de viaje, bolsos de mano y artículos similares; artículos de talabartería y guarnicionería elaborados en otros materiales.'),(1521,'Fabricación de calzado de cuero y piel, con cualquier tipo de suela.'),(1522,'Fabricación de otros tipos de calzado, excepto calzado de cuero y piel.'),(1523,'Fabricación de partes del calzado.'),(1610,'Aserrado, acepillado e impregnación de la madera.'),(1620,'Fabricación de hojas de madera para enchapado; fabricación de tableros contrachapados, tableros laminados, tableros de partículas y otros tableros y paneles.'),(1630,'Fabricación de partes y piezas de madera, de carpintería y ebanistería para la construcción.'),(1640,'Fabricación de recipientes de madera.'),(1690,'Fabricación de otros productos de madera; fabricación de artículos de corcho, cestería y espartería.'),(1701,'Fabricación de pulpas (pastas) celulósicas; papel y cartón.'),(1702,'Fabricación de papel y cartón ondulado (corrugado); fabricación de envases, empaques y de embalajes de papel y cartón.'),(1709,'Fabricación de otros artículos de papel y cartón.'),(1811,'Actividades de impresión.'),(1812,'Actividades de servicios relacionados con la impresión.'),(1820,'Producción de copias a partir de grabaciones originales.'),(1910,'Fabricación de productos de hornos de coque.'),(1921,'Fabricación de productos de la refinación del petróleo.'),(1922,'Actividad de mezcla de combustibles.'),(2011,'Fabricación de sustancias y productos químicos básicos.'),(2012,'Fabricación de abonos y compuestos inorgánicos nitrogenados.'),(2013,'Fabricación de plásticos en formas primarias.'),(2014,'Fabricación de caucho sintético en formas primarias.'),(2021,'Fabricación de plaguicidas y otros productos químicos de uso agropecuario.'),(2022,'Fabricación de pinturas, barnices y revestimientos similares, tintas para impresión y masillas.'),(2023,'Fabricación de jabones y detergentes, preparados para limpiar y pulir; perfumes y preparados de tocador.'),(2029,'Fabricación de otros productos químicos n.c.p.'),(2030,'Fabricación de fibras sintéticas y artificiales.'),(2100,'Fabricación de productos farmacéuticos, sustancias químicas medicinales y productos botánicos de uso farmacéutico.'),(2211,'Fabricación de llantas y neumáticos de caucho.'),(2212,'Reencauche de llantas usadas.'),(2219,'Fabricación de formas básicas de caucho y otros productos de caucho n.c.p.'),(2221,'Fabricación de formas básicas de plástico.'),(2229,'Fabricación de artículos de plástico n.c.p.'),(2310,'Fabricación de vidrio y productos de vidrio.'),(2391,'Fabricación de productos refractarios.'),(2392,'Fabricación de materiales de arcilla para la construcción.'),(2393,'Fabricación de otros productos de cerámica y porcelana.'),(2394,'Fabricación de cemento, cal y yeso.'),(2395,'Fabricación de artículos de hormigón, cemento y yeso.'),(2396,'Corte, tallado y acabado de la piedra.'),(2399,'Fabricación de otros productos minerales no metálicos n.c.p.'),(2410,'Industrias básicas de hierro y de acero.'),(2421,'Industrias básicas de metales preciosos.'),(2429,'Industrias básicas de otros metales no ferrosos.'),(2431,'Fundición de hierro y de acero.'),(2432,'Fundición de metales no ferrosos.'),(2511,'Fabricación de productos metálicos para uso estructural.'),(2512,'Fabricación de tanques, depósitos y recipientes de metal, excepto los utilizados para el envase o transporte de mercancías.'),(2513,'Fabricación de generadores de vapor, excepto calderas de agua caliente para calefacción central.'),(2520,'Fabricación de armas y municiones.'),(2591,'Forja, prensado, estampado y laminado de metal; pulvimetalurgia.'),(2592,'Tratamiento y revestimiento de metales; mecanizado.'),(2593,'Fabricación de artículos de cuchillería, herramientas de mano y artículos de ferretería.'),(2599,'Fabricación de otros productos elaborados de metal n.c.p.'),(2610,'Fabricación de componentes y tableros electrónicos.'),(2620,'Fabricación de computadoras y de equipo periférico.'),(2630,'Fabricación de equipos de comunicación.'),(2640,'Fabricación de aparatos electrónicos de consumo.'),(2651,'Fabricación de equipo de medición, prueba, navegación y control'),(2652,'Fabricación de relojes'),(2660,'Fabricación de equipo de irradiación y equipo electrónico de uso médico y terapéutico'),(2670,'Fabricación de instrumentos ópticos y equipo fotográfico'),(2680,'Fabricación de medios magnéticos y ópticos para almacenamiento de datos'),(2711,'Fabricación de motores, generadores y transformadores eléctricos'),(2712,'Fabricación de aparatos de distribución y control de la energía eléctrica'),(2720,'Fabricación de pilas, baterías y acumuladores eléctricos'),(2731,'Fabricación de hilos y cables eléctricos y de fibra óptica'),(2732,'Fabricación de dispositivos de cableado'),(2740,'Fabricación de equipos eléctricos de iluminación'),(2750,'Fabricación de aparatos de uso doméstico'),(2790,'Fabricación de otros tipos de equipo eléctrico n.c.p.'),(2811,'Fabricación de motores, turbinas, y partes para motores de combustión interna.'),(2812,'Fabricación de equipos de potencia hidráulica y neumática.'),(2813,'Fabricación de otras bombas, compresores, grifos y válvulas.'),(2814,'Fabricación de cojinetes, engranajes, trenes de engranajes y piezas de transmisión.'),(2815,'Fabricación de hornos, hogares y quemadores industriales.'),(2816,'Fabricación de equipo de elevación y manipulación.'),(2817,'Fabricación de maquinaria y equipo de oficina (excepto computadoras y equipo periférico).'),(2818,'Fabricación de herramientas manuales con motor.'),(2819,'Fabricación de otros tipos de maquinaria y equipo de uso general n.c.p.'),(2821,'Fabricación de maquinaria agropecuaria y forestal.'),(2822,'Fabricación de máquinas formadoras de metal y de máquinas herramienta.'),(2823,'Fabricación de maquinaria para la metalurgia.'),(2824,'Fabricación de maquinaria para explotación de minas y canteras y para obras de construcción.'),(2825,'Fabricación de maquinaria para la elaboración de alimentos, bebidas y tabaco.'),(2826,'Fabricación de maquinaria para la elaboración de productos textiles, prendas de vestir y cueros.'),(2829,'Fabricación de otros tipos de maquinaria y equipo de uso especial n.c.p.'),(2910,'Fabricación de vehículos automotores y sus motores.'),(2920,'Fabricación de carrocerías para vehículos automotores; fabricación de remolques y semirremolques.'),(2930,'Fabricación de partes, piezas (autopartes) y accesorios (lujos) para vehículos automotores.'),(3011,'Construcción de barcos y de estructuras flotantes.'),(3012,'Construcción de embarcaciones de recreo y deporte.'),(3020,'Fabricación de locomotoras y de material rodante para ferrocarriles.'),(3030,'Fabricación de aeronaves, naves espaciales y de maquinaria conexa.'),(3040,'Fabricación de vehículos militares de combate.'),(3091,'Fabricación de motocicletas.'),(3092,'Fabricación de bicicletas y de sillas de ruedas para personas con discapacidad.'),(3099,'Fabricación de otros tipos de equipo de transporte n.c.p.'),(3110,'Fabricación de muebles.'),(3120,'Fabricación de colchones y somieres.'),(3211,'Fabricación de joyas y artículos conexos'),(3212,'Fabricación de bisutería y artículos conexos'),(3220,'Fabricación de instrumentos musicales.'),(3230,'Fabricación de artículos y equipo para la práctica del deporte.'),(3240,'Fabricación de juegos, juguetes y rompecabezas.'),(3250,'Fabricación de instrumentos, aparatos y materiales médicos y odontológicos (incluido mobiliario).'),(3290,'Otras industrias manufactureras n.c.p.'),(3311,'Mantenimiento y reparación especializado de productos elaborados en metal.'),(3312,'Mantenimiento y reparación especializado de maquinaria y equipo.'),(3313,'Mantenimiento y reparación especializado de equipo electrónico y óptico.'),(3314,'Mantenimiento y reparación especializado de equipo eléctrico.'),(3315,'Mantenimiento y reparación especializado de equipo de transporte, excepto los vehículos automotores, motocicletas y bicicletas.'),(3319,'Mantenimiento y reparación de otros tipos de equipos y sus componentes n.c.p.'),(3320,'Instalación especializada de maquinaria y equipo industrial.'),(3511,'Generación de energía eléctrica.'),(3512,'Transmisión de energía eléctrica.'),(3513,'Distribución de energía eléctrica.'),(3514,'Comercialización de energía eléctrica'),(3520,'Producción de gas; distribución de combustibles gaseosos por tuberías.'),(3530,'Suministro de vapor y aire acondicionado.'),(3600,'Captación, tratamiento y distribución de agua.'),(3700,'Evacuación y tratamiento de aguas residuales.'),(3811,'Recolección de desechos no peligrosos.'),(3812,'Recolección de desechos peligrosos.'),(3821,'Tratamiento y disposición de desechos no peligrosos.'),(3822,'Tratamiento y disposición de desechos peligrosos.'),(3830,'Recuperación de materiales.'),(3900,'Actividades de saneamiento ambiental y otros servicios de gestión de desechos.'),(4111,'Construcción de edificios residenciales.'),(4112,'Construcción de edificios no residenciales.'),(4210,'Construcción de carreteras y vías de ferrocarril.'),(4220,'Construcción de proyectos de servicio público.'),(4290,'Construcción de otras obras de ingeniería civil.'),(4311,'Demolición.'),(4312,'Preparación del terreno.'),(4321,'Instalaciones eléctricas.'),(4322,'Instalaciones de fontanería, calefacción y aire acondicionado.'),(4329,'Otras instalaciones especializadas.'),(4330,'Terminación y acabado de edificios y obras de ingeniería civil.'),(4390,'Otras actividades especializadas para la construcción de edificios y obras de ingeniería civil.'),(4511,'Comercio de vehículos automotores nuevos.'),(4512,'Comercio de vehículos automotores usados.'),(4520,'Mantenimiento y reparación de vehículos automotores.'),(4530,'Comercio de partes, piezas (autopartes) y accesorios (lujos) para vehículos automotores.'),(4541,'Comercio de motocicletas y de sus partes, piezas y accesorios.'),(4542,'Mantenimiento y reparación de motocicletas y de sus partes y piezas.'),(4610,'Comercio al por mayor a cambio de una retribución o por contrata.'),(4620,'Comercio al por mayor de materias primas agropecuarias; animales vivos.'),(4631,'Comercio al por mayor de productos alimenticios.'),(4632,'Comercio al por mayor de bebidas y tabaco.'),(4641,'Comercio al por mayor de productos textiles, productos confeccionados para uso doméstico.'),(4642,'Comercio al por mayor de prendas de vestir.'),(4643,'Comercio al por mayor de calzado.'),(4644,'Comercio al por mayor de aparatos y equipo de uso doméstico.'),(4645,'Comercio al por mayor de productos farmacéuticos, medicinales, cosméticos y de tocador.'),(4649,'Comercio al por mayor de otros utensilios domésticos n.c.p.'),(4651,'Comercio al por mayor de computadores, equipo periférico y programas de informática.'),(4652,'Comercio al por mayor de equipo, partes y piezas electrónicos y de telecomunicaciones.'),(4653,'Comercio al por mayor de maquinaria y equipo agropecuarios.'),(4659,'Comercio al por mayor de otros tipos de maquinaria y equipo n.c.p.'),(4661,'Comercio al por mayor de combustibles sólidos, líquidos, gaseosos y productos conexos.'),(4662,'Comercio al por mayor de metales y productos metalíferos.'),(4663,'Comercio al por mayor de materiales de construcción, artículos de ferretería, pinturas, productos de vidrio, equipo y materiales de fontanería y calefacción.'),(4664,'Comercio al por mayor de productos químicos básicos, cauchos y plásticos en formas primarias y productos químicos de uso agropecuario.'),(4665,'Comercio al por mayor de desperdicios, desechos y chatarra.'),(4669,'Comercio al por mayor de otros productos n.c.p.'),(4690,'Comercio al por mayor no especializado.'),(4711,'Comercio al por menor en establecimientos no especializados con surtido compuesto principalmente por alimentos, bebidas o tabaco.'),(4719,'Comercio al por menor en establecimientos no especializados, con surtido compuesto principalmente por productos diferentes de alimentos (víveres en general), bebidas y tabaco.'),(4721,'Comercio al por menor de productos agrícolas para el consumo en establecimientos especializados.'),(4722,'Comercio al por menor de leche, productos lácteos y huevos, en establecimientos especializados.'),(4723,'Comercio al por menor de carnes (incluye aves de corral), productos cárnicos, pescados y productos de mar, en establecimientos especializados.'),(4724,'Comercio al por menor de bebidas y productos del tabaco, en establecimientos especializados.'),(4729,'Comercio al por menor de otros productos alimenticios n.c.p., en establecimientos especializados.'),(4731,'Comercio al por menor de combustible para automotores.'),(4732,'Comercio al por menor de lubricantes (aceites, grasas), aditivos y productos de limpieza para vehículos automotores.'),(4741,'Comercio al por menor de computadores, equipos periféricos, programas de informática y equipos de telecomunicaciones en establecimientos especializados.'),(4742,'Comercio al por menor de equipos y aparatos de sonido y de video, en establecimientos especializados.'),(4751,'Comercio al por menor de productos textiles en establecimientos especializados.'),(4752,'Comercio al por menor de artículos de ferretería, pinturas y productos de vidrio en establecimientos especializados.'),(4753,'Comercio al por menor de tapices, alfombras y cubrimientos para paredes y pisos en establecimientos especializados.'),(4754,'Comercio al por menor de electrodomésticos y gasodomésticos de uso doméstico, muebles y equipos de iluminación.'),(4755,'Comercio al por menor de artículos y utensilios de uso doméstico.'),(4759,'Comercio al por menor de otros artículos domésticos en establecimientos especializados.'),(4761,'Comercio al por menor de libros, periódicos, materiales y artículos de papelería y escritorio, en establecimientos especializados.'),(4762,'Comercio al por menor de artículos deportivos, en establecimientos especializados.'),(4769,'Comercio al por menor de otros artículos culturales y de entretenimiento n.c.p. en establecimientos especializados.'),(4771,'Comercio al por menor de prendas de vestir y sus accesorios (incluye artículos de piel) en establecimientos especializados.'),(4772,'Comercio al por menor de todo tipo de calzado y artículos de cuero y sucedáneos del cuero en establecimientos especializados.'),(4773,'Comercio al por menor de productos farmacéuticos y medicinales, cosméticos y artículos de tocador en establecimientos especializados.'),(4774,'Comercio al por menor de otros productos nuevos en establecimientos especializados.'),(4775,'Comercio al por menor de artículos de segunda mano.'),(4781,'Comercio al por menor de alimentos, bebidas y tabaco, en puestos de venta móviles.'),(4782,'Comercio al por menor de productos textiles, prendas de vestir y calzado, en puestos de venta móviles.'),(4789,'Comercio al por menor de otros productos en puestos de venta móviles.'),(4791,'Comercio al por menor realizado a través de Internet.'),(4792,'Comercio al por menor realizado a través de casas de venta o por correo.'),(4799,'Otros tipos de comercio al por menor no realizado en establecimientos, puestos de venta o mercados.'),(4911,'Transporte férreo de pasajeros.'),(4912,'Transporte férreo de carga.'),(4921,'Transporte de pasajeros.'),(4922,'Transporte mixto.'),(4923,'Transporte de carga por carretera.'),(4930,'Transporte por tuberías.'),(5011,'Transporte de pasajeros marítimo y de cabotaje.'),(5012,'Transporte de carga marítimo y de cabotaje.'),(5021,'Transporte fluvial de pasajeros.'),(5022,'Transporte fluvial de carga.'),(5111,'Transporte aéreo nacional de pasajeros.'),(5112,'Transporte aéreo internacional de pasajeros.'),(5121,'Transporte aéreo nacional de carga.'),(5122,'Transporte aéreo internacional de carga.'),(5210,'Almacenamiento y depósito'),(5221,'Actividades de estaciones, vías y servicios complementarios para el transporte terrestre.'),(5222,'Actividades de puertos y servicios complementarios para el transporte acuático.'),(5223,'Actividades de aeropuertos, servicios de navegación aérea y demás actividades conexas al transporte aéreo'),(5224,'Manipulación de carga'),(5229,'Otras actividades complementarias al transporte.'),(5310,'Actividades postales nacionales.'),(5320,'Actividades de mensajería.'),(5511,'Alojamiento en hoteles.'),(5512,'Alojamiento en apartahoteles.'),(5513,'Alojamiento en centros vacacionales'),(5514,'Alojamiento rural.'),(5519,'Otros tipos de alojamientos para visitantes.'),(5520,'Actividades de zonas de camping y parques para vehículos recreacionales.'),(5530,'Servicio por horas.'),(5590,'Otros tipos de alojamiento n.c.p.'),(5611,'Expendio a la mesa de comidas preparadas.'),(5612,'Expendio por autoservicio de comidas preparadas.'),(5613,'Expendio de comidas preparadas en cafeterías.'),(5619,'Otros tipos de expendio de comidas preparadas n.c.p.'),(5621,'Catering para eventos.'),(5629,'Actividades de otros servicios de comidas.'),(5630,'Expendio de bebidas alcohólicas para el consumo dentro del establecimiento.'),(5811,'Edición de libros.'),(5812,'Edición de directorios y listas de correo.'),(5813,'Edición de periódicos, revistas y otras publicaciones periódicas.'),(5819,'Otros trabajos de edición.'),(5820,'Edición de programas de informática (software).'),(5911,'Actividades de producción de películas cinematográficas, videos, programas, anuncios y comerciales de televisión.'),(5912,'Actividades de posproducción de películas cinematográficas, videos, programas, anuncios y comerciales de televisión.'),(5913,'Actividades de distribución de películas cinematográficas, videos, programas, anuncios y comerciales de televisión.'),(5914,'Actividades de exhibición de películas cinematográficas y videos.'),(5920,'Actividades de grabación de sonido y edición de música.'),(6010,'Actividades de programación y transmisión en el servicio de radiodifusión sonora.'),(6020,'Actividades de programación y transmisión de televisión.'),(6110,'Actividades de telecomunicaciones alámbricas.'),(6120,'Actividades de telecomunicaciones inalámbricas.'),(6130,'Actividades de telecomunicación satelital.'),(6190,'Otras actividades de telecomunicaciones.'),(6201,'Actividades de desarrollo de sistemas informáticos (planificación, análisis, diseño, programación, pruebas).'),(6202,'Actividades de consultoría informática y actividades de administración de instalaciones informáticas.'),(6209,'Otras actividades de tecnologías de información y actividades de servicios informáticos.'),(6311,'Procesamiento de datos, alojamiento (hosting) y actividades relacionadas.'),(6312,'Portales web.'),(6391,'Actividades de agencias de noticias.'),(6399,'Otras actividades de servicio de información n.c.p.'),(6411,'Banco Central.'),(6412,'Bancos comerciales.'),(6421,'Actividades de las corporaciones financieras.'),(6422,'Actividades de las compañías de financiamiento.'),(6423,'Banca de segundo piso.'),(6424,'Actividades de las cooperativas financieras.'),(6431,'Fideicomisos, fondos y entidades financieras similares.'),(6432,'Fondos de cesantías.'),(6491,'Leasing financiero (arrendamiento financiero).'),(6492,'Actividades financieras de fondos de empleados y otras formas asociativas del sector solidario.'),(6493,'Actividades de compra de cartera o factoring.'),(6494,'Otras actividades de distribución de fondos.'),(6495,'Instituciones especiales oficiales.'),(6496,'Capitalización.'),(6499,'Otras actividades de servicio financiero, excepto las de seguros y pensiones n.c.p.'),(6511,'Seguros generales.'),(6512,'Seguros de vida.'),(6513,'Reaseguros.'),(6515,'Seguros de salud.'),(6521,'Servicios de seguros sociales de salud.'),(6522,'Servicios de seguros sociales de riesgos profesionales.'),(6523,'Servicios de seguros sociales en riesgos familia.'),(6531,'Régimen de prima media con prestación definida (RPM).'),(6532,'Régimen de ahorro individual (RAI).'),(6611,'Administración de mercados financieros.'),(6612,'Corretaje de valores y de contratos de productos básicos.'),(6613,'Otras actividades relacionadas con el mercado de valores.'),(6614,'Actividades de las casas de cambio.'),(6615,'Actividades de los profesionales de compra y venta de divisas.'),(6619,'Otras actividades auxiliares de las actividades de servicios financieros n.c.p.'),(6621,'Actividades de agentes y corredores de seguros.'),(6629,'Evaluación de riesgos y daños, y otras actividades de servicios auxiliares.'),(6630,'Actividades de administración de fondos.'),(6810,'Actividades inmobiliarias realizadas con bienes propios o arrendados.'),(6820,'Actividades inmobiliarias realizadas a cambio de una retribución o por contrata.'),(6910,'Actividades jurídicas.'),(6920,'Actividades de contabilidad, teneduría de libros, auditoría financiera y asesoría tributaria.'),(7010,'Actividades de administración empresarial.'),(7020,'Actividades de consultoría de gestión.'),(7111,'Actividades de arquitectura.'),(7112,'Actividades de ingeniería y otras actividades conexas de consultoría técnica.'),(7120,'Ensayos y análisis técnicos.'),(7210,'Investigaciones y desarrollo experimental en el campo de las ciencias naturales y la ingeniería.'),(7220,'Investigaciones y desarrollo experimental en el campo de las ciencias sociales y las humanidades.'),(7310,'Publicidad.'),(7320,'Estudios de mercado y realización de encuestas de opinión pública.'),(7410,'Actividades especializadas de diseño.'),(7420,'Actividades de fotografía.'),(7490,'Otras actividades profesionales, científicas y técnicas n.c.p.'),(7500,'Actividades veterinarias.'),(7710,'Alquiler y arrendamiento de vehículos automotores.'),(7721,'Alquiler y arrendamiento de equipo recreativo y deportivo.'),(7722,'Alquiler de videos y discos.'),(7729,'Alquiler y arrendamiento de otros efectos personales y enseres domésticos n.c.p.'),(7730,'Alquiler y arrendamiento de otros tipos de maquinaria, equipo y bienes tangibles n.c.p.'),(7740,'Arrendamiento de propiedad intelectual y productos similares, excepto obras protegidas por derechos de autor.'),(7810,'Actividades de agencias de empleo.'),(7820,'Actividades de agencias de empleo temporal.'),(7830,'Otras actividades de suministro de recurso humano.'),(7911,'Actividades de las agencias de viaje.'),(7912,'Actividades de operadores turísticos.'),(7990,'Otros servicios de reserva y actividades relacionadas.'),(8010,'Actividades de seguridad privada.'),(8020,'Actividades de servicios de sistemas de seguridad.'),(8030,'Actividades de detectives e investigadores privados.'),(8110,'Actividades combinadas de apoyo a instalaciones.'),(8121,'Limpieza general interior de edificios.'),(8129,'Otras actividades de limpieza de edificios e instalaciones industriales.'),(8130,'Actividades de paisajismo y servicios de mantenimiento conexos.'),(8211,'Actividades combinadas de servicios administrativos de oficina.'),(8219,'Fotocopiado, preparación de documentos y otras actividades especializadas de apoyo a oficina.'),(8220,'Actividades de centros de llamadas (Call center).'),(8230,'Organización de convenciones y eventos comerciales.'),(8291,'Actividades de agencias de cobranza y oficinas de calificación crediticia.'),(8292,'Actividades de envase y empaque.'),(8299,'Otras actividades de servicio de apoyo a las empresas n.c.p.'),(8411,'Actividades legislativas de la administración pública.'),(8412,'Actividades ejecutivas de la administración pública.'),(8413,'Regulación de las actividades de organismos que prestan servicios de salud, educativos, culturales y otros servicios sociales, excepto servicios de seguridad social.'),(8414,'Actividades reguladoras y facilitadoras de la actividad económica.'),(8415,'Actividades de los otros órganos de control.'),(8421,'Relaciones exteriores.'),(8422,'Actividades de defensa.'),(8423,'Orden público y actividades de seguridad.'),(8424,'Administración de justicia.'),(8430,'Actividades de planes de seguridad social de afiliación obligatoria.'),(8511,'Educación de la primera infancia.'),(8512,'Educación preescolar.'),(8513,'Educación básica primaria.'),(8521,'Educación básica secundaria.'),(8522,'Educación media académica.'),(8523,'Educación media técnica y de formación laboral.'),(8530,'Establecimientos que combinan diferentes niveles de educación.'),(8541,'Educación técnica profesional.'),(8542,'Educación tecnológica.'),(8543,'Educación de instituciones universitarias o de escuelas tecnológicas.'),(8544,'Educación de universidades.'),(8551,'Formación académica no formal.'),(8552,'Enseñanza deportiva y recreativa.'),(8553,'Enseñanza cultural.'),(8559,'Otros tipos de educación n.c.p.'),(8560,'Actividades de apoyo a la educación.'),(8610,'Actividades de hospitales y clínicas, con internación.'),(8621,'Actividades de la práctica médica, sin internación.'),(8622,'Actividades de la práctica odontológica.'),(8691,'Actividades de apoyo diagnóstico.'),(8692,'Actividades de apoyo terapéutico.'),(8699,'Otras actividades de atención de la salud humana.'),(8710,'Actividades de atención residencial medicalizada de tipo general.'),(8720,'Actividades de atención residencial, para el cuidado de pacientes con retardo mental, enfermedad mental y consumo de sustancias psicoactivas.'),(8730,'Actividades de atención en instituciones para el cuidado de personas mayores y/o discapacitadas.'),(8790,'Otras actividades de atención en instituciones con alojamiento.'),(8810,'Actividades de asistencia social sin alojamiento para personas mayores y discapacitadas.'),(8891,'Actividades de guarderías para niños y niñas.'),(8899,'Otras actividades de asistencia social sin alojamiento n.c.p.'),(9001,'Creación literaria.'),(9002,'Creación musical.'),(9003,'Creación teatral.'),(9004,'Creación audiovisual.'),(9005,'Artes plásticas y visuales.'),(9006,'Actividades teatrales.'),(9007,'Actividades de espectáculos musicales en vivo.'),(9008,'Otras actividades de espectáculos en vivo.'),(9101,'Actividades de bibliotecas y archivos.'),(9102,'Actividades y funcionamiento de museos, conservación de edificios y sitios históricos.'),(9103,'Actividades de jardines botánicos, zoológicos y reservas naturales.'),(9200,'Actividades de juegos de azar y apuestas.'),(9311,'Gestión de instalaciones deportivas.'),(9312,'Actividades de clubes deportivos'),(9319,'Otras actividades deportivas.'),(9321,'Actividades de parques de atracciones y parques temáticos.'),(9329,'Otras actividades recreativas y de esparcimiento n.c.p.'),(9411,'Actividades de asociaciones empresariales y de empleadores.'),(9412,'Actividades de asociaciones profesionales.'),(9420,'Actividades de sindicatos de empleados.'),(9491,'Actividades de asociaciones religiosas.'),(9492,'Actividades de asociaciones políticas.'),(9499,'Actividades de otras asociaciones n.c.p.'),(9511,'Mantenimiento y reparación de computadores y de equipo periférico.'),(9512,'Mantenimiento y reparación de equipos de comunicación.'),(9521,'Mantenimiento y reparación de aparatos electrónicos de consumo.'),(9522,'Mantenimiento y reparación de aparatos y equipos domésticos y de jardinería.'),(9523,'Reparación de calzado y artículos de cuero.'),(9524,'Reparación de muebles y accesorios para el hogar.'),(9529,'Mantenimiento y reparación de otros efectos personales y enseres domésticos.'),(9601,'Lavado y limpieza, incluso la limpieza en seco, de productos textiles y de piel.'),(9602,'Peluquería y otros tratamientos de belleza.'),(9603,'Pompas fúnebres y actividades relacionadas.'),(9609,'Otras actividades de servicios personales n.c.p.'),(9700,'Actividades de los hogares individuales como empleadores de personal doméstico.'),(9810,'Actividades no diferenciadas de los hogares individuales como productores de bienes para uso propio.'),(9820,'Actividades no diferenciadas de los hogares individuales como productores de servicios para uso propio.'),(9900,'Actividades de organizaciones y entidades extraterritoriales.');
/*!40000 ALTER TABLE `economic_activities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `emails`
--

DROP TABLE IF EXISTS `emails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `emails` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `company_id` int DEFAULT NULL,
  `email_address` varchar(255) NOT NULL,
  `label_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `company_id` (`company_id`),
  KEY `label_id` (`label_id`),
  CONSTRAINT `correos_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `correos_ibfk_2` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`),
  CONSTRAINT `correos_ibfk_3` FOREIGN KEY (`label_id`) REFERENCES `labels` (`id`),
  CONSTRAINT `chk_cor_exclusivo` CHECK (((`user_id` is null) <> (`company_id` is null))),
  CONSTRAINT `chk_correo_exclusivo` CHECK ((((`user_id` is not null) and (`company_id` is null)) or ((`user_id` is null) and (`company_id` is not null)))),
  CONSTRAINT `chk_formato_correo` CHECK ((`email_address` like _utf8mb4'%@%.%'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `genders`
--

DROP TABLE IF EXISTS `genders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genders`
--

LOCK TABLES `genders` WRITE;
/*!40000 ALTER TABLE `genders` DISABLE KEYS */;
INSERT INTO `genders` VALUES (2,'Femenino'),(1,'Masculino'),(3,'Otro');
/*!40000 ALTER TABLE `genders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `labels`
--

DROP TABLE IF EXISTS `labels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `labels` (
  `id` int NOT NULL AUTO_INCREMENT,
  `label_name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_nombre` (`label_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `labels`
--

LOCK TABLES `labels` WRITE;
/*!40000 ALTER TABLE `labels` DISABLE KEYS */;
INSERT INTO `labels` VALUES (1,'Personal'),(2,'Trabajo'),(3,'Móvil'),(4,'Casa'),(5,'Principal'),(6,'Otro');
/*!40000 ALTER TABLE `labels` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `phones`
--

DROP TABLE IF EXISTS `phones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `phones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `company_id` int DEFAULT NULL,
  `country_id` int NOT NULL,
  `local_number` varchar(50) NOT NULL,
  `label_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `company_id` (`company_id`),
  KEY `country_id` (`country_id`),
  KEY `label_id` (`label_id`),
  CONSTRAINT `telefonos_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `telefonos_ibfk_2` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`),
  CONSTRAINT `telefonos_ibfk_3` FOREIGN KEY (`country_id`) REFERENCES `countries` (`id`),
  CONSTRAINT `telefonos_ibfk_4` FOREIGN KEY (`label_id`) REFERENCES `labels` (`id`),
  CONSTRAINT `chk_tel_exclusivo` CHECK (((`user_id` is null) <> (`company_id` is null))),
  CONSTRAINT `chk_telefono_exclusivo` CHECK ((((`user_id` is not null) and (`company_id` is null)) or ((`user_id` is null) and (`company_id` is not null))))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `positions`
--

DROP TABLE IF EXISTS `positions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `positions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `position_name` varchar(255) NOT NULL,
  `description` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_nombre_cargo` (`position_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `positions`
--

LOCK TABLES `positions` WRITE;
/*!40000 ALTER TABLE `positions` DISABLE KEYS */;
INSERT INTO `positions` VALUES (1,'Gerente',NULL),(2,'Subgerente',NULL),(3,'Director',NULL),(4,'Director comercial',NULL),(5,'Asistente comercial',NULL),(6,'Director de compras',NULL),(7,'Asistente de compras',NULL),(8,'Director de proyectos',NULL),(9,'Ing. de proyectos',NULL),(10,'Asistente de proyectos',NULL),(11,'Ing. Residente',NULL),(12,'Asistente contable',NULL),(13,'Jefe de mantenimiento',NULL),(14,'Asistente de logística',NULL),(15,'Persona natural','Cargo para usuarios que representan a personas naturales'),(16,'Otro','');
/*!40000 ALTER TABLE `positions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(255) NOT NULL,
  `description` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_nombre_rol` (`role_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Administrador','Control total sobre el sistema y los datos.'),(2,'Agente','Comercial'),(3,'Agente especial','Ing. de presupuestos'),(4,'Socio',NULL),(5,'Cliente','Activos'),(6,'Cliente potencial','Nuevos'),(7,'Revendedor',NULL),(8,'Proveedor',NULL),(9,'Otra',NULL);
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `states`
--

DROP TABLE IF EXISTS `states`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `states` (
  `id` int NOT NULL AUTO_INCREMENT,
  `state_name` varchar(255) DEFAULT NULL,
  `country_id` int DEFAULT NULL,
  `area_km2` int unsigned DEFAULT NULL,
  `population` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_departamento` (`state_name`),
  KEY `country_id` (`country_id`),
  CONSTRAINT `departamentos_ibfk_1` FOREIGN KEY (`country_id`) REFERENCES `countries` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `states`
--

LOCK TABLES `states` WRITE;
/*!40000 ALTER TABLE `states` DISABLE KEYS */;
INSERT INTO `states` VALUES (1,'Bogotá',1,1578,8034649),(2,'Amazonas',1,109665,76589),(3,'Antioquia',1,63612,6677930),(4,'Arauca',1,23818,262174),(5,'Atlántico',1,3388,2535517),(6,'Bolívar',1,25978,2070110),(7,'Boyacá',1,23189,1217376),(8,'Caldas',1,7888,998255),(9,'Caquetá',1,88965,401849),(10,'Casanare',1,44995,435195),(11,'Cauca',1,29308,1491937),(12,'Cesar',1,22905,1200574),(13,'Chocó',1,46530,534826),(14,'Córdoba',1,25020,1784783),(15,'Cundinamarca',1,22623,3242999),(16,'Guainía',1,72238,48114),(17,'Guaviare',1,53460,73081),(18,'Huila',1,19890,1200386),(19,'La Guajira',1,20848,965718),(20,'Magdalena',1,23188,1341746),(21,'Meta',1,85635,1039722),(22,'Nariño',1,33268,1630592),(23,'Norte de Santander',1,21658,1658835),(24,'Putumayo',1,24885,359127),(25,'Quindío',1,1845,555401),(26,'Risaralda',1,3600,988091),(27,'Archipiélago de San Andrés, Providencia y Santa Catalina',1,53,63692),(28,'Santander',1,30537,2184837),(29,'Sucre',1,10917,904863),(30,'Tolima',1,23562,1339998),(31,'Valle del Cauca',1,22140,4532152),(32,'Vaupés',1,54135,40797),(33,'Vichada',1,100242,112958);
/*!40000 ALTER TABLE `states` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `statuses`
--

DROP TABLE IF EXISTS `statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `statuses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `status_name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_nombre_estado` (`status_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `statuses`
--

LOCK TABLES `statuses` WRITE;
/*!40000 ALTER TABLE `statuses` DISABLE KEYS */;
INSERT INTO `statuses` VALUES (1,'Activo'),(5,'Archivado'),(6,'Eliminado'),(2,'Inactivo'),(4,'Intento de contacto'),(3,'Nuevo');
/*!40000 ALTER TABLE `statuses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tags` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `color` varchar(20) DEFAULT '#808080',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
/*!40000 ALTER TABLE `tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `company_tags`
--

DROP TABLE IF EXISTS `company_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `company_tags` (
  `id` int NOT NULL AUTO_INCREMENT,
  `company_id` int NOT NULL,
  `tag_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_company_tag` (`company_id`,`tag_id`),
  KEY `fk_ct_tag` (`tag_id`),
  CONSTRAINT `company_tags_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`) ON DELETE CASCADE,
  CONSTRAINT `company_tags_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_companies`
--

DROP TABLE IF EXISTS `user_companies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_companies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `company_id` int NOT NULL,
  `position_id` int DEFAULT NULL,
  `company_department_id` int DEFAULT NULL,
  `is_main_contact` tinyint(1) DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_usuario_empresa` (`user_id`,`company_id`),
  KEY `company_id` (`company_id`),
  KEY `position_id` (`position_id`),
  KEY `company_department_id` (`company_department_id`),
  KEY `idx_comp_rel` (`company_id`),
  KEY `idx_user_rel` (`user_id`),
  CONSTRAINT `usuarios_empresas_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `usuarios_empresas_ibfk_2` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`),
  CONSTRAINT `usuarios_empresas_ibfk_3` FOREIGN KEY (`position_id`) REFERENCES `positions` (`id`),
  CONSTRAINT `usuarios_empresas_ibfk_4` FOREIGN KEY (`company_department_id`) REFERENCES `company_departments` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
--
-- Table structure for table `user_relation_types`
--

DROP TABLE IF EXISTS `user_relation_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_relation_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `inverse_type_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_user_rel_inverse` (`inverse_type_id`),
  CONSTRAINT `fk_user_rel_inverse` FOREIGN KEY (`inverse_type_id`) REFERENCES `user_relation_types` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_relation_types`
--

LOCK TABLES `user_relation_types` WRITE;
/*!40000 ALTER TABLE `user_relation_types` DISABLE KEYS */;
-- 1: Jefe (Inv: 2) | 2: Empleado (Inv: 1) | 3: Familiar (Inv: 3) | 4: Mentor (Inv: 5) | 5: Aprendiz (Inv: 4)
INSERT INTO `user_relation_types` VALUES (1,'Jefe',2,'2026-01-04 16:51:26'),(2,'Empleado',1,'2026-01-04 16:51:26'),(3,'Familiar',3,'2026-01-04 16:51:26'),(4,'Profesor',5,'2026-01-04 16:51:26'),(5,'Aprendiz',4,'2026-01-04 16:51:26'),(6,'Amigo',6,'2026-01-04 16:51:26');
/*!40000 ALTER TABLE `user_relation_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_tags`
--

DROP TABLE IF EXISTS `user_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_tags` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `tag_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_tag` (`user_id`,`tag_id`),
  KEY `tag_id` (`tag_id`),
  CONSTRAINT `user_tags_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_tags_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_user_relations`
--

DROP TABLE IF EXISTS `user_user_relations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_user_relations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `from_user_id` int NOT NULL,
  `to_user_id` int NOT NULL,
  `relation_type_id` int NOT NULL,
  `custom_label` varchar(100) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_rel` (`from_user_id`,`to_user_id`,`relation_type_id`),
  KEY `to_user_id` (`to_user_id`),
  KEY `fk_user_rel_type` (`relation_type_id`),
  CONSTRAINT `fk_user_rel_type` FOREIGN KEY (`relation_type_id`) REFERENCES `user_relation_types` (`id`),
  CONSTRAINT `user_user_relations_ibfk_1` FOREIGN KEY (`from_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_user_relations_ibfk_2` FOREIGN KEY (`to_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `global_user_id` int DEFAULT NULL COMMENT 'Link to master_db.global_users.id',
  `agent_id` int DEFAULT NULL,
  `role_id` int DEFAULT NULL,
  `status_id` int NOT NULL,
  `prefix` varchar(50) DEFAULT NULL,
  `first_name` varchar(255) NOT NULL,
  `middle_name` varchar(255) DEFAULT NULL,
  `last_name` varchar(255) NOT NULL,
  `suffix` varchar(50) DEFAULT NULL,
  `phonetic_first_name` text,
  `phonetic_middle_name` text,
  `phonetic_last_name` text,
  `nickname` varchar(255) DEFAULT NULL,
  `file_as` varchar(255) DEFAULT NULL,
  `rut_nit` varchar(50) DEFAULT NULL,
  `birthday` date DEFAULT NULL,
  `gender_id` int DEFAULT NULL,
  `notes` text,
  `verification_digit` tinyint unsigned DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de creación automática',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Fecha de última modificación automática',
  `deleted_at` timestamp NULL DEFAULT NULL,
  `is_natural_person` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_nombre_apellido` (`first_name`,`last_name`),
  KEY `role_id` (`role_id`),
  KEY `status_id` (`status_id`),
  KEY `idx_last_name` (`last_name`),
  KEY `idx_tax_id` (`rut_nit`),
  KEY `idx_natural_person` (`is_natural_person`),
  KEY `fk_user_gender` (`gender_id`),
  KEY `idx_users_deleted_at` (`deleted_at`),
  KEY `idx_global_user` (`global_user_id`),
  CONSTRAINT `fk_user_gender` FOREIGN KEY (`gender_id`) REFERENCES `genders` (`id`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `usuarios_ibfk_2` FOREIGN KEY (`status_id`) REFERENCES `statuses` (`id`),
  CONSTRAINT `chk_dv_usuario` CHECK ((`verification_digit` between 0 and 9))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--

--
-- Dumping events for database 'crm'
--

--
-- Dumping routines for database 'crm'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-04 19:12:23

-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `actor_id` int DEFAULT NULL,
  `action_type` varchar(50) NOT NULL,
  `entity_type` varchar(50) NOT NULL,
  `entity_id` int DEFAULT NULL,
  `details` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_actor` (`actor_id`),
  KEY `idx_entity` (`entity_type`,`entity_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
