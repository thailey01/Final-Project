import pandas as pd;
import csv;
import math;
from threading import Thread;
from threading import Event;

class RouteMap:
    '''
    Load file into dataframe object
    Run through list of cities and create a city object with city name
    and list of cities names and city distances
    '''

    def __init__(self, file_name):
        print(file_name + "\n");
        print('Fetching cities...\n');
        self.df = pd.read_excel(io = file_name).drop([' '], 1);
        self.cities = self.df.columns;
        self.city_objects = list();

    # Create a dataframe from with our currently explored cities
    # and their closest lists of cities and distances
    def pretty_display(self, thread):
        thread.stop_running();
        print('\n');
        explored_cities_dict = dict();
        for city in self.city_objects:
            possible_cities = list();
            for next_city in city.routes:
                possible_cities.append(next_city + ' ' +
                                       str(round(city.routes[next_city], 2)) + ' || ');
            explored_cities_dict['Node: ' + city.name + ' ' +
                                 str(round(city.get_distance_from_start(), 2)) +
                                 ' || '] = possible_cities;
        explored_cities_df = pd.DataFrame(explored_cities_dict);
        pd.set_option('display.max_rows', 500);
        pd.set_option('display.max_columns', 500);
        pd.set_option('display.width', 150);
        # .head() prints out the first 5 or so objects in the dataframe
        # if you want to increase the number of rows just give .head()
        # an integer parameter (i.e. explored_cities_df.head(10))
        print(explored_cities_df.head());
        print('\n');

    # Return list of cities in original order
    def get_cities_list(self):
        return self.cities.tolist();

    # Return the distances to cities from given city
    def get_cities_distances_list(self, city):
        return self.df[city].tolist();

    # Append city node to city_objects list
    def append_city_by_node(self, city, prev_city, distance = 0):
        past_distance = 0;
        self.city_objects.append(City(city, self.get_cities_list(),
                                      self.get_cities_distances_list(city),
                                      prev_city,
                                      distance));

    # Create node of city and add to city_objects list
    def append_city_by_name(self, city):
        self.city_objects.append(City(city, self.get_cities_list(),
                                      self.get_cities_distances_list(city)));

    # Validate that the user input is actually a city
    def is_valid_city(self, city):
        return city in self.get_cities_list();

    # Remove given city from every city_object in explored list
    # prevents us from going back over city already explored
    def remove_city_from_cities_dictionary(self, city_to_remove):
        for city in self.city_objects:
            city.remove_city(city_to_remove);

    # Remove all already explored cities from every city_object in explored list
    # prevents us from going back over city already explored
    def remove_all_explored_cities(self):
        for curr_city in self.city_objects:
            for city in self.city_objects:
                curr_city.remove_city(city.name);

    # Traverse backwards through the path we found to the end node
    # This finds what the optimal path actually was
    def get_path_from_start_to_end(self):
        path = list();
        curr_node = self.city_objects[-1];
        while curr_node:
            path.append(curr_node);
            curr_node = curr_node.prev_city;
        return path;

    # Break down the currently explored nodes and how we got there
    def print_routes(self):
        for city in self.city_objects:
            print('To:', city.name + ', Distance from start:',
                  city.get_distance_from_start());
            prev_city = city.prev_city;
            while prev_city:
                print('From:', prev_city.name + ', Distance from start:', prev_city.get_distance_from_start());
                prev_city = prev_city.prev_city;
            print('\n---------------------------------------\n');

    # Ask for user input in how many steps of the algorithm they'd like to run through
    # thread.start/stop_running() just lets takes care of printing out progress text
    # so you know the algorithm isn't frozen, just slow
    def get_number_of_steps(self, thread, stop):
        val = None;
        while not isinstance(val, int) or val == 0:
            try:
                if thread.is_running:
                    thread.stop_running();
                val = int(input("\nHow many steps would you like to run through (-1 to finish search): "));
            except ValueError as e:
                print("Invalid number of steps, please make sure you've give a positive integer");
        print('');
        print('Searching', end = '');
        thread.start_running();
        return val;

    # Find which city closest to our currently explored nodes should be the
    # next city to explore.
    # If it's found that a city is closest but too far away in terms of
    # one node to the next in distance (100 miles or more) then we
    # skip that node and find another, unless that destination node has no closer
    # nodes to itself
    def explore_cities(self, prev_city, curr_city,
                       determine_num_steps, steps_counter, thread):
        shortest_distance = 100000000;
        if steps_counter == determine_num_steps:
            self.pretty_display(thread);
        for city in self.city_objects:
            # Distance from the start node to give current city node
            distance_travelled = city.get_distance_from_start();
            # Name of closest city to current city node
            # Distance to closest city from current city node
            # (no including distance from start)
            temp_closest_city, temp_distance = city.get_closest_city();
            # Need to make sure that the possible destination node is
            # the closest it could be to any other node
            temp_next_city = City(temp_closest_city, self.get_cities_list(),
                                      self.get_cities_distances_list(temp_closest_city),
                                      None,
                                      0);
            for temp_curr_city in self.city_objects:
                temp_next_city.remove_city(temp_curr_city.name);
            check_city, check_distance = temp_next_city.get_closest_city();
            if temp_distance > 100 and check_distance < 100:
                continue;
            if (distance_travelled + temp_distance) < shortest_distance:
                prev_city = city;
                curr_city = temp_closest_city;
                shortest_distance = temp_distance + prev_city.get_distance_from_start();
        return prev_city, curr_city, shortest_distance;
    
    # Search function beginning with some starting node and perform
    # Djikstras algorithm
    # will return path of cities taken to get to sink node
    # will return total distance of path taken
    def search(self, start, end):
        prev_city = None;
        distance = 0;
        curr_city = start;
        stop = Event();
        thread = TimerThread(stop);
        thread.start();
        determine_num_steps = self.get_number_of_steps(thread, stop);
        steps_counter = 0;
        while True:
            if steps_counter == determine_num_steps:
                steps_counter = 0;
                determine_num_steps = self.get_number_of_steps(thread, stop);
            steps_counter += 1;
            self.append_city_by_node(curr_city, prev_city, distance);
            self.remove_all_explored_cities();
            prev_city, curr_city, distance = self.explore_cities(prev_city, curr_city,
                                                           determine_num_steps,
                                                           steps_counter, thread);
            if steps_counter == determine_num_steps:
                print('Exploring', curr_city, 'from', prev_city.name);
                print('Distance from', prev_city.name + ':',
                      (distance - prev_city.get_distance_from_start()));
                print('Total distance from start:', distance, '\n');
            if curr_city == end:
                break;
        stop.set();
        thread.stop_running();
        self.append_city_by_node(curr_city, prev_city, distance);
        optimal_path = self.display_explored_cities();
        city_names = list();
        city_distances = list();
        for city in optimal_path:
            city_names.append(city.name);
            city_distances.append(city.get_distance_from_start());
        return city_names, city_distances;

    # Find the optimal path and run through it
    def display_explored_cities(self):
        print("\n\nFound destination!");
        path = self.get_path_from_start_to_end();
        for i in range(len(path)):
            city = path[-1 - i];
            print("City:", city.name);
            print("Distance:", city.get_distance_from_start());
        return path;

class City:
    '''
    Instantiate City object with:
    name,
    previous city object,
    distance from start,
    dictionary: {city: distance to city}
    '''

    def __init__(self, name, cities, distances, prev_city = None, distance_from_start = 0):
        self.name = name;
        self.prev_city = prev_city;
        self.distance_from_start = distance_from_start;
        # creates dictionary for each city of its closest cities and their distances
        routes = {k: v for k, v in zip(cities, distances)};
        # sorts the previous dictionary from least to greatest
        self.routes = {k: v for k, v in sorted(routes.items(), key = lambda x: x[1])};

    # Retrieve the distance from the starting node to this node
    def get_distance_from_start(self):
        return self.distance_from_start;

    # Return closest city name and its distance
    def get_closest_city(self):
        closest = list(self.routes.keys())[0];
        return closest, self.routes[closest];

    # Remove city from routes list
    # This is for after you explore a city
    def remove_city(self, city):
        try:
            return self.routes.pop(city);
        except KeyError as e:
            pass;

    # Return list of all routes from city
    def view_routes(self):
        return self.routes;

# Just a multithread class for dealing with progress text display
class TimerThread(Thread):

    def __init__(self, event):
        Thread.__init__(self);
        self.stopped = event;
        self.is_running = False;

    def start_running(self):
        self.is_running = True;

    def stop_running(self):
        self.is_running = False;

    def run(self):
        while not self.stopped.wait(1.0):
            if self.is_running:
                print('.', end = '');
                
