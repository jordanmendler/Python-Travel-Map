# Python-Travel-Map: Create a travel map based on coordinates from one or more CSV, KML, or JSON file

# Install dependences: Note that it must be electron@1.8.4 and not just latest
# version of electron or else Orca breaks
npm install -g electron@1.8.4 orca
pip3 install --user orca psutil requests plotly pandas

# Extract sample inputs
mkdir tmp/

for f in Samples/*.gz ; do 
    gunzip -kc "$f" > "tmp/$(basename "$f" .gz)"
done

# Plot all points from sample inputs
./plot_travel_map.py tmp/*

# Can also plot everything recursively under a directory
./plot_travel_map.py ~/Takeout/
