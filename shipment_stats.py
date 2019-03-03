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

class line_info():

    def __init__(self, time, given_status, category):

        self.time = time
        self.status = given_status
        self.info_type = category

        self.country = None
        self.location = None
        self.duration = dt.timedelta(0)

    def translate_time(self):
        try:
            from_tz = tz.gettz(location_bank[(self.country, self.location)][1])
            to_zone = tz.gettz('UTC')
            self.time = self.time.replace(tzinfo=from_tz)
            self.time = self.time.astimezone(to_zone)

        except KeyError:

            if (self.country == None) or (self.location == None):
                lazy_error_msg("Data does not specify where the shipment was picked up from.")
            else:
                lazy_error_msg("Location," + str((self.location, self.country)) + " doesn't exist in location_bank.")


time_continent = {}
time_country = {}
the_data = []
max_obj = line_info(0,0,0)


def lazy_error_msg(string):
    line_number = open(sys.argv[1]).readlines().index(line) + 1
    error_message = "In '" + str(sys.argv[1]) + "', line number " + str(line_number) + ": " + string
    print(error_message)
    exit()

def give_hm(given_time):
    hours = (given_time.days * 24) + (given_time.seconds // 3600)
    minutes = (given_time.seconds-((given_time.seconds//3600)*3600))//60
    if ((given_time.seconds - (given_time.seconds // 60) * 60) > 0): minutes += 1
    return hours,minutes

def time_tracker(given_time):

    global max_obj

    the_data[-1].duration = given_time - the_data[-1].time

    if max_obj.duration < the_data[-1].duration:
        max_obj = the_data[-1]

    this_country = the_data[-1].country
    this_continent = location_bank[(the_data[-1].country,the_data[-1].location)][0]


    if this_country in time_country:
        time_country[this_country] += the_data[-1].duration

    else:
        time_country[this_country] = the_data[-1].duration

    if this_continent in time_continent:
        time_continent[this_continent] += the_data[-1].duration

    else:
        time_continent[this_continent] = the_data[-1].duration

if len(sys.argv)!=2:
    print("Need to give the right number of parameters (one).\nFor example:\n\t python shipment_stats.py test_data.txt")
    exit()

try:
    for line in reversed(open(sys.argv[1]).readlines()):

        if re.match(r'(Date, Time, Status|[\r\n\s]+)', line, re.M | re.I): continue

        match_str = re.match(r'(\d{4}-\d{2}-\d{2},\s\d{2}:\d{2}:\d{2}),\s(.*)', line, re.M | re.I)

        time_object = dt.datetime.strptime(match_str.group(1), "%Y-%m-%d, %H:%M:%S")
        match_str2 = re.match(r'(\w+).*', match_str.group(2), re.M | re.I)
        category = match_str2.group(1)

        if category!="Shipment" and (len(the_data) == 0):
            lazy_error_msg("Shipment was never officially shipped.")
            print("File contains not enouagh/no data.")
            exit()

        line_obj = line_info(time_object, match_str.group(2), category)


        if category in ["Shipment", "Arrived", "Delivered"]:

            match_str3 = re.match(r'(Arrived at Sort Facility|Shipment picked up at|Delivered - Signed for by receiver in)(.*)[,-]([\w\s]*)\.?$', match_str.group(2), re.M | re.I)

            if (category == "Delivered") and not (the_data[-1].country == match_str3.group(3).strip().lower()):
                lazy_error_msg("Logistic Error in status, location wasn't `" + match_str3.group(2).strip().lower() + "` before.")

            line_obj.location = match_str3.group(2).strip().lower()
            line_obj.country = match_str3.group(3).strip().lower()
            line_obj.translate_time()

            if category != "Shipment":
                time_tracker(line_obj.time)


        elif category in ["Processed","Departed","Clearance"]:
            match_str3 = re.match(r'(Processed at|Departed Facility in|Clearance processing complete at)(.*)-(.*)$', match_str.group(2), re.M | re.I)


            a = (the_data[-1].location == match_str3.group(2).strip().lower())
            b = (the_data[-1].country == match_str3.group(3).strip().lower())

            if not(a):
                lazy_error_msg("Logistic Error in status, location wasn't `"+ match_str3.group(2).strip().lower() + "` before.")

            elif not(b):
                lazy_error_msg("Logistic Error in status, country wasn't `"+ match_str3.group(3).strip().lower() + "` before.")

            line_obj.location = match_str3.group(2).strip().lower()
            line_obj.country = match_str3.group(3).strip().lower()
            line_obj.translate_time()
            time_tracker(line_obj.time)

        elif category in ["Customs", "With", "Delivery"]:

            its_not_okay = not(re.match(r'^Customs status updated$', match_str.group(2), re.M | re.I)) and\
            not(re.match(r'^With delivery courier$', match_str.group(2), re.M | re.I)) and\
            not(re.match(r'^Delivery attempted; recipient not home$', match_str.group(2), re.M | re.I))

            if its_not_okay:
                lazy_error_msg("Data given is not recognized - e3")

            line_obj.location = the_data[-1].location
            line_obj.country = the_data[-1].country
            line_obj.translate_time()
            time_tracker(line_obj.time)

        else: lazy_error_msg("Data given is not recognized - e1")

        if the_data:
            if the_data[-1].time > line_obj.time:
                lazy_error_msg("Logistic Error in status, Data travels back in time")

        the_data.append(line_obj)

    if the_data[0].info_type != "Shipment":
        lazy_error_msg("Shipment was never officially shipped.")

    elif the_data[-1].info_type != "Delivered":
        lazy_error_msg("Shipment was never delivered.")


    total_time = the_data[-1].time - the_data[0].time
    th, tm = give_hm(total_time)

    if not('Asia' in time_continent):
        ah,am = 0
    else:
        ah, am = give_hm(time_continent['Asia'])

    if not('usa' in time_country):
        uh, um = 0, 0
    else:
        uh, um = give_hm(time_country['usa'])



except ValueError:
    lazy_error_msg("Time data '"+ match_str.group(1) +"' doesn't make sense.")

except AttributeError:
    lazy_error_msg("Data given is not recognized - e2")

except IndexError:
    print("File contains not enough/no data")
    exit()

except NameError:
    print("File contains not enough/no data.")
    exit()

except FileNotFoundError:
    print("Need to pass in a proper file.\nFor example:\n\t python shipment_stats.py test_data.txt")
    exit()



print("Total shipment time: {0}:{1}".format(th, tm))
print("Total time in Asia: {0}:{1}".format(ah, am))
print("Total time in USA: {0}:{1}".format(uh, um))
print("Longest shipment step: from \"{0}\" to \"{1}\"".format(max_obj.status,the_data[the_data.index(max_obj)+1].status))

# Resseting the data variables since they are no longer needed
time_continent = None
time_country = None
the_data = None
max_obj = None