import datetime

import googlemaps
import matplotlib.pyplot as plt
import pandas as pd
import ast
import seaborn as sns
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy.distance import geodesic
import openrouteservice
from openrouteservice import convert
import time
import math


def haversine_distance(coord1, coord2):
    """
    Calculate the Haversine distance between two points on the Earth.

    Parameters:
    coord1: tuple of (lat1, lon1) for the first point
    coord2: tuple of (lat2, lon2) for the second point

    Returns:
    Distance between the two coordinates in meters.
    """
    # Radius of the Earth in meters
    R = 6371000

    # Coordinates in radians
    coord1 = ast.literal_eval(coord1)
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0][0]), math.radians(coord2[0][0])

    # Differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in meters
    distance = R * c
    return distance


def find_closest_address(row, address_dict, metric):
    address_list_coords = [(address, address_dict[address][0]) for address in address_dict]

    current_coords = ast.literal_eval(row['coordinates'])
    if not current_coords:
        return None, None  # Handle missing coordinates

    closest_address = None
    min_distance = float('inf')

    # Compare the current address with each in the list
    for addr, coords in address_list_coords:
        if coords:
            distance = metric(current_coords, coords)  #
            if distance < min_distance:
                min_distance = distance
                closest_address = addr
    # print(closest_address, min_distance)
    return closest_address, min_distance


def calculate_direct_distance(origin, destination):
    return geodesic(origin, destination).kilometers


def calculate_walking_distance(origin, destination):
    # Request the distance matrix for walking mode
    try:
        result = gmaps.distance_matrix(origins=origin,
                                       destinations=destination,
                                       mode="walking")
        distance = result['rows'][0]['elements'][0]['distance']['value']
        return distance
    except:
        return float('inf')


def get_coordinates(address, retries=3):
    for i in range(retries):
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                return (location.latitude, location.longitude)

        except GeocoderTimedOut:
            print(f"Geocoder timed out for address: {address}. Retrying {i + 1}/{retries}...")
            time.sleep(2)  # Wait before retrying
    print(f"Failed to retrieve coordinates for address: {address}")
    return None


def rearrange_address(address):
    parts = address.split()  # Split by spaces
    # Assuming the last part is always the house number and first two parts are the city
    city = ' '.join(parts[:2])  # City is the first two words
    rest_of_address = ' '.join(parts[2:-1])  # Middle part (street name)
    house_number = parts[-1]  # House number (last part)
    new_address = f"{rest_of_address} {house_number} {city}"
    return new_address


def proccess_data(text):
    text = text.replace(" דרך ", " ")
    text = text.replace(" שדרות", "")
    text = text.replace("שמעון פרוג", "פרוג")
    text = text.replace("שלמה אבן גבירול", "אבן גבירול")
    text = text.replace("אליה", "אליהו")
    text = text.replace("אהרון בנימיני", "בנימיני")

    if "רמת גן" in text:
        text = rearrange_address(text)
    if "תל אביב-יפו" in text:
        text = rearrange_address(text)
    if "גבעתיים" in text:
        parts = text.split()  # Split by spaces
        city = ' '.join(parts[:1])  # City is the first two words
        rest_of_address = ' '.join(parts[1:-1])  # Middle part (street name)    return text
        house_number = parts[-1]  # House number (last part)
        text = f"{rest_of_address} {house_number} {city}"

    return text


def create_df_With_coordinates():
    df = pd.read_excel('df with addresses 21_sep.xlsx')
    df['addresses'] = df['addresses'].apply(lambda x: ast.literal_eval(x))
    df = df.dropna(axis='rows')

    # Keep only valid addresses
    df = df[df['addresses'].apply(lambda x: x != [])]
    df['address'] = df['addresses'].apply(lambda x: x[0])
    df = df[df['address'] != 'אין תוצאות']
    # print(df['address'])
    df['address'] = df['address'].apply(proccess_data)
    # print(df['address'])

    # Find coordinates once
    addresses = pd.DataFrame({'address': df['address'].unique().tolist()})

    # Get coordinates for each address
    coordinates = [get_coordinates(address) for address in addresses['address'].tolist()]
    addresses['coordinates'] = coordinates

    # apply the coordinates to all apartments
    df = df.merge(addresses, on=['address'])
    df.to_excel('df with addresses and coordinates.xlsx', index=False)


train_address = ["זאב אורלוב 70 פתח תקווה", 'זאב אורלוב 41 פתח תקווה', 'זאב אורלוב 8 פתח תקווה',
                 "ז'בוטינסקי 31 פתח תקווה", "ז'בוטינסקי 72 פתח תקווה", "ז'בוטינסקי 82 פתח תקווה",
                 "ז'בוטינסקי 101 פתח תקווה", "אמיל זולא 5 פתח תקווה", "ז'בוטינסקי 117 בני ברק",
                 "ז'בוטינסקי 166 בני ברק", "ז'בוטינסקי 12 בני ברק", "ז'בוטינסקי 3 בני ברק",
                 "ז'בוטינסקי 85 רמת גן", "ז'בוטינסקי 75 רמת גן", "ז'בוטינסקי 68 רמת גן", "אבא הלל 1 רמת גן",
                 "על פרשת דרכים 1 תל אביב יפו", "מנחם בגין 160 תל אביב", "שדרות מנחם בגין 125 תל אביב",
                 "מנחם בגין 144 תל אביב יפו", "מנחם בגין 112 תל אביב יפו", "שדרות מנחם בגין 98 תל אביב",
                 "אלוף אלברט מנדלר 38 תל אביב", "קרליבך/לינקולן", "קרליבך/מנחם בגין תל אביב", "יהודה הלוי 63",
                 "מקווה ישראל 10", "מקווה ישראל 47 תל אביב", "אהרון שלוש 7 תל אביב", "שדרות ירושלים 15 תל אביב-יפו",
                 "שדרות ירושלים 42 תל אביב-יפו", "שדרות ירושלים 94 תל אביב-יפו", "שדרות ירושלים 120 תל אביב-יפו",
                 "שדרות ירושלים 146 תל אביב-יפו", "שדרות ירושלים 210 תל אביב-יפו", "שדרות העצמאות 69 בת ים",
                 "רוטשילד 17 בת ים", "הרצל 64 בת ים", "יוספטל 44 בת ים", "יוספטל 70 בת ים", "יוספטל 82 בת ים",
                 "ניסנבאום 48 בת ים", "ניסנבאום 7 בת ים", "מנחם בגין 4 בת ים", "לינקולן 17, תל אביב-יפו"]

train_station_dict = {
    # Petah tikva
    'Petah Tikva CBS': [(32.094607, 34.886591)], 'Pinsker': [(32.093679, 34.882236)],
    'Krol': [(32.091869, 34.877537)], 'Dankner': [(32.090921, 34.872163)],
    'Beilinson': [(32.091413, 34.866798)], 'Shaham': [(32.091950, 34.861221)],
    'Shenkar': [(32.092654, 34.853257)], 'Kiryat Ary': [(32.105971, 34.862879)],
    # bneibrak
    'Gesher Em HaMoshavot': [(32.099220, 34.846380)], 'Aharonovich': [(32.092655, 34.838742)],
    'Ben Gurion': [(32.090972, 34.823586)],
    # ramat gan
    'Bialik': [(32.087254, 34.812820)],
    'Abba Hillel': [(32.082877, 34.802720)],
    # tlv
    'Arlosoroff': [(32.081479, 34.796526)],
    "Sha'ul HaMelekh": [(32.076626, 34.791928)], "Yehudit": [(32.070141, 34.788421)],
    "Carlebach": [(32.065198, 34.782893)], "Allenby": [(32.062731, 34.775103)],
    "Elifelet": [(32.058363, 34.763035)], "Shalma (Salame)": [(32.054320, 34.759477)],
    "Bloomfield Stadium": [(32.050211, 34.759011)], "Ehrlich": [(32.045708, 34.757293)],
    "Isakov": [(32.042132, 34.757049)], "HaBesht": [(32.038615, 34.755802)], "Mahrozet": [(32.033225, 34.751556)],
    # bat yam
    "Ha'Atsma'ut": [(32.028130, 34.748961)],
    "Rothschild": [(32.026659, 34.744413)], "Jabotinsky": [(32.021638, 34.743238)],
    "Balfour": [(32.017422, 34.744748)],
    "Binyamin": [(32.016328, 34.748458)], "Yoseftal": [(32.015495, 34.751456)],
    "Kaf Tet BeNovember": [(32.010777, 34.751539)], "He'Amal": [(32.005830, 34.748941)],
    "HaKomemiyut": [(32.002243, 34.746818)]
}


def get_min_distances(df, train_station_dict):
    df[['closest_direct_address', 'direct_distance_km']] = df.apply(
        lambda row: pd.Series(find_closest_address(row, train_station_dict, calculate_direct_distance)), axis=1)
    # df[['closest_walking_address', 'walking_distance_km']] = df.apply(
    #     lambda row: pd.Series(find_closest_address(row, train_station_dict, calculate_walking_distance)), axis=1)
    # print(df.head())
    df.dropna(inplace=False)
    df.to_excel('df with direct distances.xlsx', index=False)
    return df


def create_classes(distance):
    if distance >= 1.0:
        return '1000+'
    elif distance < 1.0 and distance >= 0.5:
        return '500-1000'
    else:
        return '0-500'


def create_group_columns(df):
    df['class'] = df['direct_distance_km'].apply(create_classes)
    df['sale_date'] = pd.to_datetime(df.sale_date, dayfirst=True)
    df['sale_year'] = df['sale_date'].apply(lambda x: x.year)
    df['sale_year_range'] = df['sale_year'].apply(lambda x: '21-22' if x <= 2022 else '23-24')
    df['subgroup'] = df['sale_year_range'] + ' - ' + df['class']

    df.to_excel('df with direct distances and subgroups.xlsx', index=False)

    sns.countplot(df, x="subgroup")
    plt.show()

def get_distances():
    """
    Runs code in order to get distances from light rail to scraped data.
    :return: none
    """
    geolocator = Nominatim(user_agent="einamlocs")
    gmaps = googlemaps.Client(key='')
    # client = openrouteservice.Client(key='einamlocs')

    # Create df with cooridinates:
    create_df_With_coordinates()

    # Create df with distances:
    df = pd.read_excel('df with addresses and coordinates.xlsx')
    print(df.columns)
    df = df.drop_duplicates()
    df = get_min_distances(df, train_station_dict)
    df = df.drop_duplicates()
    create_group_columns(df)
