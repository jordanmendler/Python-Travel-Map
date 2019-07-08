import csv
import geopy.distance
import math

countOrig = 0
count = 0
coordinates = []

def distance(lat1, lng1, lat0, lng0):
    deglen = 110.25
    x = lat1 - lat0
    yy = lng1 - lng0
    if x > 0.01 or x < -0.01 or yy > 0.05 or yy < -0.05:
        return 1
    else:
        y = (yy) * math.cos(lat0)
        return deglen * math.sqrt(x*x + y*y)

with open('TravelMapAll_non_America.csv') as infile:
    readCSV = csv.reader(infile, delimiter=',')
    for row in readCSV:
        countOrig += 1
        add = True
        if count == 0:
            count += 1
        elif count == 1:
            coordinates.append((float(row[0]),float(row[1])))
            count += 1
        else:
            new_point = (float(row[0]),float(row[1]))
            for i in range(len(coordinates) - 1, -1, -1):
            #for pair in reversed(coordinates):
                lat1 = new_point[0]
                lat0 = coordinates[i][0]
                lng1 = new_point[1]
                lng0 = coordinates[i][1]

                deglen = 110.25
                x = lat1 - lat0
                yy = lng1 - lng0
                if x < 0.01 and x > -0.01 and yy < 0.05 and yy > -0.05:
                    y = (yy) * math.cos(lat0)
                    if deglen * math.sqrt(x*x + y*y) < 0.5:
                        add = False
                        break
            if add:
                coordinates.append(new_point)
                print(count, 'added:', new_point)
                count += 1

        if countOrig % 50 == 0:
            print('Processed:', countOrig)


with open('TraveelMapAll_nonAmerica_trimmed2.csv', mode='w') as outfile:
    writeCSV = csv.writer(outfile, delimiter=',')
    writeCSV.writerow(['Latitude','Longitude'])
    for pairs in coordinates:
        writeCSV.writerow([pairs[0],pairs[1]])

print('New count:', count)
print('Original count:', countOrig)
