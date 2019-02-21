"""
Created on Tue Feb  19 17:16:19 2019

.Done
@author: Dan
"""
import sys
import re
import datetime as dt

# key   <- country | value <- continent of said country
country_continent = {'china':'Asia', 'hong kong':'Asia','canada':'North America','usa':'North America'}
# key   <- continent | value <- hours spent in said continent
time_continent = {}
# key   <- country | value <- hours spent in said country
time_country = {}

the_data = []
current_country = "blank"

max_time_object = dt.timedelta(0)
max_tuple = []

def time_translate(given_time):
    hours = (given_time.days * 24) + (given_time.seconds // 3600)
    minutes = (given_time.seconds-((given_time.seconds//3600)*3600))//60
    if ((given_time.seconds - (given_time.seconds // 60) * 60) > 0): minutes += 1
    return hours,minutes

def time_tracker():
    global max_time_object
    global max_tuple
    the_data[-1][4] = time_object - the_data[-1][0]

    if max_time_object < the_data[-1][4]:
        max_time_object = the_data[-1][4]
        max_tuple = the_data[-1]

    continent = country_continent[the_data[-1][3]]

    if the_data[-1][3] in time_country:
        time_country[the_data[-1][3]] += the_data[-1][4]
    else:
        time_country[the_data[-1][3]] = the_data[-1][4]

    if continent in time_continent:
        time_continent[continent] += the_data[-1][4]
    else:
        time_continent[continent] = the_data[-1][4]

for line in reversed(open(sys.argv[1]).readlines()):

    match_str = re.match(r'(\d\d\d\d-\d\d-\d\d, \d\d:\d\d:\d\d), (.*)', line, re.M | re.I)

    if match_str:
        time_object = dt.datetime.strptime(match_str.group(1), "%Y-%m-%d, %H:%M:%S")

        match_str2 = re.match(r'(\w+).*', match_str.group(2), re.M | re.I)
        category = match_str2.group(1)

        if category == "Shipment":
            match_str3 = re.match(r'.*\s(\w+)$', match_str.group(2), re.M | re.I)
            current_country = match_str3.group(1).strip().lower()

            current_tuple = [time_object, match_str.group(2), category, current_country, 0]
            the_data.append(current_tuple)

        elif category in ["Customs", "Processed", "Departed", "Clearance", "With", "Delivery"]:
            time_tracker()

            # time_continent[]
            current_tuple = [time_object, match_str.group(2),category, current_country, 0]
            the_data.append(current_tuple)

        elif category == "Arrived":
            time_tracker()

            match_str3 = re.match(r'.*-(.*)', match_str.group(2), re.M | re.I)
            current_country = (match_str3.group(1)).strip().lower()

            current_tuple = [time_object, match_str.group(2),category, current_country, 0]
            the_data.append(current_tuple)

        elif category == "Delivered":
            time_tracker()
            last_length = dt.timedelta(0)
            current_tuple = [time_object, match_str.group(2),category, current_country, last_length]
            the_data.append(current_tuple)


total_time = the_data[-1][0] - the_data[0][0]
th,tm = time_translate(total_time)
ah, am = time_translate(time_continent['Asia'])
uh, um = time_translate(time_country['usa'])


print("Total shipment time: {0}:{1}".format(th, tm))
print("Total time in Asia: {0}:{1}".format(ah, am))
print("Total time in USA: {0}:{1}".format(uh, um))
# Are you sure that the Longest shipment step is not the summation of said step overal or just the one instance?
print("Longest shipment step: from \"{0}\" to \"{1}\"".format(max_tuple[1],the_data[the_data.index(max_tuple)+1][1]))