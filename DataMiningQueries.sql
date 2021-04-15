tee outfile.txt;

SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Crime Datamining Queries' AS '';

-- Crime per capita for each minor category
SELECT minorCategory, COUNT(generalCrimeID)*100000/(SELECT SUM(population) FROM LSOA) AS crimesPerCapita
FROM GeneralCrime 
GROUP BY minorCategory
ORDER BY crimesPerCapita DESC;

-- Crime per capita for each year
SELECT year, COUNT(generalCrimeID)*100000/(SELECT SUM(population) FROM LSOA) AS crimesPerCapita
FROM GeneralCrime
WHERE year > 2007 AND year < 2017
GROUP BY year
ORDER BY year;

-- Crime per capita for each borough
SELECT borough, numCrimes*100000/pop AS crimesPerCapita
FROM (
    SELECT COUNT(generalCrimeID) AS numCrimes, borough
    FROM LSOA
    INNER JOIN GeneralCrime USING (lsoa)
    GROUP BY borough
) AS t1
INNER JOIN (
    SELECT borough, SUM(population) AS pop
    FROM LSOA
    GROUP BY borough
) AS t2 USING(borough)
ORDER BY crimesPerCapita DESC;

-- Specific Data to identify trends
SELECT borough, year, minorCategory, numCrimes*100000/pop AS crimesPerCapita
FROM (
    SELECT COUNT(generalCrimeID) AS numCrimes, minorCategory, borough, year
    FROM LSOA
    INNER JOIN GeneralCrime USING (lsoa)
    GROUP BY borough, year, minorCategory
    ORDER BY borough, year, minorCategory
) AS t1
INNER JOIN (
    SELECT borough, SUM(population) AS pop
    FROM LSOA
    GROUP BY borough
) AS t2 USING(borough);


SELECT '-----------------------------------------------------------------------' as '';
SELECT 'Stop And Search Datamining Queries' AS '';

SELECT gender, COUNT(*)/(SELECT COUNT(*) FROM SearchProfile) AS searchRatio
FROM SearchProfile
GROUP BY gender;

SELECT officerDefinedEthnicity, COUNT(*)/(SELECT COUNT(*) FROM SearchProfile) AS searchRatio
FROM SearchProfile
GROUP BY officerDefinedEthnicity;

SELECT selfDefinedEthnicity, COUNT(*)/(SELECT COUNT(*) FROM SearchProfile) AS searchRatio
FROM SearchProfile
GROUP BY selfDefinedEthnicity;

SELECT ageRange, COUNT(*)/(SELECT COUNT(*) FROM SearchProfile) AS searchRatio
FROM SearchProfile
GROUP BY ageRange;

notee;
