import csv
count = 0

with open('./CrimeData/london-crime-by-lsoa.csv','r') as csvinput:
    with open('./CrimeData/new-london-crime-by-lsoa.csv', 'w') as csvoutput:
        writer = csv.writer(csvoutput, lineterminator='\n')
        reader = csv.reader(csvinput)

        allrows = []
        for row in reader:
            if row[3].strip() == "Burglary in Other Buildings":
                row[2] = "Burglary"
            elif row[3].strip() == "Other violence":
                row[2] = "Violence and sexual offences"
            elif row[3].strip() == "Personal Property":
                row[2] = "Robbery"
            elif row[3].strip() == "Other Theft":
                row[2] = "Other theft"
            elif row[3].strip() == "Offensive Weapon":
                row[2] = "Possession of weapons"
            elif row[3].strip() == "Criminal Damage To Other Building":
                row[2] = "Criminal damage and arson"
            elif row[3].strip() == "Theft/Taking of Pedal Cycle":
                row[2] = "Bicycle theft"
            elif row[3].strip() == "Motor Vehicle Interference & Tampering":
                row[2] = "Vehicle crime"
            elif row[3].strip() == "Theft/Taking Of Motor Vehicle":
                row[2] = "Vehicle crime"
            elif row[3].strip() == "Wounding/GBH":
                row[2] = "Violence and sexual offences"
            elif row[3].strip() == "Other Theft Person":
                row[2] = "Theft from the person"
            elif row[3].strip() == "Common Assault":
                row[2] = "Violence and sexual offences"
            elif row[3].strip() == "Theft From Shops":
                row[2] = "Shoplifting"
            elif row[3].strip() == "Possession Of Drugs":
                row[2] = "Drugs"
            elif row[3].strip() == "Harassment":
                row[2] = "Violence and sexual offences"
            elif row[3].strip() == "Handling Stolen Goods":
                row[2] = "Other theft"
            elif row[3].strip() == "Criminal Damage To Dwelling":
                row[2] = "Criminal damage and arson"
            elif row[3].strip() == "Burglary in a Dwelling":
                row[2] = "Burglary"
            elif row[3].strip() == "Criminal Damage To Motor Vehicle":
                row[2] = "Criminal damage and arson"
            elif row[3].strip() == "Other Criminal Damage":
                row[2] = "Criminal damage and arson"
            elif row[3].strip() == "Counted per Victim":
                row[2] = "Other crime"
            elif row[3].strip() == "Going Equipped":
                row[2] = "Other crime"
            elif row[3].strip() == "Other Fraud & Forgery":
                row[2] = "Other crime"
            elif row[3].strip() == "Assault with Injury":
                row[2] = "Violence and sexual offences"
            elif row[3].strip() == "Drug Trafficking":
                row[2] = "Drugs"
            elif row[3].strip() == "Other Drugs":
                row[2] = "Drugs"
            elif row[3].strip() == "Business Property":
                row[2] = "Robbery"
            elif row[3].strip() == "Other Notifiable":
                row[2] = "Other crime"
            elif row[3].strip() == "Other Sexual":
                row[2] = "Violence and sexual offences"
            elif row[3].strip() == "Theft From Motor Vehicle":
                row[2] = "Other theft"
            elif row[3].strip() == "Rape":
                row[2] = "Violence and sexual offences"
            elif row[3].strip() == "Murder":
                row[2] = "Violence and sexual offences"

            if count == 0:
                row.insert(0, "ID")
            else:    
                row.insert(0, count)
            count +=1
            allrows.append(row)

        writer.writerows(allrows)
