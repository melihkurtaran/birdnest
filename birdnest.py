import requests
import xml.etree.ElementTree as ET

# URL for the snapshot endpoint
snapshot_url = "https://assignments.reaktor.com/birdnest/drones"


# Send a GET request to the snapshot endpoint
response = requests.get(snapshot_url)

# Parse the XML data
root = ET.fromstring(response.text)

# Extract the drone information from the XML data
drones = []
for drone in root.findall("./capture/drone"):
    serial_number = drone.find("serialNumber").text
    x = float(drone.find("positionX").text)
    y = float(drone.find("positionY").text)
    drones.append({"serial_number": serial_number, "x": x, "y": y})

# Calculate the distance of each drone from the NDZ perimeter
ndz_x = 250000
ndz_y = 250000
ndz_radius = 100000 # limit is 100 meter

from flask import Flask, render_template
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

# URL for the snapshot endpoint
snapshot_url = "https://assignments.reaktor.com/birdnest/drones"

# URL for the registry endpoint
registry_url = "https://assignments.reaktor.com/birdnest/pilots/{serial_number}"

@app.route('/')
def index():
    # Send a GET request to the snapshot endpoint
    response = requests.get(snapshot_url)

    # Parse the XML data
    root = ET.fromstring(response.text)

    # Extract the drone information from the XML data
    drones = []
    for drone in root.findall("./capture/drone"):
        serial_number = drone.find("serialNumber").text
        x = float(drone.find("positionX").text)
        y = float(drone.find("positionY").text)
        drones.append({"serial_number": serial_number, "x": x, "y": y})

    # Calculate the distance of each drone from the NDZ perimeter
    ndz_x = 250000
    ndz_y = 250000
    ndz_radius = 100000 # limit is 100 meter
    for drone in drones:
        x = drone["x"]
        y = drone["y"]
        distance = ((x - ndz_x) ** 2 + (y - ndz_y) ** 2) ** 0.5
        drone["distance"] = distance

    # Filter the drones to only include those that have violated the NDZ
    violators = [drone for drone in drones if drone["distance"] < ndz_radius]
    
    # Query the registry endpoint for each violator and extract the pilot information
    pilots = []
    for drone in violators:
        serial_number = drone["serial_number"]
        url = registry_url.format(serial_number=serial_number)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            first_name = data["firstName"]
            last_name = data["lastName"]
            name = first_name + " " + last_name  # Concatenate first and last names
            email = data["email"]
            phone = data["phoneNumber"]
            pilots.append({"name": name, "email": email, "phone": phone, "distance": round(drone["distance"]/1000.0,2)})
        #Please note on a rare occasion pilot information may not be found, indicated by a 404 status code.
        if response.status_code == 404:
            print("There is a violation but the violator is UNKNOWN!")


    # Generate the HTML for the user interface
    html = "<html><head><title>NDZ Violations</title></head><body>"
    html += "<h1>NDZ Violations</h1>"

    # Add a table to display the violator information
    html += "<table>"
    html += "<tr><th>Name</th><th>Email</th><th>Phone</th><th>Distance (m)</th></tr>"

    # Add a row for each violator
    for pilot in pilots:
        html += "<tr>"
        html += f"<td>{pilot['name']}</td>"
        html += f"<td>{pilot['email']}</td>"
        html += f"<td>{pilot['phone']}</td>"
        html += f"<td>{pilot['distance']}</td>"
        html += "</tr>"

    html += "</table>"
    html += "</body></html>"

    # Display the HTML
    print(html)

