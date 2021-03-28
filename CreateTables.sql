\! rm -f project-outfile.txt
tee project-outfile.txt;

-- Show warnings after every statement
warnings;

-- Drop existing tables
DROP TABLE IF EXISTS SearchProfile;
DROP TABLE IF EXISTS StopAndSearch;

DROP TABLE IF EXISTS CrimeLocation;
DROP TABLE IF EXISTS LSOA;
DROP TABLE IF EXISTS ReportedCrime;

DROP TABLE IF EXISTS Borough;
DROP TABLE IF EXISTS Year;

-- -- Borough ---------------------------------------------------------------------
-- SELECT '----------------------------------------------------------------' as '';
-- SELECT 'Create Borough Crime' AS '';


-- Reported Crime --------------------------------------------------------------
SELECT '----------------------------------------------------------------' as '';
SELECT 'Create Reported Crime' AS '';

CREATE TABLE ReportedCrime (
    crimeID CHAR(64),
    jurisdiction VARCHAR(50),
    type VARCHAR(50),
    outcome VARCHAR(50),
    year INT,
    month INT,
    PRIMARY KEY(crimeID)
);

LOAD DATA INFILE '/var/lib/mysql-files/CrimeData/london-street.csv' IGNORE INTO TABLE ReportedCrime
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 2850000 LINES
    (crimeID, @monthyear, @dummy, jurisdiction, @dummy, @dummy, @dummy, @dummy, @dummy, type, outcome, @dummy)
    SET year = YEAR(CAST(CONCAT(@monthyear, "-01") AS dateTime)),
        month = MONTH(CAST(CONCAT(@monthyear, "-01") AS dateTime));

DELETE FROM ReportedCrime WHERE crimeID="";

-- Crime Location --------------------------------------------------------------
SELECT '----------------------------------------------------------------' as '';
SELECT 'Create Crime Location' AS '';
CREATE TABLE CrimeLocation (
    crimeID CHAR(64),
    longitude FLOAT,
    latitude FLOAT,
    description VARCHAR(255),
    lsoa CHAR(10),
    PRIMARY KEY(crimeID),
    FOREIGN KEY(crimeID) REFERENCES ReportedCrime(crimeID)
);

LOAD DATA INFILE '/var/lib/mysql-files/CrimeData/london-street.csv' IGNORE INTO TABLE CrimeLocation
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 2850000 LINES
    (crimeID, @dummy, @dummy, @dummy, longitude, latitude, description, lsoa, @dummy, @dummy, @dummy, @dummy);

DELETE FROM CrimeLocation WHERE description="No location" OR crimeID="";

-- LSOA ------------------------------------------------------------------------
SELECT '----------------------------------------------------------------' as '';
SELECT 'Create LSOA' AS '';
CREATE TABLE LSOA (
    lsoa CHAR(10),
    lsoaName VARCHAR(50),
    borough VARCHAR(50),
    PRIMARY KEY(lsoa)
);

LOAD DATA INFILE '/var/lib/mysql-files/CrimeData/lsoa.csv' IGNORE INTO TABLE LSOA
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 LINES
    (@dummy, @dummy, borough, lsoa, lsoaName, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy);


DELETE FROM LSOA
WHERE borough NOT IN (
    "City of London",
    "Barking and Dagenham",
    "Barnet",
    "Bexley",
    "Brent",
    "Bromley",
    "Camden",
    "Croydon",
    "Ealing",
    "Enfield",
    "Greenwich",
    "Hackney",
    "Hammersmith and Fulham",
    "Haringey",
    "Harrow",
    "Havering",
    "Hillingdon",
    "Hounslow",
    "Islington",
    "Kensington and Chelsea",
    "Kingston upon Thames",
    "Lambeth",
    "Lewisham",
    "Merton",
    "Newham",
    "Redbridge",
    "Richmond upon Thames",
    "Southwark",
    "Sutton",
    "Tower Hamlets",
    "Waltham Forest",
    "Wandsworth",
    "Westminster"
);

-- Stop and Search -------------------------------------------------------------
SELECT '----------------------------------------------------------------' as '';
SELECT 'Create Stop And Search' AS '';
CREATE TABLE StopAndSearch (
    searchID INT,
    type VARCHAR(50),
    date DATETIME,
    legislation VARCHAR(255),
    objectOfSearch VARCHAR(50),
    outcome VARCHAR(50),
    PRIMARY KEY(searchID)
);

LOAD DATA INFILE '/var/lib/mysql-files/CrimeData/london-stop-and-search.csv' IGNORE INTO TABLE StopAndSearch
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 LINES
    (searchID, type, date, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, legislation, @objectOfSearch, outcome, @dummy, @dummy)
    SET objectOfSearch = IF(@objectOfSearch LIKE '', NULL, @objectOfSearch);

-- Search Profile---------------------------------------------------------------
SELECT '----------------------------------------------------------------' as '';
SELECT 'Create Search Profile' AS '';
CREATE TABLE SearchProfile (
    searchID INT,
    gender VARCHAR(10),
    ageRange VARCHAR(10),
    selfDefinedEthnicity VARCHAR(50),
    officerDefinedEthnicity VARCHAR(50),
    PRIMARY KEY(searchID),
    FOREIGN KEY (searchID) REFERENCES StopAndSearch(searchID)
);

LOAD DATA INFILE '/var/lib/mysql-files/CrimeData/london-stop-and-search.csv' IGNORE INTO TABLE SearchProfile
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\n'
    IGNORE 1 LINES
    (searchID, @dummy, @dummy, @dummy, @dummy, @dummy, @dummy, @gender, @ageRange, @selfDefinedEthnicity, @officerDefinedEthnicity, @dummy, @dummy, @dummy, @dummy, @dummy)
    SET gender = IF(@gender LIKE '', NULL, @gender),
        ageRange = IF(@ageRange LIKE '', NULL, @ageRange),
        selfDefinedEthnicity = IF(@selfDefinedEthnicity LIKE '', NULL, @selfDefinedEthnicity),
        officerDefinedEthnicity = IF(@officerDefinedEthnicity LIKE '', NULL, @officerDefinedEthnicity);

DELETE FROM SearchProfile WHERE gender IS NULL AND ageRange IS NULL AND selfDefinedEthnicity IS NULL AND officerDefinedEthnicity IS NULL;