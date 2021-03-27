role = ''
roleMap = {
    'p': 'Police',
    'a': 'Analyst',
    'c': 'Citizen',
}
crime_types = set()

def get_input(prompt, valid_values=None):
    user_input = str(input(prompt + ' ')).lower()
    if not valid_values:
        return user_input
    
    while user_input not in valid_values and user_input != 'na':
        user_input = str(input('Please enter a valid value: ')).lower()
    
    return user_input if user_input != 'na' else ''

def get_area_crime_stats():
    borough = get_input('What borough would you like to get crime stats for?')
    # QUERY crimes activity for borough

def find_crimes_in_location_or_time():
    choice = get_input('Would you like to get crimes for a location or a time period? (L = Location, T = Time Period)', {'l', 't'})
    if choice == 'l':
        location_inputs = {}
        lsoa_inputs = {}
        print('Please enter the location details for the crime (enter NA to leave the field blank).')
        location_inputs['lsoa'] = get_input('LSOA:')
        location_inputs['description'] = get_input('Description:')
        location_inputs['longitude'] = get_input('Longitude:')
        location_inputs['latitude'] = get_input('Latitude:')
        lsoa_inputs['lsoa'] = location_inputs['lsoa']
        lsoa_inputs['lsoa_name'] = get_input('LSOA name:')
        lsoa_inputs['borough'] = get_input('Borough:')
        
        # QUERY LSOA table with lsoa inputs
        # QUERY Location table with LSOA details from LSOA table
        # QUERY Reported Crime with returned crime IDs
    else:
        print('Please enter the time period details below')
        startMonth = int(get_input('Start month:', set([str(i) for i in range(1, 13)])))
        startYear = int(get_input('Start year:'))
        endMonth = int(get_input('End month:', set([str(i) for i in range(1, 13)])))
        endYear = int(get_input('End year:'))

        # QUERY reported crime with start and end dates

def find_crime_outcome():
    crime_id = get_input('Please enter the crime ID for which you would like to find the outcome:')
    if crime_id:
        # QUERY reported crime with crime id to get output

def get_crimes_of_type():
    crime_type = get_input('Please enter the type of crime you would like to find:', crime_types)
    if crime_type:
        # QUERY reported crime to get all crimes with that crime type
def insert_reported_crime():
    reported_crime_inputs = {}
    crime_location_inputs = {}
    lsoa_inputs = {}
    print('Please enter the following reported crime details.')
    reported_crime_inputs['crime_id'] = get_input('Crime ID:')
    reported_crime_inputs['jurisdiction'] = get_input('Jurisdiction:')
    reported_crime_inputs['type'] = get_input('Crime type:')
    reported_crime_inputs['outcome'] = get_input('Crime outcome:')
    reported_crime_inputs['year'] = get_input('Year of the crime:')
    reported_crime_inputs['month'] = get_input('Month of the crime:')
    crime_location_inputs['lsoa'] = get_input('LSOA:')
    crime_location_inputs['description'] = get_input('Location description:')
    crime_location_inputs['longitude'] = get_input('Location longitude:')
    crime_location_inputs['latitude'] = get_input('Location latitude:')
    lsoa_inputs['lsoa'] = crime_location_inputs['lsoa']
    lsoa_inputs['lsoa_name'] = get_input('LSOA name:')
    lsoa_inputs['borough'] = get_input('Borough:')

    # QUERY insert crime details into crime table
    # QUERY insert location details into location table

def insert_stop_and_search():
    stop_and_search_inputs = {}
    profile_inputs = {}
    print('Please enter the following stop and search details.')
    stop_and_search_inputs['date'] = get_input('Date:')
    stop_and_search_inputs['type'] = get_input('Type:', crime_types)
    stop_and_search_inputs['legislation'] = get_input('Legislation:')
    stop_and_search_inputs['object_of_search'] = get_input('Object of search:')
    stop_and_search_inputs['found'] = get_input('Found object:', {'y', 'n'}) == 'y'
    stop_and_search_inputs['outcome'] = get_input('Outcome:')
    stop_and_search_inputs['removal_of_clothing'] = get_input('Removal of clothing:', {'y', 'n'}) == 'y'
    
    # QUERY insert stop and search details
    # QUERY stop and search to get search ID
    
    print('Please enter details about the person that was stopped and searched.')
    # profile_inputs['search_id'] = search ID
    profile_inputs['gender'] = get_input('Gender:')
    profile_inputs['self_defined_ethnicity'] = get_input('Self-Defined Ethnicity:')
    profile_inputs['officer_defined_ethnicity'] = get_input('Officer-Defined Ethnicity:')
    profile_inputs['age_range'] = get_input('Age range:')

    # QUERY insert person's profile details at search ID

def get_stop_and_searches_aggregate():
    choice = get_input('What category would you like to aggregate by? (E = Ethnicity, A = Age range, G = Gender)', {'e', 'a', 'g'})
    if choice == 'e':
        # QUERY stop and searches grouped by officer-defined ethnicity and then self-defined ethnicity
    elif choice == 'a':
        # QUERY stop and searches grouped by age range
    else:
        # QUERY stop and searches grouped by gender

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
            get_area_crime_stats()
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
1. Get crime data by year or borough.
2. Get number of stop and searches by person's characteristics.
Pick one of the 2 options by entering the number:""",
            set([str(i) for i in range(1, 3)])
        ))

        if option == 1:
            # get crime by year or borough
        else:
            get_stop_and_searches_aggregate()
        
    else:
        


