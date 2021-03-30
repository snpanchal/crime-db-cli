\! rm -f project-outfile.txt
tee project-outfile.txt;

-- Show warnings after every statement
warnings;

-- Drop existing tables
DROP TABLE IF EXISTS SearchProfile;
DROP TABLE IF EXISTS StopAndSearch;

DROP TABLE IF EXISTS GeneralCrime;
DROP TABLE IF EXISTS CrimeCategory;

DROP TABLE IF EXISTS CrimeLocation;
DROP TABLE IF EXISTS ReportedCrime;

DROP TABLE IF EXISTS LSOA;
DROP TABLE IF EXISTS Borough;

-- Borough -------------------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
CREATE TABLE Borough (
    borough VARCHAR(50),
    PRIMARY KEY(borough)
);

INSERT INTO Borough
VALUES  ("City of London"),
        ("Barking and Dagenham"),
        ("Barnet"),
        ("Bexley"),
        ("Brent"),
        ("Bromley"),
        ("Camden"),
        ("Croydon"),
        ("Ealing"),
        ("Enfield"),
        ("Greenwich"),
        ("Hackney"),
        ("Hammersmith and Fulham"),
        ("Haringey"),
        ("Harrow"),
        ("Havering"),
        ("Hillingdon"),
        ("Hounslow"),
        ("Islington"),
        ("Kensington and Chelsea"),
        ("Kingston upon Thames"),
        ("Lambeth"),
        ("Lewisham"),
        ("Merton"),
        ("Newham"),
        ("Redbridge"),
        ("Richmond upon Thames"),
        ("Southwark"),
        ("Sutton"),
        ("Tower Hamlets"),
        ("Waltham Forest"),
        ("Wandsworth"),
        ("Westminster");


-- LSOA -------------------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Create LSOA' AS '';

CREATE TABLE LSOA (
    lsoa CHAR(10),
    lsoaName VARCHAR(50),
    borough VARCHAR(50),
    malePopulation INT,
    femalePopulation INT,
    population INT,
    PRIMARY KEY(lsoa),
    FOREIGN KEY(borough) REFERENCES Borough(borough),
    CHECK(lsoa LIKE 'E01%'),
    CHECK(lsoaName LIKE CONCAT(borough,'%')),
    CHECK(malePopulation >= 0),
    CHECK(femalePopulation >= 0),
    CHECK(population >= 0)
);

CREATE TEMPORARY TABLE tempLSOA (
    lsoa CHAR(10),
    year INT,
    lsoaName VARCHAR(50),
    borough VARCHAR(50),
    malePopulation INT,
    femalePopulation INT,
    population INT
);

LOAD DATA INFILE '/var/lib/mysql-files/CrimeData/new-lsoa-population.csv' IGNORE
INTO TABLE tempLSOA
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 LINES
    (lsoa, year, lsoaName, borough, @malePopulation, @femalePopulation, @population)
    SET malePopulation = IF(
            @malePopulation LIKE '', NULL, @malePopulation
        ),
        femalePopulation = IF(
            @femalePopulation LIKE '', NULL, @femalePopulation
        ),
        population = IF(
            @population LIKE '', NULL, @population
        );

INSERT INTO LSOA
SELECT lsoa, lsoaName, borough, malePopulation, femalePopulation, population
FROM tempLSOA
WHERE borough IN (SELECT borough FROM Borough)
    AND year=2014;


-- Reported Crime ---------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Create Reported Crime' AS '';

CREATE TABLE ReportedCrime (
    crimeReportID INT NOT NULL,
    jurisdiction VARCHAR(50),
    type VARCHAR(50),
    outcome VARCHAR(50),
    year INT,
    month INT,
    PRIMARY KEY(crimeReportID),
    CHECK(crimeReportID > 0),
    CHECK(year >= 2000 AND year < 3000),
    CHECK(month >= 1 AND month <= 12)
);

CREATE TEMPORARY TABLE tempReportedCrime (
    crimeReportID INT,
    year INT,
    month INT,
    jurisdiction VARCHAR(50),
    longitude FLOAT,
    latitude FLOAT,
    description VARCHAR(255),
    lsoa CHAR(10),
    type VARCHAR(50),
    outcome VARCHAR(50)
);

LOAD DATA INFILE '/var/lib/mysql-files/CrimeData/new-london-street.csv' IGNORE
INTO TABLE tempReportedCrime
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 LINES
    (@crimeReportID, @monthyear, @dummy, jurisdiction, @longitude, @latitude, description,
     lsoa, @dummy, type, outcome, @dummy)
    SET crimeReportID = IF(@crimeReportID LIKE '', NULL, @crimeReportID),
        year = YEAR(CAST(CONCAT(@monthyear, "-01") AS dateTime)),
        month = MONTH(CAST(CONCAT(@monthyear, "-01") AS dateTime)),
        longitude = IF(@longitude LIKE '', NULL, @longitude),
        latitude = IF(@latitude LIKE '', NULL, @latitude);

INSERT INTO ReportedCrime
SELECT crimeReportID, jurisdiction, type, outcome, year, month
FROM tempReportedCrime
WHERE crimeReportID!="";


-- Crime Location ---------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Create Crime Location' AS '';

CREATE TABLE CrimeLocation (
    crimeReportID INT NOT NULL,
    longitude FLOAT,
    latitude FLOAT,
    description VARCHAR(255),
    lsoa CHAR(10),
    PRIMARY KEY(crimeReportID),
    FOREIGN KEY(crimeReportID) REFERENCES ReportedCrime(crimeReportID),
    FOREIGN KEY(lsoa) REFERENCES LSOA(lsoa),
    CHECK(longitude >= -180.0 AND longitude <= 180.0),
    CHECK(latitude >= -90.0 AND latitude <= 90.0)
);

INSERT INTO CrimeLocation
SELECT crimeReportID, longitude, latitude, description, lsoa
FROM tempReportedCrime
WHERE description!="No location"
    AND lsoa IN(SELECT lsoa FROM LSOA)
    AND crimeReportID!="";


-- Crime Category ---------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Create Crime Category' AS '';

CREATE TABLE CrimeCategory (
    minorCategory VARCHAR(50),
    majorCategory VARCHAR(50),
    PRIMARY KEY(minorCategory)
);

CREATE TEMPORARY TABLE tempCrimeToLsoa (
    generalCrimeID INT,
    lsoa CHAR(10),
    majorCategory VARCHAR(50),
    minorCategory VARCHAR(50),
    year INT,
    month INT
);

LOAD DATA INFILE '/var/lib/mysql-files/CrimeData/new-london-crime-by-lsoa.csv' IGNORE
INTO TABLE tempCrimeToLsoa
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 LINES
    (generalCrimeID, lsoa, @dummy, majorCategory, minorCategory, @dummy, year, month);

INSERT INTO CrimeCategory
SELECT minorCategory, MAX(majorCategory) AS majorCategory
FROM tempCrimeToLsoa
GROUP BY minorCategory;

-- General Crime ----------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Create General Crime' AS '';

CREATE TABLE GeneralCrime (
    generalCrimeID INT NOT NULL,
    lsoa CHAR(10),
    minorCategory VARCHAR(50),
    year INT,
    month INT,
    PRIMARY KEY(generalCrimeID),
    FOREIGN KEY(lsoa) REFERENCES LSOA(lsoa),
    FOREIGN KEY(minorCategory) REFERENCES CrimeCategory(minorCategory),
    CHECK(generalCrimeID > 0),
    CHECK(year >= 2000 AND year < 3000),
    CHECK(month >= 1 AND month <= 12)
);

INSERT INTO GeneralCrime
SELECT generalCrimeID, lsoa, minorCategory, year, month
FROM tempCrimeToLsoa
WHERE lsoa IN (SELECT lsoa FROM LSOA);


-- Stop and Search --------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Create Stop And Search' AS '';

CREATE TABLE StopAndSearch (
    searchID INT NOT NULL,
    type VARCHAR(50),
    date DATETIME,
    legislation VARCHAR(255),
    objectOfSearch VARCHAR(50),
    outcome VARCHAR(50),
    PRIMARY KEY(searchID),
    CHECK(searchID > 0),
    CHECK(date >= '2000-01-01 00:00:00' AND date <= '3000-01-01 00:00:00')
);

CREATE TEMPORARY TABLE tempStopAndSearch (
    searchID INT,
    type VARCHAR(50),
    date DATETIME,
    gender VARCHAR(10),
    ageRange VARCHAR(10),
    selfDefinedEthnicity VARCHAR(100),
    officerDefinedEthnicity VARCHAR(100),
    legislation VARCHAR(255),
    objectOfSearch VARCHAR(50),
    outcome VARCHAR(50)
);

LOAD DATA INFILE '/var/lib/mysql-files/CrimeData/new-london-stop-and-search.csv' IGNORE
INTO TABLE tempStopAndSearch
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 LINES
    (searchID, type, date, @dummy, @dummy, @dummy, @dummy, @gender, @ageRange,
     @selfDefinedEthnicity, @officerDefinedEthnicity, legislation, @objectOfSearch,
     outcome, @dummy, @dummy)
    SET objectOfSearch = IF(@objectOfSearch LIKE '', NULL, @objectOfSearch),
        gender = IF(@gender LIKE '', NULL, @gender),
        ageRange = IF(@ageRange LIKE '', NULL, @ageRange),
        selfDefinedEthnicity = IF(
            @selfDefinedEthnicity LIKE '', NULL, @selfDefinedEthnicity
        ),
        officerDefinedEthnicity = IF(
            @officerDefinedEthnicity LIKE '', NULL, @officerDefinedEthnicity
        );

INSERT INTO StopAndSearch
SELECT searchID, type, date, legislation, objectOfSearch, outcome FROM tempStopAndSearch;

-- Search Profile----------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Create Search Profile' AS '';

CREATE TABLE SearchProfile (
    searchID INT NOT NULL,
    gender VARCHAR(10),
    ageRange VARCHAR(10),
    selfDefinedEthnicity VARCHAR(100),
    officerDefinedEthnicity VARCHAR(100),
    PRIMARY KEY(searchID),
    FOREIGN KEY (searchID) REFERENCES StopAndSearch(searchID)
);

INSERT INTO SearchProfile
SELECT searchID, gender, ageRange, selfDefinedEthnicity, officerDefinedEthnicity
FROM tempStopAndSearch
WHERE gender IS NOT NULL
    OR ageRange IS NOT NULL
    OR selfDefinedEthnicity IS NOT NULL
    OR officerDefinedEthnicity IS NOT NULL;

notee;