import csv

#Delete 'Name' column and invalid coords
with open('Travel_Map_Cleaned.csv', mode='w') as outfile:
    count = -1
    writeCSV = csv.writer(outfile, delimiter=',')
    with open('Travel_Map_All.csv') as infile:
        readCSV = csv.reader(infile, delimiter=',')
        for row in readCSV:
            if count == -1:
                count +=1
            else:
                if float(row[0]) < 85 and float(row[0]) > -60 and float(row[1]) <= 180 and float(row[1]) >= -180:
                    writeCSV.writerow([row[0],row[1]])
                    count += 1

print(count)
