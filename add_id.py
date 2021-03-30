import csv
count = 0

with open('./CrimeData/london-crime-by-lsoa.csv','r') as csvinput:
    with open('./CrimeData/new-london-crime-by-lsoa.csv', 'w') as csvoutput:
# with open('./CrimeData/london-stop-and-search.csv','r') as csvinput:
#     with open('./CrimeData/new-london-stop-and-search.csv', 'w') as csvoutput:
        writer = csv.writer(csvoutput, lineterminator='\n')
        reader = csv.reader(csvinput)

        allrows = []
        for row in reader:
            if count == 0:
                row.insert(0, "ID")
            else:    
                row.insert(0, count)
            count +=1
            allrows.append(row)

        writer.writerows(allrows)
