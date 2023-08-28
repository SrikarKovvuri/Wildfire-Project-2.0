# app.py
from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

# Define a function that converts Degree Minute Second (DMS) format to Decimal Degrees.
def dms_to_decimal(dms_str):
    """
    Convert a string in DMS format (like '44 13 19.5') to a decimal number.
    
    Parameters:
        dms_str (str): The string containing the DMS representation.
    
    Returns:
        float: The decimal representation of the DMS value.
    """
    # Determine if the input is negative
    negative = False
    if "-" in dms_str:
        negative = True
        dms_str = dms_str.replace("-", "")
    
    # Extract all the numbers (degrees, minutes, seconds) from the input string.
    parts = list(map(float, re.findall(r"[\d.]+", dms_str)))

    # Convert DMS to Decimal based on the number of extracted parts.
    decimal_val = 0
    if len(parts) == 3:  # degrees, minutes, seconds
        decimal_val = parts[0] + parts[1]/60 + parts[2]/3600
    elif len(parts) == 2:  # degrees, minutes
        decimal_val = parts[0] + parts[1]/60
    else:  # just degrees
        decimal_val = parts[0]

    return -decimal_val if negative else decimal_val

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-wildfires-data')
def data():
    # URL of the RSS feed containing wildfire incidents.
    url = "https://inciweb.nwcg.gov/incidents/rss.xml"
    # Fetch the XML content from the URL using the requests library.
    response = requests.get(url)
    # Parse the fetched XML using BeautifulSoup.
    soup = BeautifulSoup(response.content, 'xml')
    # Extract all the items (or incidents) from the XML.
    items = soup.find_all('item')
    # Initialize an empty list to store information about wildfires.
    wildfires = []
    
    # Loop through each item to extract relevant information.
    for item in items:
        # Get the title of the incident (name of the fire).
        title = item.title.text
        # Get the detailed description of the incident.
        description = item.description.text
        # Check if the incident type is a Wildfire.
        if "The type of incident is Wildfire" in description:
            # Extract latitude and longitude from the description using regex.
            latitude_match = re.search(r"Latitude:\s*([\d\s.]+)", description)
            longitude_match = re.search(r"Longitude:\s*([-]?[\d\s.]+)", description)
            # Convert the regex match to a string or assign None if not found.
            latitude_str = latitude_match.group(1).strip() if latitude_match else None
            longitude_str = longitude_match.group(1).strip() if longitude_match else None
            # If both latitude and longitude are found, convert them from DMS to Decimal format.
            if latitude_str and longitude_str:
                try:
                    latitude = dms_to_decimal(latitude_str)
                    longitude = dms_to_decimal(longitude_str)
                    # Append the wildfire details to the list.
                    wildfires.append({
                        'title': title,
                        'latitude': latitude,
                        'longitude': longitude
                    })
                except Exception as e:
                    # If there's an error in conversion, skip that entry.
                    pass
                
    return jsonify(wildfires)

if __name__ == '__main__':
    app.run(debug=True)
