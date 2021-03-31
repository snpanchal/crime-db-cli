import mysql.connector

crime_db = mysql.connector.connect(
    host="localhost",
    user="yourusername",
    password="yourpassword"
)
cursor = crime_db.cursor()

role = ''
roleMap = {
    'p': 'Police',
    'a': 'Analyst',
    'c': 'Citizen',
}
crime_minor_categories = ['Burglary in Other Buildings', 'Other violence', 'Personal Property', 'Other Theft', 'Offensive Weapon', 'Criminal Damage To Other Building', 'Theft/Taking of Pedal Cycle', 'Motor Vehicle Interference & Tampering', 'Theft/Taking Of Motor Vehicle', 'Wounding/GBH', 'Other Theft Person', 'Common Assault', 'Theft From Shops', 'Possession Of Drugs', 'Harassment', 'Handling Stolen Goods', 'Criminal Damage To Dwelling', 'Burglary in a Dwelling', 'Criminal Damage To Motor Vehicle', 'Other Criminal Damage', 'Counted per Victim', 'Going Equipped', 'Other Fraud & Forgery', 'Assault with Injury', 'Drug Trafficking', 'Other Drugs', 'Business Property', 'Other Notifiable', 'Other Sexual', 'Theft From Motor Vehicle', 'Rape', 'Murder']
crime_major_categories = ['Burglary', 'Violence Against the Person', 'Robbery', 'Theft and Handling', 'Criminal Damage', 'Drugs', 'Fraud or Forgery', 'Other Notifiable Offences', 'Sexual Offences']

def get_input(prompt, valid_values=None):
    user_input = str(input(prompt + ' ')).lower()
    if not valid_values:
        return user_input
    
    while user_input not in valid_values and user_input != 'na':
        user_input = str(input('Please enter a valid value: ')).lower()
    
    return user_input if user_input != 'na' else ''

def create_where_clause(inputs):
    where_clause = 'WHERE'
    first = True
    for key in inputs.keys():
        if inputs[key]:
            if not first:
                where_clause += ' AND'
            where_clause += ' {} = {}'.format(key, inputs[key])
            first = False

    return where_clause if where_clause != 'WHERE' else ''

def get_area_crime_stats_police():
    choice = get_input('What would you like to search crime stats by? (Borough = B, LSOA = L)', {'b', 'l'})
    if choice == 'l':
        lsoa = get_input('What LSOA would you like to get crime stats for?')
        if lsoa:
            # QUERY crimes activity for LSOA
            cursor.execute('SELECT year, majorCategory, COUNT(crimeReportID)*100000/population AS crimesPerCapita FROM CrimeLocation INNER JOIN ReportedCrime USING (crimeReportID) GROUP BY lsoa, year, majorCategory WHERE lsoa = {};'.format(lsoa))
            result = cursor.fetchall()
            for r in result:
                print(r)
    else:
        borough = get_input('What borough would you like to get crime stats for?')
        if borough:
            cursor.execute('SELECT SUM(population) FROM LSOA WHERE borough = {};'.format(borough))
            boroughPopulation = cursor.fetchone()[0]

            # QUERY crimes activity for borough
            cursor.execute('SELECT year, majorCategory, COUNT(crimeReportID)*100000/{} AS crimesPerCapita FROM CrimeLocation INNER JOIN ReportedCrime USING (crimeReportID) INNER JOIN LSOA USING (lsoa) GROUP BY borough, year, majorCategory WHERE borough = {};'.format(boroughPopulation, borough))
            result = cursor.fetchall()
            for r in result:
                print(r)

def get_area_crime_stats_analyst():
    cursor.execute('SELECT borough, year, majorCategory, COUNT(generalCrimeID)*100000/population AS crimesPerCapita FROM LSOA INNER JOIN GeneralCrime USING (lsoa) INNER JOIN CrimeCategory USING (minorCategory) GROUP BY borough, year, majorCategory;')
    result = cursor.fetchall()
    for r in result:
        print(r)

def get_area_crime_stats_citizen():
    lsoa = get_input('What LSOA would you like to get crime stats for?')
    if lsoa:
        # QUERY crimes activity for LSOA
        cursor.execute('SELECT year, majorCategory, COUNT(generalCrimeID)*100000/population AS crimesPerCapita FROM LSOA INNER JOIN GeneralCrime USING (lsoa) GROUP BY lsoa, year, majorCategory WHERE lsoa = {};'.format(lsoa))
        result = cursor.fetchall()
        for r in result:
            print(r)

def find_crimes_in_location_or_time():
    choice = get_input('Would you like to get crimes for a location or a time period? (L = Location, T = Time Period)', {'l', 't'})
    if choice == 'l':
        location_inputs = {}
        lsoa_inputs = {}
        print('Please enter the location details for the crime (enter NA to leave the field blank).')
        location_inputs['lsoa'] = get_input('LSOA:')
        lsoa_inputs['lsoa'] = location_inputs['lsoa']
        lsoa_inputs['lsoaName'] = get_input('LSOA name:')
        lsoa_inputs['borough'] = get_input('Borough:')
        
        if not location_inputs['lsoa']:
            # QUERY LSOA table with lsoa inputs
            cursor.execute('SELECT lsoa FROM LSOA {};'.format(create_where_clause(lsoa_inputs)))
            lsoa = cursor.fetchall()[0]
            location_inputs['lsoa'] = lsoa
        
        # QUERY Reported Crime with returned crime IDs
        cursor.execute('SELECT crimeReportID, jurisdiction, type, outcome, year, month FROM ReportedCrime INNER JOIN CrimeLocation USING (crimeReportID) {};'.format(create_where_clause(location_inputs)))
        result = cursor.fetchall()
        for r in result:
            print(r)
    else:
        print('Please enter the time period details below')
        startMonth = int(get_input('Start month:', set([str(i) for i in range(1, 13)])))
        startYear = int(get_input('Start year:'))
        endMonth = int(get_input('End month:', set([str(i) for i in range(1, 13)])))
        endYear = int(get_input('End year:'))

        # QUERY reported crime with start and end dates
        cursor.execute('SELECT * FROM ReportedCrime WHERE month BETWEEN {} and {} and year BETWEEN {} and {};'.format(str(startMonth), str(endMonth), str(startYear), str(endYear)))

def find_crime_outcome():
    crime_id = get_input('Please enter the crime ID for which you would like to find the outcome:')
    if crime_id:
        # QUERY reported crime with crime id to get output
        cursor.execute('SELECT outcome FROM ReportedCrime WHERE crimeID = {};'.format(crime_id))
        result = cursor.fetchone()
        print(result)

def get_crimes_of_type():
    print('The following are the crime types: {}'.format(', '.split(crime_major_categories)))
    crime_major_category = get_input('Please enter the type of crime you would like to find:', set([x.lower() for x in crime_major_categories]))
    if crime_major_category:
        # QUERY reported crime to get all crimes with that crime type
        cursor.execute('SELECT * FROM ReportedCrime WHERE majorCategory = {};'.format(crime_major_category))
        result = cursor.fetchall()
        for r in result:
            print(r)

def insert_reported_crime():
    reported_crime_inputs = {}
    crime_location_inputs = {}
    general_crime_inputs = {}
    print('Please enter the following reported crime details.')
    reported_crime_inputs['jurisdiction'] = get_input('Jurisdiction:')
    print('The following are minor crime categories: {}'.format(', '.join(crime_minor_categories)))
    crime_minor_category = get_input('Crime minor category:', set([x.lower() for x in crime_minor_categories]))
    reported_crime_inputs['outcome'] = get_input('Crime outcome:')
    reported_crime_inputs['year'] = get_input('Year of the crime:')
    reported_crime_inputs['month'] = get_input('Month of the crime:', set([str(i) for i in range(1, 13)]))
    crime_location_inputs['lsoa'] = get_input('LSOA:')
    crime_location_inputs['description'] = get_input('Location description:')
    crime_location_inputs['longitude'] = get_input('Location longitude:')
    crime_location_inputs['latitude'] = get_input('Location latitude:')

    # QUERY get max crimeReportID from ReportedCrime
    cursor.execute('SELECT MAX(crimeReportID) FROM ReportedCrime;')
    max_crime_id = cursor.fetchone()
    reported_crime_inputs['crimeReportID'] = str(int(max_crime_id) + 1)
    crime_location_inputs['crimeReportID'] = reported_crime_inputs['crimeReportID']

    # QUERY get major category from minor category
    cursor.execute('SELECT majorCategory FROM CrimeCategory WHERE minorCategory = {};'.format(crime_minor_category))
    reported_crime_inputs['majorCategory'] = cursor.fetchone()[0]

    # QUERY insert crime details into reported crime table
    cursor.execute('INSERT INTO ReportedCrime (crimeID, jurisdiction, type, outcome, year, month) VALUES (%(crimeID)s, %(jurisdiction)s, %(type)s, %(outcome)s, %(year)s, %(month)s);', reported_crime_inputs)
 
    # QUERY insert location details into location table
    cursor.execute('INSERT INTO CrimeLocation (crimeID, longitude, latitude, description, lsoa) VALUES (%(crimeID)s, %(longitude)s, %(latitude)s, %(description)s, %(lsoa)s);', crime_location_inputs)

    cursor.execute('SELECT MAX(generalCrimeID) FROM GeneralCrime;')
    max_crime_id = cursor.fetchone()[0]
    general_crime_inputs['generalCrimeID'] = str(int(max_crime_id) + 1)
    general_crime_inputs['lsoa'] = location_inputs['lsoa']
    general_crime_inputs['minorCategory'] = crime_minor_category
    general_crime_inputs['year'] = reported_crime_inputs['year']
    general_crime_inputs['month'] = reported_crime_inputs['month']

    # QUERY insert crime details into general crime table
    cursor.execute('INSERT INTO GeneralCrime (generalCrimeID, lsoa, minorCategory, year, month) VALUES (%(generalCrimeID)s, %(lsoa)s, %(minorCategory)s, %(year)s, %(month)s);', general_crime_inputs)

    crime_db.commit()

def insert_stop_and_search():
    stop_and_search_inputs = {}
    profile_inputs = {}
    print('Please enter the following stop and search details.')
    stop_and_search_inputs['date'] = get_input('Date in YYYY-MM-DD format:')
    print('Possible types of stops and searches: person search, person and vehicle search')
    stop_and_search_inputs['type'] = get_input('Type:', {'person search', 'person and vehicle search'})
    stop_and_search_inputs['legislation'] = get_input('Legislation:')
    stop_and_search_inputs['objectOfSearch'] = get_input('Object of search:')
    stop_and_search_inputs['outcome'] = get_input('Outcome:')
    
    print('Please enter details about the person that was stopped and searched.')
    profile_inputs['gender'] = get_input('Gender:')
    profile_inputs['selfDefinedEthnicity'] = get_input('Self-Defined Ethnicity:')
    profile_inputs['officerDefinedEthnicity'] = get_input('Officer-Defined Ethnicity:')
    print('Possible age ranges: under 10, 10-17, 18-24, 25-34, over 34')
    profile_inputs['ageRange'] = get_input('Age range:', {'under 10', '10-17', '18-24', '25-34', 'over 34'})

    # QUERY max stop and search id
    cursor.execute('SELECT MAX(searchID) FROM StopAndSearch;')
    max_search_id = int(cursor.fetchone()[0])
    stop_and_search_inputs['searchID'] = str(max_search_id + 1)
    profile_inputs['searchID'] = stop_and_search_inputs['searchID']

    # QUERY insert stop and search details
    cursor.execute('INSERT INTO StopAndSearch (searchID, type, date, legislation, objectOfSearch, outcome) VALUES (%(searchID)s, %(type)s, %(date)s, %(legislation)s, %(objectOfSearch)s, %(outcome)s);', stop_and_search_inputs)

    # QUERY insert person's profile details at search ID
    cursor.execute('INSERT INTO SearchProfile (searchID, gender, ageRange, selfDefinedEthnicity, officerDefinedEthnicity) VALUES (%(searchID)s, %(gender)s, %(ageRange)s, %(selfDefinedEthnicity)s, %(officerDefinedEthnicity)s);', profile_inputs)
    crime_db.commit()

def get_stop_and_searches_aggregate():
    choice = get_input('What category would you like to aggregate by? (O = Officer-defined ethnicity, S = Self-defined ethnicity, A = Age range, G = Gender)', {'o', 's', 'a', 'g'})
    group_by_category = ''
    if choice == 'o':
        group_by_category = 'officerDefinedEthnicity'
    elif choice == 's':
        group_by_category = 'selfDefinedEthnicity'
    elif choice == 'a':
        group_by_category = 'ageRange'
    else:
        group_by_category = 'gender'

    cursor.execute('SELECT COUNT(*) FROM SearchProfile;')
    totalSearches = int(cursor.fetchone()[0])
    cursor.execute('SELECT {group_by_category}, COUNT(*)/{totalSearches} FROM SearchProfile GROUP BY {group_by_category};'.format(totalSearches=totalSearches, group_by_category=group_by_category))
    result = cursor.fetchall()
    for r in result:
        print(r)

role = get_input('What is your role? (P = Police, A = Analyst, C = Citizen)?', {'p', 'a', 'c'})

while True:
    print('--------')
    print('Role: {}'.format(roleMap[role]))
    print('--------')
    
    if role == 'p':
        option = int(get_input(
            """What would you like to do?
1. Get stats about crime type and activity in an area.
2. Find crimes reported in a location or in some time period.
3. Find the outcome of a crime.
4. Identify other crimes of a certain type.
5. Insert new reported crime.
6. Insert new stop and search.
Pick one of the 6 options by entering the number:""",
            set([str(i) for i in range(1, 7)])
        ))

        if option == 1:
            get_area_crime_stats_police()
        elif option == 2:
            find_crimes_in_location_or_time()
        elif option == 3:
            find_crime_outcome()
        elif option == 4:
            get_crimes_of_type()
        elif option == 5:
            insert_reported_crime()
        else:
            insert_stop_and_search()

    elif role.lower() == 'a':
        option = int(get_input(
            """What would you like to do?
1. Get crime data by borough.
2. Get number of stop and searches by person's profile.
Pick one of the 2 options by entering the number:""",
            set([str(i) for i in range(1, 3)])
        ))

        if option == 1:
            get_area_crime_stats_analyst()
        else:
            get_stop_and_searches_aggregate()
    else:
        get_area_crime_stats_citizen()

cursor.close()
crime_db.close()
