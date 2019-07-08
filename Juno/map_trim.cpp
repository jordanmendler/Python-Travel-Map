#include <fstream>
#include <iostream>
#include <string>
#include <vector>

using namespace std;

int main()
{
    string line;
    ifstream csvIn;
    csvIn.open("./TravelMapAll_non_America_sorted.csv");
    unsigned int lineCount = 0;
    vector<float> lat;
    vector<float> lng;

    const float DEGLEN = 110.25;

    while( getline(csvIn, line) )
    {
        lineCount++;


        if (lineCount == 1)
        {
            continue;
        }


        vector<string> result;
        boost::split(result, line , boost::is_any_of(","));
        float lat0 = stof(result[0]);
        float lng0 = stof(result[1]);


        if (lineCount == 2)
        {

            lat.push_back(lat0);
            lng.push_back(lng0);
            cout << lat0 << "," << lng0;
            continue;
        }


        if (lineCount > 0 && lineCount % 1000 == 0)
        {
            cerr << "Retained " << lineCount << " of " << lat.size() << " lines";
        }


        for (int i = lat.size() - 1 ; i >= 0; i--)
        {
            float lat1 = lat[$i];
            float lng1 = lng[$i];

            if ( abs(lat1 - lat0) > 0.01 && abs(lng1-lng0) > 0.01 )
            {
                float y = lng1 - lng0;
                float x = lat1 - lat0;
                y = y * cos(lat0);


                if (DEGLEN * sqrt( x*x + y*y ) > 0.5 )
                {
                    lat.push_back(lat0);
                    lng.push_back(lng0);
                    cout << lat0 << "," << lng0;
                    break;
                }
            }
        }
    }
}
