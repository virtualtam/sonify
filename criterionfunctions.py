'''
This module holds criterion functions which can be applied to DataObjects. Criterion functions 
define how DataObjects should be compared to determine which ones should be
kept. The criterion function should return a comparable value; the ones that return the
largest values are the ones kept. Note that they can also be composed using create_combined_criterion()

Created on May 29, 2013
@author: egg
'''

def record_length(data_object):
    ''' Compare length of an arbitrary TimeSeries member of the DataObject 
    (they're assumed to all be the same length) '''
    key = data_object.keys()[0]
    return len(data_object[key]) # longer is better

def longer_than(n):
    def is_longer_than(data_object):
        key = data_object.keys()[0]
        return len(data_object[key]) > n
    return is_longer_than

def reject_prime_meridian_crossers(data_object):
    ''' If a satellite crosses the 0-degree line, it jumps to 360. This gives the impression
    of discontinuous motion, which doesn't reflect reality. You can apply a function to longitude
    that makes it continuous (eg convert to a sin/cos pair), or just punt by using this 
    criterion function. '''
    assert 'LON' in data_object.keys() # otherwise WTF are you doing?
    ts = data_object['LON']
    ts_sorted = sorted(ts)
    if ts_sorted[0] < 5 and ts_sorted[-1] > 355: return False
    return True

def get_nearness_function(lat, lon):
    def nearness_function(data_object):
        start_lat = data_object['LAT'][0]
        start_lon = data_object['LON'][0]
        lat_diff = start_lat - lat
        lon_diff = start_lon - lon
        return -1 * (lat_diff ** 2 + lon_diff ** 2) # pythagorean theorem. skip the sqrt for efficiency. Sign flipped for heapq
    return nearness_function

def get_num_missing_values_function(missing_value):
    def num_missing_values(data_object):
        ''' returns a value representing the combined number of missing values in the first and last
        members of the time series. Sign inverted to fit heapq expectations. '''
        total_missing = 0
        for ts in data_object.values():
            if ts[0] == missing_value:  total_missing += 1
            if ts[-1] == missing_value: total_missing += 1
        return -1 * total_missing # flip sign for heapq
    return num_missing_values

def create_combined_criterion(list_of_functions):
    ''' Use a tuple of the results from multiple functions. Useful where the result of the first
    function is likely to be the same for all DataObjects (eg where we use record_length for all
    when we expect them to all be the same length) '''
    def combined_criterion(data_object):
        return [f(data_object) for f in list_of_functions]
    return combined_criterion

#TODO a weighted combination might be really useful too.
