lines_per_file = 100000
newfile = None

with open('TravelMapAll_clean1.csv') as infile:
    for lineno, line in enumerate(infile, -1):
        if lineno >= 0:
            if lineno % lines_per_file == 0:
                if newfile:
                    newfile.close()
                new_filename = 'datasets/TravelMapAll_p{}.csv'.format(lineno // lines_per_file + 1)
                newfile = open(new_filename, 'w')
            newfile.write(line)
    if newfile:
        newfile.close()
