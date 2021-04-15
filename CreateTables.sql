\! rm -f tableOutfile.txt
tee table-outfile.txt;

-- Show warnings after every statement
warnings;

-- Drop existing tables
DROP TABLE IF EXISTS SearchProfile;
DROP TABLE IF EXISTS SimpleEthnicity;
DROP TABLE IF EXISTS DetailedEthnicity;
DROP TABLE IF EXISTS AgeRange;
DROP TABLE IF EXISTS Gender;

DROP TABLE IF EXISTS StopAndSearch;
DROP TABLE IF EXISTS SearchOutcome;
DROP TABLE IF EXISTS ObjectOfSearch;
DROP TABLE IF EXISTS SearchLegislation;
DROP TABLE IF EXISTS SearchType;

DROP TABLE IF EXISTS CrimeLocation;
DROP TABLE IF EXISTS ReportedCrime;
DROP TABLE IF EXISTS CrimeOutcome;
DROP TABLE IF EXISTS GeneralCrime;
DROP TABLE IF EXISTS CrimeCategory;

DROP TABLE IF EXISTS LSOA;
DROP TABLE IF EXISTS LondonBorough;

-- London Borough ---------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Create London Borough' AS '';

CREATE TABLE LondonBorough (
    borough VARCHAR(50),
    PRIMARY KEY(borough)
);

INSERT INTO LondonBorough
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
    FOREIGN KEY(borough) REFERENCES LondonBorough(borough),
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
WHERE borough IN (SELECT borough FROM LondonBorough)
    AND year=2014;


-- Load Crime Data --------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Load Crime Data' AS '';

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
    IGNORE 13000000 LINES -- To avoid long runtime in testing
    -- IGNORE 1 LINES
    (generalCrimeID, lsoa, @dummy, majorCategory, minorCategory, @dummy, year, month);


CREATE TEMPORARY TABLE tempReportedCrime (
    crimeReportID INT,
    year INT,
    month INT,
    longitude FLOAT,
    latitude FLOAT,
    description VARCHAR(255),
    lsoa CHAR(10),
    majorCategory VARCHAR(50),
    outcome VARCHAR(50)
);

LOAD DATA INFILE '/var/lib/mysql-files/CrimeData/new-london-street.csv' IGNORE
INTO TABLE tempReportedCrime
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 2850000 LINES -- To avoid long runtime in testing
    -- IGNORE 1 LINES
    (@crimeReportID, @monthyear, @dummy, @dummy, @longitude, @latitude, description,
     lsoa, @dummy, majorCategory, @outcome, @dummy)
    SET crimeReportID = IF(@crimeReportID LIKE '', NULL, @crimeReportID),
        year = YEAR(CAST(CONCAT(@monthyear, "-01") AS dateTime)),
        month = MONTH(CAST(CONCAT(@monthyear, "-01") AS dateTime)),
        outcome = IF(@outcome LIKE '', NULL, @outcome),
        longitude = IF(@longitude LIKE '', NULL, @longitude),
        latitude = IF(@latitude LIKE '', NULL, @latitude);


-- Crime Category ---------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Create Crime Category' AS '';

CREATE TABLE CrimeCategory (
    minorCategory VARCHAR(50),
    majorCategory VARCHAR(50),
    PRIMARY KEY(minorCategory)
);

INSERT INTO CrimeCategory
SELECT minorCategory, MAX(majorCategory) AS majorCategory
FROM tempCrimeToLsoa
GROUP BY minorCategory;
CREATE INDEX idxMajorCategory on CrimeCategory(majorCategory);


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


-- Crime Outcome ----------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Crime Outcome' AS '';

CREATE TABLE CrimeOutcome (
    outcome VARCHAR(50),
    PRIMARY KEY(outcome)
);

INSERT INTO CrimeOutcome
SELECT DISTINCT outcome FROM tempReportedCrime
WHERE outcome IS NOT NULL;


-- Reported Crime ---------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Create Reported Crime' AS '';

CREATE TABLE ReportedCrime (
    crimeReportID INT NOT NULL,
    majorCategory VARCHAR(50),
    outcome VARCHAR(50),
    year INT,
    month INT,
    PRIMARY KEY(crimeReportID),
    FOREIGN KEY (majorCategory) REFERENCES CrimeCategory(majorCategory),
    FOREIGN KEY (outcome) REFERENCES CrimeOutcome(outcome),
    CHECK(crimeReportID > 0),
    CHECK(year >= 2000 AND year < 3000),
    CHECK(month >= 1 AND month <= 12)
);

INSERT INTO ReportedCrime
SELECT crimeReportID, majorCategory, outcome, year, month
FROM tempReportedCrime
WHERE lsoa IN(SELECT lsoa FROM LSOA)
    AND crimeReportID!="";


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


-- Load Search Data -------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Load Search Data' AS '';

CREATE TEMPORARY TABLE tempStopAndSearch (
    searchID INT,
    type VARCHAR(50),
    date DATETIME,
    gender VARCHAR(10),
    ageRange VARCHAR(10),
    selfDefinedEthnicity VARCHAR(100),
    officerDefinedEthnicity VARCHAR(100),
    legislation VARCHAR(100),
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


-- Search Type ------------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Search Type' AS '';

CREATE TABLE SearchType (
    type VARCHAR(50),
    PRIMARY KEY(type)
);

INSERT INTO SearchType
SELECT DISTINCT type FROM tempStopAndSearch
WHERE type IS NOT NULL;


-- Search Legislation -----------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Search Legislation' AS '';

CREATE TABLE SearchLegislation (
    legislation VARCHAR(100),
    PRIMARY KEY(legislation)
);

INSERT INTO SearchLegislation
SELECT DISTINCT legislation FROM tempStopAndSearch
WHERE legislation IS NOT NULL;


-- Object Of Search -------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Object Of Search' AS '';

CREATE TABLE ObjectOfSearch (
    objectOfSearch VARCHAR(50),
    PRIMARY KEY(objectOfSearch)
);

INSERT INTO ObjectOfSearch
SELECT DISTINCT objectOfSearch FROM tempStopAndSearch
WHERE objectOfSearch IS NOT NULL;


-- Search Outcome ---------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Search Outcome' AS '';

CREATE TABLE SearchOutcome (
    outcome VARCHAR(50),
    PRIMARY KEY(outcome)
);

INSERT INTO SearchOutcome
SELECT DISTINCT outcome FROM tempStopAndSearch
WHERE outcome IS NOT NULL;


-- Stop and Search --------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Create Stop And Search' AS '';

CREATE TABLE StopAndSearch (
    searchID INT NOT NULL,
    type VARCHAR(50),
    date DATETIME,
    legislation VARCHAR(100),
    objectOfSearch VARCHAR(50),
    outcome VARCHAR(50),
    PRIMARY KEY(searchID),
    FOREIGN KEY(type) REFERENCES SearchType(type),
    FOREIGN KEY(legislation) REFERENCES SearchLegislation(legislation),
    FOREIGN KEY(objectOfSearch) REFERENCES ObjectOfSearch(objectOfSearch),
    FOREIGN KEY(outcome) REFERENCES SearchOutcome(outcome),
    CHECK(searchID > 0),
    CHECK(date >= '2000-01-01 00:00:00' AND date <= '3000-01-01 00:00:00')
);

INSERT INTO StopAndSearch
SELECT searchID, type, date, legislation, objectOfSearch, outcome FROM tempStopAndSearch;


-- Gender -----------------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Gender' AS '';

CREATE TABLE Gender (
    gender VARCHAR(10),
    PRIMARY KEY(gender)
);

INSERT INTO Gender
SELECT DISTINCT gender FROM tempStopAndSearch
WHERE gender IS NOT NULL;


-- Age Range --------------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'AgeRange' AS '';

CREATE TABLE AgeRange (
    ageRange VARCHAR(10),
    PRIMARY KEY(ageRange)
);

INSERT INTO AgeRange
SELECT DISTINCT ageRange FROM tempStopAndSearch
WHERE ageRange IS NOT NULL;


-- Detailed Ethnicity -----------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Detailed Ethnicity' AS '';

CREATE TABLE DetailedEthnicity (
    ethnicity VARCHAR(100),
    PRIMARY KEY(ethnicity)
);

INSERT INTO DetailedEthnicity
SELECT DISTINCT selfDefinedEthnicity AS ethnicity FROM tempStopAndSearch
WHERE selfDefinedEthnicity IS NOT NULL;


-- Simple Ethnicity -------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Simple Ethnicity' AS '';

CREATE TABLE SimpleEthnicity (
    ethnicity VARCHAR(10),
    PRIMARY KEY(ethnicity)
);

INSERT INTO SimpleEthnicity
SELECT DISTINCT officerDefinedEthnicity AS ethnicity FROM tempStopAndSearch
WHERE officerDefinedEthnicity IS NOT NULL;


-- Search Profile----------------------------------------------------------------------
SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Create Search Profile' AS '';

CREATE TABLE SearchProfile (
    searchID INT NOT NULL,
    gender VARCHAR(10),
    ageRange VARCHAR(10),
    selfDefinedEthnicity VARCHAR(100),
    officerDefinedEthnicity VARCHAR(10),
    PRIMARY KEY(searchID),
    FOREIGN KEY (searchID) REFERENCES StopAndSearch(searchID),
    FOREIGN KEY (gender) REFERENCES Gender(gender),
    FOREIGN KEY (ageRange) REFERENCES AgeRange(ageRange),
    FOREIGN KEY (selfDefinedEthnicity) REFERENCES DetailedEthnicity(ethnicity),
    FOREIGN KEY (officerDefinedEthnicity) REFERENCES SimpleEthnicity(ethnicity)
);

INSERT INTO SearchProfile
SELECT searchID, gender, ageRange, selfDefinedEthnicity, officerDefinedEthnicity
FROM tempStopAndSearch
WHERE gender IS NOT NULL
    OR ageRange IS NOT NULL
    OR selfDefinedEthnicity IS NOT NULL
    OR officerDefinedEthnicity IS NOT NULL;

notee;