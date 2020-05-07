#imports to read retrieved file
from tkinter import *;
from tkinter.filedialog import askopenfilename;
from routemap import RouteMap;

def start_process():
    file_name = get_file();
    # Create custom object to handle finding shortest path
    route_map = RouteMap(file_name);
    source = get_node(route_map, 'Enter name of city we\'re starting from: ');
    sink = get_node(route_map, 'Enter name of city we\'re ending at: ');
    path, distances = route_map.search(source, sink);
    covid_dict = load_covid_data();
    perform_birth_death_process(path, covid_dict);

def perform_birth_death_process(path, covid_dict):
    print('');
    for city in reversed(path):
        if city in covid_dict.keys():
            print('Expected number of covid cases in', city, 'is', covid_dict[city][0]);
        else:
            print('No information found for', city);
            

# Retrieve user file
def get_file():
    # Open file in read mode
    # specify exel file
    return './assets/Driving Distances Between Missouri Towns.xlsx';

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
