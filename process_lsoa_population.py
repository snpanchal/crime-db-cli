import csv
with open('./CrimeData/lsoa-population.csv','r') as csvinput:
    with open('./CrimeData/new-lsoa-population.csv', 'w') as csvoutput:
        writer = csv.writer(csvoutput, lineterminator='\n')
        reader = csv.reader(csvinput)

        allrows = [next(reader)]
        for row in reader:
            for i in range(len(row)):
                if row[i].strip() == '-':
                    row[i] = ""
            row[-1] = row[-1].replace(',', '')
            allrows.append(row)
        writer.writerows(allrows)
