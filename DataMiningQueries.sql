-- Grouping # of crimes that occur in a particular Borough by the crime cateogory
SELECT COUNT(generalCrimeID) AS numberOfCrimes, lsoa, minorCategory, borough
FROM GeneralCrime
INNER JOIN LSOA 
USING (lsoa)
GROUP BY minorCategory, lsoa, borough;
SELECT COUNT(generalCrimeID) AS numberOfCrimes, minorCategory 
FROM ReportedCrime 
WHERE minorCategory = "Other Theft"
ORDER BY numberOfCrimes DESC;
-- Borough 
SELECT SUM(population) FROM LSOA WHERE borough = "Barnet";
--actual qeury
SELECT COUNT(generalCrimeID)*100000/{borough_population} AS crimesPerCapita, GeneralCrime.minorCategory,lsoa, borough 
FROM GeneralCrime 
INNER JOIN LSOA 
USING (lsoa) 
WHERE borough = "Barnet" 
GROUP BY minorCategory,lsoa, borough 
ORDER BY crimesPerCapita DESC;