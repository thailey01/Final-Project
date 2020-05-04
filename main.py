#imports to read retrieved file
from tkinter import *;
from tkinter.filedialog import askopenfilename;
from routemap import RouteMap;
import datetime;
import math;

def start_process():
    try:
        file_name = get_file();
        # Create custom object to handle finding shortest path
        route_map = RouteMap(file_name);
        source = get_node(route_map, 'Enter name of city we\'re starting from: ');
        sink = get_node(route_map, 'Enter name of city we\'re ending at: ');
        path, distances = route_map.search(source, sink);
        covid_dict = load_covid_data();
        perform_birth_death_process(path, covid_dict);
    except FileNotFoundError as e:
        print("You must select an excel file to import cities");

def perform_birth_death_process(path, covid_dict):
    start = datetime.date(2020, 1, 16);
    today = datetime.date(2020, 5, 4);
    difference = today - start;
    for city in reversed(path):
        if city in covid_dict.keys():
            lam = .05;
            mu = .78;
            print('Expected number of covid cases in', city, 'is', covid_dict[city][0]);
            

# Retrieve user file
def get_file():
    # Open file in read mode
    # specify exel file
    return './assets/Driving Distances Between Missouri Towns.xlsx';
    #return askopenfilename(title = 'Select Path To City Excel File', filetypes = (('', '*.xlsx'),));

# Retrieve covid file
def load_covid_data():
    covid_dict = {};
    with open('./assets/data.txt', 'r') as f:
        for item in f:
            # Data presented in form county, cases, deaths, pop. cases/100k
            line = item.split('\t');
            covid_dict[line[0]] = line[1:-1];
    return covid_dict;
    
# Retrieve user input for city
def get_node(route_map, message):
    while True:
        city = str(input(message));
        if route_map.is_valid_city(city):
            return city;
        else:
            print('Invalid city\n');

if __name__ == '__main__':
    # Takes care of showing file dialog
    root = Tk();
    root.withdraw();
    root.call('wm', 'attributes', '.', '-topmost', True);
    load_covid_data();
    # Calls function to get user input and search
    start_process();
