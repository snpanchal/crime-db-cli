-- Grouping # of crimes that occur in a particular Borough by the crime cateogory
SELECT COUNT(generalCrimeID) AS numberOfCrimes, lsoa, minorCategory, borough
FROM GeneralCrime
INNER JOIN LSOA 
USING (lsoa)
GROUP BY minorCategory, lsoa, borough;
