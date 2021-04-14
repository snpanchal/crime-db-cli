import mysql.connector
import sys

crime_db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='crime_db',
    port=3308
)
cursor = crime_db.cursor()

role = ''
role_map = {
    'p': 'Police',
    'a': 'Analyst',
    'c': 'Citizen',
}
month_set = set([str(i) for i in range(1, 13)])
year_set = set([str(i) for i in range(2000, 3000)])
crime_minor_categories = ['Burglary in Other Buildings', 'Other violence', 'Personal Property', 'Other Theft', 'Offensive Weapon', 'Criminal Damage To Other Building', 'Theft/Taking of Pedal Cycle', 'Motor Vehicle Interference & Tampering', 'Theft/Taking Of Motor Vehicle', 'Wounding/GBH', 'Other Theft Person', 'Common Assault', 'Theft From Shops', 'Possession Of Drugs', 'Harassment', 'Handling Stolen Goods', 'Criminal Damage To Dwelling', 'Burglary in a Dwelling', 'Criminal Damage To Motor Vehicle', 'Other Criminal Damage', 'Counted per Victim', 'Going Equipped', 'Other Fraud & Forgery', 'Assault with Injury', 'Drug Trafficking', 'Other Drugs', 'Business Property', 'Other Notifiable', 'Other Sexual', 'Theft From Motor Vehicle', 'Rape', 'Murder']
crime_major_categories = ['Burglary', 'Violence Against the Person', 'Robbery', 'Theft and Handling', 'Criminal Damage', 'Drugs', 'Fraud or Forgery', 'Other Notifiable Offences', 'Sexual Offences']

def get_input(prompt='', table_name='', valid_values=None, can_add_value=False):
    if not prompt:
        return ''
    domain_values = []
    print(prompt)
    if table_name:
        cursor.execute(f'SELECT * FROM {table_name};')
        domain_values = [x[0] for x in cursor.fetchall()]
        if can_add_value:
            domain_values.append('Add new value')
        options = [f'{i + 1}. {domain_values[i]}' for i in range(len(domain_values))]
        print('Valid values:\n{}'.format("\n".join(options)))
        valid_values = set([str(i + 1) for i in range(len(domain_values))])
    user_input = str(input('Please enter a value (press Enter to leave blank): ')).lower()
    if not valid_values or not user_input:
        return user_input
    
    while user_input and user_input not in valid_values:
        user_input = str(input('Please enter a valid value (press Enter to leave blank): ')).lower()
    
    if can_add_value and user_input and int(user_input) == len(domain_values):
        new_value = input('What is the new value you want to add? ')
        cursor.execute(f'INSERT INTO {table_name} VALUES ({new_value});')
        return new_value
    
    if not table_name:
        return user_input

    return domain_values[int(user_input) - 1] 

def create_where_clause(inputs):
    where_clause = 'WHERE'
    first = True
    for key in inputs.keys():
        if inputs[key]:
            if not first:
                where_clause += ' AND'
            where_clause += (f' {key} = "{inputs[key]}"')
            first = False

    return where_clause if where_clause != 'WHERE' else ''

def get_area_crime_stats_police():
    choice = get_input(prompt='What would you like to search crime stats by? (Borough = B, LSOA = L)', valid_values={'b', 'l'})
    if choice == 'l':
        lsoa = str(input('What LSOA would you like to get crime stats for? '))
        if lsoa:
            # QUERY crimes activity for LSOA
            cursor.execute(f'SELECT year, majorCategory, COUNT(crimeReportID)*100000/population AS crimesPerCapita FROM CrimeLocation INNER JOIN ReportedCrime USING (crimeReportID) INNER JOIN LSOA USING (lsoa) WHERE lsoa = "{lsoa}" GROUP BY year, majorCategory;')
            result = cursor.fetchall()
            for r in result:
                print(r)
    else:
        borough = get_input(prompt='What borough would you like to get crime stats for?', table_name='LondonBorough')
        if borough:
            query = f'SELECT SUM(population) FROM LSOA WHERE borough = "{borough}";'
            cursor.execute(query)
            borough_population = cursor.fetchone()[0]

            # QUERY crimes activity for borough
            cursor.execute(f'SELECT year, majorCategory, COUNT(crimeReportID)*100000/{borough_population} AS crimesPerCapita FROM CrimeLocation INNER JOIN ReportedCrime USING (crimeReportID) INNER JOIN LSOA USING (lsoa) WHERE borough = "{borough}" GROUP BY year, majorCategory;')
            result = cursor.fetchall()
            for r in result:
                print(r)

def get_area_crime_stats_analyst():
    cursor.execute('SELECT borough, year, majorCategory, COUNT(generalCrimeID)*100000/SUM(population) AS crimesPerCapita FROM LSOA INNER JOIN GeneralCrime USING (lsoa) INNER JOIN CrimeCategory USING (minorCategory) GROUP BY borough, year, majorCategory ORDER BY borough, year, majorCategory;')
    result = cursor.fetchall()
    for r in result:
        print(r)

def get_area_crime_stats_citizen():
    choice = get_input(prompt='How would you like to aggregate crime stats? (Year = Y, Category = C)', valid_values={'y', 'c'})
    lsoa = get_input(prompt='What LSOA would you like to get crime stats for?')
    if lsoa:
        if choice == 'c':
            # QUERY crimes activity for LSOA
            cursor.execute(f'WITH LSOACrimes AS (SELECT minorCategory, COUNT(generalCrimeID) AS numberOfCrimes FROM GeneralCrime WHERE lsoa = "{lsoa}" GROUP BY minorCategory) SELECT minorCategory, SUM(numberOfCrimes) AS numberOfCrimes FROM (SELECT * from LSOACrimes UNION (SELECT minorCategory, 0 AS numberOfCrimes FROM CrimeCategory)) AS temp GROUP BY minorCategory;')
        else:
            cursor.execute(f'SELECT year, count(generalCrimeID) FROM GeneralCrime WHERE lsoa = "{lsoa}" GROUP BY year ORDER BY year;')
        result = cursor.fetchall()
        for r in result:
            print(r)
            

def find_crimes_in_location_or_time():
    choice = get_input(prompt='Would you like to get crimes for a location or a time period? (L = Location, T = Time Period)', valid_values={'l', 't'})
    if choice == 'l':
        location_inputs = {}
        lsoa_inputs = {}
        print('Please enter the location details for the crime (press Enter to leave the field blank).')
        location_inputs['lsoa'] = get_input('LSOA') 
        lsoa_inputs['lsoa'] = location_inputs['lsoa']
        if not location_inputs['lsoa']:
            lsoa_inputs['lsoaName'] = get_input(prompt='LSOA name')
            lsoa_inputs['borough'] = get_input(prompt='Borough', table_name='LondonBorough')
        
            # QUERY LSOA table with lsoa inputs
            cursor.execute(f'SELECT lsoa FROM LSOA {create_where_clause(lsoa_inputs)};')
            lsoa = cursor.fetchall()[0][0]
            location_inputs['lsoa'] = lsoa
        
        # QUERY Reported Crime with returned crime IDs
        cursor.execute(f'SELECT crimeReportID, majorCategory, outcome, year, month FROM ReportedCrime INNER JOIN CrimeLocation USING (crimeReportID) {create_where_clause(location_inputs)};')

        result = cursor.fetchall()
        for r in result:
            print(r)
    else:
        print('Please enter the time period details below')
        startMonth = int(get_input(prompt='Start month (1-12)', valid_values=month_set))
        startYear = int(get_input(prompt='Start year'))
        endMonth = int(get_input(prompt='End month (1-12)', valid_values=month_set))
        endYear = int(get_input(prompt='End year'))

        # QUERY reported crime with start and end dates
        cursor.execute(f'SELECT * FROM ReportedCrime WHERE month BETWEEN {str(startMonth)} and {str(endMonth)} and year BETWEEN {str(startYear)} and {str(endYear)};')
    
        result = cursor.fetchall()
        for r in result:
            print(r)

def get_crime_details():
    crime_id = get_input(prompt='Crime ID for which you would like to get the details')
    if crime_id:
        # QUERY reported crime with crime id to get output
        cursor.execute(f'SELECT * FROM ReportedCrime WHERE crimeReportID = {crime_id};')
        result = cursor.fetchone()
        print(result)
        print()

def get_crimes_of_type():
    print(f'The following are the crime types: {", ".join(crime_major_categories)}')
    crime_major_category = get_input(prompt='Type of crime you would like to find', valid_values=set([x.lower() for x in crime_major_categories]))
    if crime_major_category:
        # QUERY reported crime to get all crimes with that crime type
        cursor.execute(f'SELECT * FROM ReportedCrime WHERE majorCategory = "{crime_major_category}";')
        result = cursor.fetchall()
        for r in result:
            print(r)

def get_stop_and_search_details():
    search_id = get_input(prompt='Search ID for which you would like to get the details')
    if search_id:
        # QUERY stop and search with search id to get output
        cursor.execute(f'SELECT * FROM StopAndSearch WHERE searchID = {search_id};')
        result = cursor.fetchone()
        print(result)
        print()

def update_existing_crime_outcome():
    crime_id = get_input(prompt='Crime ID for which you would like to update the outcome')
    if crime_id:
        new_outcome = get_input(prompt='New outcome of crime', table_name='CrimeOutcome')
        if new_outcome:
            cursor.execute(f'UPDATE ReportedCrime SET outcome = "{new_outcome}" WHERE crimeReportID = {crime_id};')
            crime_db.commit()

def update_existing_search_outcome():
    search_id = get_input(prompt='Search ID for which you would like to update the outcome')
    if search_id:
        new_outcome = get_input(prompt='New outcome of stop and search', table_name='SearchOutcome')
        if new_outcome:
            cursor.execute(f'UPDATE StopAndSearch SET outcome = "{new_outcome}" WHERE searchID = {search_id};')
            crime_db.commit()

def insert_reported_crime():
    reported_crime_inputs = {}
    crime_location_inputs = {}
    general_crime_inputs = {}
    crime_minor_category = get_input(prompt='\nPlease select the minor category of the crime.', table_name='CrimeCategory')
    reported_crime_inputs['outcome'] = get_input(prompt='\nPlease select the outcome of the crime.', table_name='CrimeOutcome')
    reported_crime_inputs['year'] = get_input(prompt='\nPlease enter the year the crime occurred.', valid_values=year_set)
    reported_crime_inputs['month'] = get_input(prompt='\nPlease enter the month the crime occurred. (1-12)', valid_values=month_set)
    crime_location_inputs['lsoa'] = get_input(prompt='\nPlease enter the LSOA where the crime occured (Press ENTER to skip).')
    crime_location_inputs['description'] = get_input(prompt='\nPlease enter the location description (Press ENTER to skip).')
    crime_location_inputs['longitude'] = get_input(prompt='\nPlease enter the longitude of the crime location (Press ENTER to skip).')
    crime_location_inputs['latitude'] = get_input(prompt='\nPlease enter the latitude of the crime location (Press ENTER to skip).')

    # QUERY get max crimeReportID from ReportedCrime
    cursor.execute('SELECT MAX(crimeReportID) FROM ReportedCrime;')
    reported_crime_id = int(cursor.fetchone()[0]) + 1
    reported_crime_inputs['crimeReportID'] = str(reported_crime_id)
    crime_location_inputs['crimeReportID'] = reported_crime_inputs['crimeReportID']

    # QUERY get major category from minor category
    cursor.execute(f'SELECT majorCategory FROM CrimeCategory WHERE minorCategory = "{crime_minor_category}";')
    reported_crime_inputs['majorCategory'] = cursor.fetchone()[0]
    print(f'\nYour reported crime ID is {str(reported_crime_id)}.\n')

    # QUERY insert crime details into reported crime table
    cursor.execute('INSERT INTO ReportedCrime (crimeReportID, majorCategory, outcome, year, month) VALUES (%(crimeReportID)s, %(majorCategory)s, %(outcome)s, %(year)s, %(month)s);', reported_crime_inputs)
 
    # QUERY insert location details into location table
    if crime_location_inputs['lsoa'] != '' or crime_location_inputs['description'] != '' or crime_location_inputs['longitude'] != '' or crime_location_inputs['latitude'] != '':
        cursor.execute('INSERT INTO CrimeLocation (crimeReportID, longitude, latitude, description, lsoa) VALUES (%(crimeReportID)s, %(longitude)s, %(latitude)s, %(description)s, %(lsoa)s);', crime_location_inputs)

    if crime_location_inputs['lsoa'] != "":
        # QUERY get max crimeReportID from GeneralCrime
        cursor.execute('SELECT MAX(generalCrimeID) FROM GeneralCrime;')
        general_crime_id = int(cursor.fetchone()[0]) + 1
        general_crime_inputs['generalCrimeID'] = str(general_crime_id)
        general_crime_inputs['lsoa'] = crime_location_inputs['lsoa']
        general_crime_inputs['minorCategory'] = crime_minor_category
        general_crime_inputs['year'] = reported_crime_inputs['year']
        general_crime_inputs['month'] = reported_crime_inputs['month']

        # QUERY insert crime details into general crime table
        cursor.execute('INSERT INTO GeneralCrime (generalCrimeID, lsoa, minorCategory, year, month) VALUES (%(generalCrimeID)s, %(lsoa)s, %(minorCategory)s, %(year)s, %(month)s);', general_crime_inputs)

    crime_db.commit()

def insert_stop_and_search():
    stop_and_search_inputs = {}
    profile_inputs = {}
    stop_and_search_inputs['date'] = get_input(prompt='\nPlease enter the date of the search in YYYY-MM-DD format.')
    stop_and_search_inputs['type'] = get_input(prompt='\nPlease select the type of search.', table_name='SearchType', can_add_value=True)
    stop_and_search_inputs['legislation'] = get_input(prompt='\nPlease select the legislation under which the search was conducted.', table_name='SearchLegislation', can_add_value=True)
    stop_and_search_inputs['objectOfSearch'] = get_input(prompt='\nPlease select the object of the search.', table_name='ObjectOfSearch', can_add_value=True)
    stop_and_search_inputs['outcome'] = get_input(prompt='\nPlease select the final outcome of the search.', table_name='SearchOutcome')
    
    profile_inputs['gender'] = get_input(prompt='\nPlease select the gender of the person searched.', table_name='Gender')
    profile_inputs['selfDefinedEthnicity'] = get_input(prompt='\nPlease select the self-defined ethnicity of the person searched.', table_name='DetailedEthnicity')
    profile_inputs['officerDefinedEthnicity'] = get_input(prompt='\nPlease select the officer-defined ethnicity of the person searched.', table_name='SimpleEthnicity')
    profile_inputs['ageRange'] = get_input(prompt='\nPlease select the age range of the person searched.', table_name='AgeRange')

    # QUERY max stop and search id
    cursor.execute('SELECT MAX(searchID) FROM StopAndSearch;')
    search_id = int(cursor.fetchone()[0]) + 1
    stop_and_search_inputs['searchID'] = str(search_id)
    profile_inputs['searchID'] = stop_and_search_inputs['searchID']
    print(f'\nYour search ID is {str(search_id)}.\n')

    # QUERY insert stop and search details
    cursor.execute('INSERT INTO StopAndSearch (searchID, type, date, legislation, objectOfSearch, outcome) VALUES (%(searchID)s, %(type)s, %(date)s, %(legislation)s, %(objectOfSearch)s, %(outcome)s);', stop_and_search_inputs)

    # QUERY insert person's profile details at search ID
    if profile_inputs['gender'] != '' or profile_inputs['selfDefinedEthnicity'] != '' or profile_inputs['officerDefinedEthnicity'] != '' or profile_inputs['ageRange']:
        cursor.execute('INSERT INTO SearchProfile (searchID, gender, ageRange, selfDefinedEthnicity, officerDefinedEthnicity) VALUES (%(searchID)s, %(gender)s, %(ageRange)s, %(selfDefinedEthnicity)s, %(officerDefinedEthnicity)s);', profile_inputs)
    crime_db.commit()

def get_stop_and_searches_aggregate():
    choice = get_input(prompt='What category would you like to aggregate by? (O = Officer-defined ethnicity, S = Self-defined ethnicity, A = Age range, G = Gender)', valid_values={'o', 's', 'a', 'g'})
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
    total_searches = int(cursor.fetchone()[0])
    cursor.execute(f'SELECT {group_by_category}, COUNT(*)/{total_searches} FROM SearchProfile GROUP BY {group_by_category};')
    result = cursor.fetchall()
    for r in result:
        print(r)

role = get_input(prompt='What is your role? (P = Police, A = Analyst, C = Citizen)?', valid_values={'p', 'a', 'c'})

while True:
    print('--------')
    print(f'Role: {role_map[role]}')
    print('--------')
    
    if role == 'p':
        option = int(get_input(
            prompt="""
What would you like to do?
1. Get stats about crime type and activity in an area.
2. Find crimes reported in a location or in some time period.
3. Get the details for a crime.
4. Identify other crimes of a certain type.
5. Get the details for a search.
6. Update an existing crime's outcome.
7. Update an existing search's outcome.
8. Insert new reported crime.
9. Insert new stop and search.

Pick one of the 9 options by entering the corresponding number""",
            valid_values=set([str(i) for i in range(1, 10)])
        ))

        if option == 1:
            get_area_crime_stats_police()
        elif option == 2:
            find_crimes_in_location_or_time()
        elif option == 3:
            get_crime_details()
        elif option == 4:
            get_crimes_of_type()
        elif option == 5:
            get_stop_and_search_details()
        elif option == 6:
            update_existing_crime_outcome()
        elif option == 7:
            update_existing_search_outcome()
        elif option == 8:
            insert_reported_crime()
        elif option == 9:
            insert_stop_and_search()

    elif role.lower() == 'a':
        option = int(get_input(
            prompt="""What would you like to do?
1. Get crime data by borough.
2. Get number of stop and searches by person's profile.
Pick one of the 2 options by entering the number""",
            valid_values=set([str(i) for i in range(1, 3)])
        ))

        if option == 1:
            get_area_crime_stats_analyst()
        elif option == 2:
            get_stop_and_searches_aggregate()
    else:
        get_area_crime_stats_citizen()

cursor.close()
crime_db.close()

