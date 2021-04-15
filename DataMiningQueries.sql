---Grouping # of crimes that occur in a particular Borough by the crime cateogory
SELECT COUNT(SELECT COUNT(generalCrimeID) as numberOfCrimes, GeneralCrime.lsoa, GeneralCrime.minorCategory, LSOA.Borough
FROM GeneralCrime
INNER JOIN LSOA 
USING (lsoa)
GROUP BY GeneralCrime.minorCategory;
