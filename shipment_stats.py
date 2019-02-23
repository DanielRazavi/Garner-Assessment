"""
Created on Tue Feb  19 17:16:19 2019

.Done
@author: Dan
"""
import sys
import re
import datetime as dt
from dateutil import tz

location_bank = {('china','shanghai'):['Asia', 'PRC'],
                 ('hong kong','hong kong'):['Asia','Hongkong'],
                 ('usa','cincinnati hub,oh'):['North America','US/Eastern'],
                 ('canada','ontario service area'): ['North America', 'Canada/Eastern'],
                 ('canada','toronto'):['North America','Canada/Eastern']}

time_continent = {}
time_country = {}

the_data = []
current_location = None
current_country = None

max_tuple = [None,None,None,None,None,dt.timedelta(0)]

def lazy_error_msg(string):
    line_number = open(sys.argv[1]).readlines().index(line) + 1
    error_message = "In '" + str(sys.argv[1]) + "', line number " + str(line_number) + ": " + string
    raise Exception(error_message) from None

def give_hm(given_time):
    hours = (given_time.days * 24) + (given_time.seconds // 3600)
    minutes = (given_time.seconds-((given_time.seconds//3600)*3600))//60
    if ((given_time.seconds - (given_time.seconds // 60) * 60) > 0): minutes += 1
    return hours,minutes

def time_tracker():

    global max_tuple

    the_data[-1][5] = time_object - the_data[-1][0]

    if max_tuple[5] < the_data[-1][5]:
        max_tuple = the_data[-1]

    this_country = the_data[-1][3]
    this_continent = location_bank[(the_data[-1][3],the_data[-1][4])][0]

    if this_country in time_country:
        time_country[this_country] += the_data[-1][5]
    else:
        time_country[this_country] = the_data[-1][5]

    if this_continent in time_continent:
        time_continent[this_continent] += the_data[-1][5]
    else:
        time_continent[this_continent] = the_data[-1][5]

def translate_time(given_time):
    try:
        from_tz = tz.gettz(location_bank[(current_country, current_location)][1])
        to_zone = tz.gettz('UTC')
        given_time = given_time.replace(tzinfo=from_tz)
        given_time = given_time.astimezone(to_zone)

    except KeyError:

        if current_country == None:
            lazy_error_msg("Data does not specify where the shipment was picked up from.")
        else:
            lazy_error_msg("Location,"+str((current_location,current_country))+" doesn't exist in location_bank.")

for line in reversed(open(sys.argv[1]).readlines()):

    if re.match(r'Date, Time, Status', line, re.M | re.I):
        continue

    match_str = re.match(r'(\d{4}-\d{2}-\d{2},\s\d{2}:\d{2}:\d{2}),\s(.*)', line, re.M | re.I)

    try:

        time_object = dt.datetime.strptime(match_str.group(1), "%Y-%m-%d, %H:%M:%S")

        match_str2 = re.match(r'(\w+).*', match_str.group(2), re.M | re.I)
        category = match_str2.group(1)

        if category == "Shipment":

            match_str3 = re.match(r'Shipment picked up at (.*),(.*)$', match_str.group(2), re.M | re.I)
            current_location = match_str3.group(1).strip().lower()
            current_country = match_str3.group(2).strip().lower()

            translate_time(time_object)


        elif category in ["Processed","Departed","Clearance"]:
            match_str3 = re.match(r'(Processed at|Departed Facility in|Clearance processing complete at)(.*)-(.*)$', match_str.group(2), re.M | re.I)

            a = (current_location == match_str3.group(2).strip().lower())
            b = (current_country == match_str3.group(3).strip().lower())

            if not(a):
                lazy_error_msg("Logistic Error in status, current_location wasn't `"+ match_str3.group(2).strip().lower() + "` before.")

            elif not(b):
                lazy_error_msg("Logistic Error in status, current_country wasn't `"+ match_str3.group(3).strip().lower() + "` before.")

            translate_time(time_object)
            time_tracker()

        elif category in ["Customs", "With", "Delivery"]:

            its_not_okay = not(re.match(r'^Customs status updated$', match_str.group(2), re.M | re.I)) and\
            not(re.match(r'^With delivery courier$', match_str.group(2), re.M | re.I)) and\
            not(re.match(r'^Delivery attempted; recipient not home$', match_str.group(2), re.M | re.I))

            if its_not_okay:
                lazy_error_msg("Data given is not recognized - e3")

            translate_time(time_object)
            time_tracker()

        elif category == "Arrived":
            match_str3 = re.match(r'Arrived at Sort Facility (.*)-(.*)', match_str.group(2), re.M | re.I)
            current_location = (match_str3.group(1)).strip().lower()
            current_country = (match_str3.group(2)).strip().lower()

            translate_time(time_object)
            time_tracker()

        elif category == "Delivered":
            match_str3 = re.match(r'Delivered - Signed for by receiver in (.*), (.*).', match_str.group(2), re.M | re.I)
            current_location = match_str3.group(1).strip().lower()
            current_country = match_str3.group(2).strip().lower()

            translate_time(time_object)
            time_tracker()

        else:
            lazy_error_msg("Data given is not recognized - e1")

        the_data.append([time_object, match_str.group(2), category, current_country, current_location, dt.timedelta(0)])

    except ValueError:
        lazy_error_msg("Time data '"+ match_str.group(1) +"' doesn't make sense.")

    except AttributeError:
        lazy_error_msg("Data given is not recognized - e2")




total_time = the_data[-1][0] - the_data[0][0]
th, tm = give_hm(total_time)
ah, am = give_hm(time_continent['Asia'])
uh, um = give_hm(time_country['usa'])

print("Total shipment time: {0}:{1}".format(th, tm))
print("Total time in Asia: {0}:{1}".format(ah, am))
print("Total time in USA: {0}:{1}".format(uh, um))
# Are you sure that the Longest shipment step is not the summation of said step overal or just the one instance?
print("Longest shipment step: from \"{0}\" to \"{1}\"".format(max_tuple[1],the_data[the_data.index(max_tuple)+1][1]))