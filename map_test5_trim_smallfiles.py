import math

countOrig = 0
count = 0
coordinates = []
my_files = []
for i in range(1, 14):
    my_files.append('datasets/TravelMapAll_p{}.csv'.format(i))
#print(my_files)

for filename in my_files:
    coords = []
    with open(filename) as infile:
        for row in infile:
            row = row.strip().split(',')
            new_point = (float(row[0]),float(row[1]))

            add = True
            if coords == None:
                coords.append(new_point)
                count += 1
                print(count, 'added:', new_point)
            else:
                for j in range(len(coords) - 1, -1, -1):
                    lat1 = new_point[0]
                    lat0 = coords[j][0]
                    lng1 = new_point[1]
                    lng0 = coords[j][1]

                    deglen = 110.25
                    x = lat1 - lat0
                    yy = lng1 - lng0
                    if x < 0.01 and x > -0.01 and yy < 0.05 and yy > -0.05:
                        y = (yy) * math.cos(lat0)
                        if deglen * math.sqrt(x*x + y*y) < 0.5:
                            add = False
                            break
                if add:
                    coords.append(new_point)
                    #print(count, 'added:', new_point)
                    count += 1

            countOrig += 1
            if countOrig % 100 == 0:
                print('Processed:', countOrig)

    coordinates = coordinates + coords

print('New count:', count)
print('Original count:', countOrig)

with open('TravelMapAll_trimmed.csv', mode='w') as outfile:
    outfile.write('Latitude,Longitude\n')
    for pairs in coordinates:
        outfile.write(f'{pairs[0]},{pairs[1]}\n')
