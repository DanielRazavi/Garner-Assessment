"""
Created on Tue Feb  19 17:16:19 2019

.Done
@author: Dan
"""
import sys
import re
import datetime as dt

the_file = sys.argv[1]
the_data = []
current_country = "blank"

test = dt.datetime.strptime("2017-01-01, 12:00:00", "%Y-%m-%d, %H:%M:%S")
max_time_object = test - test
max_tuple = []


for line in reversed(open(sys.argv[1]).readlines()):
    # the_data.append(line)
    match_str = re.match(r'(\d\d\d\d-\d\d-\d\d, \d\d:\d\d:\d\d), (.*)', line, re.M | re.I)
    if match_str:
        time_object = dt.datetime.strptime(match_str.group(1), "%Y-%m-%d, %H:%M:%S")

        match_str2 = re.match(r'(\w+).*', match_str.group(2), re.M | re.I)
        category = match_str2.group(1)

        if category == "Shipment":
            match_str3 = re.match(r'.*\s(\w+)$', match_str.group(2), re.M | re.I)
            current_country = match_str3.group(1)
            current_tuple = [time_object, match_str.group(2),category, current_country, 0]
            the_data.append(current_tuple)

        elif category in ["Customs", "Processed", "Departed", "Clearance", "With", "Delivery"]:
            the_data[-1][3] = time_object - the_data[-1][0]
            if max_time_object < the_data[-1][3]:
                max_time_object = the_data[-1][3]
                max_tuple = the_data[-1]

            current_tuple = [time_object, match_str.group(2),category, current_country, 0]
            the_data.append(current_tuple)

        elif category == "Arrived":
            the_data[-1][3] = time_object - the_data[-1][0]
            if max_time_object < the_data[-1][3]:
                max_time_object = the_data[-1][3]
                max_tuple = the_data[-1]

            match_str3 = re.match(r'.*-(.*)', match_str.group(2), re.M | re.I)
            current_country = (match_str3.group(1)).strip()
            current_tuple = [time_object, match_str.group(2),category, current_country, 0]
            the_data.append(current_tuple)

        elif category == "Delivered":
            the_data[-1][3] = time_object - the_data[-1][0]
            if max_time_object < the_data[-1][3]:
                max_time_object = the_data[-1][3]
                max_tuple = the_data[-1]

            last_length = time_object - time_object
            current_tuple = [time_object, match_str.group(2),category, current_country, last_length]
            the_data.append(current_tuple)


# Are you sure that the Longest shipment step is not the summation of said step overal or just the one instance?
print("Longest shipment step: from \"{0}\" to \"{1}\"".format(max_tuple[1],the_data[the_data.index(max_tuple)+1][1]))


# for i in the_data:
#     print(i)