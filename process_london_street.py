import csv
count = 0

with open('./CrimeData/london-street.csv','r') as csvinput:
    with open('./CrimeData/new-london-street.csv', 'w') as csvoutput:
        writer = csv.writer(csvoutput, lineterminator='\n')
        reader = csv.reader(csvinput)
        
        first_row = next(reader)
        first_row[0] = "ID"
        allrows = [first_row]
        for row in reader:
            if row[9].strip() == "Public order":
                row[9] = "Other crime"
            if row[0].strip() != '':
                row[0] = count
                count +=1
            allrows.append(row)

        writer.writerows(allrows)
