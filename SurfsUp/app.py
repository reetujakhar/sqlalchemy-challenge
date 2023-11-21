# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import datetime as dt
from datetime import timedelta
from flask import Flask, jsonify
import json

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
## Flask Routes
#################################################
@app.route("/")

def home():
    """All available Routes"""
    return(
        "All available Routes:<br/><br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/&lt;start&gt;<br/>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

## Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
## Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Calculate the date one year ago

    most_recent_date = session.query(func.max(Measurement.date)).scalar()

    last_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date()
    one_year_ago = last_date - timedelta(days=365)

    # Query for the last 12 months of precipitation data

    precipitation_data = session.query(Measurement.date,Measurement.prcp)\
    .filter(Measurement.date >= one_year_ago)\
    .order_by(Measurement.date.desc())\
    .all()

    # Convert the query results to a dictionary
    precipitation_dict = {str(date): prcp for date, prcp in precipitation_data}

    # Return the JSON representation of the dictionary
    json_representation = json.dumps(precipitation_dict, indent=4)
    print(json_representation)
    
    session.close()
    return jsonify(precipitation_dict)


## Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():

    # Query all stations
    stations = session.query(Station).all()

    
    station_list = [{'station_id': st.station,
                 'station_name': st.name,
                 'latitude': st.latitude,
                 'longitude': st.longitude,
                 'elevation': st.elevation} for st in stations]
    
    # Return the JSON representation of the list
    json_representation = json.dumps(station_list, indent=4)
    print(json_representation)
    
    session.close()
    return jsonify(station_list)


## Query the dates and temperature observations of the most-active station for the previous year of data.
## Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
   
   # Query to find the most active stations
   most_active_stations = session.query(Measurement.station, func.count(Measurement.station))\
    .group_by(Measurement.station)\
    .order_by(func.count(Measurement.station).desc())
   
   # Calculate the date one year ago
   most_recent_date = session.query(func.max(Measurement.date)).scalar()
   
   last_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date()
   one_year_ago = last_date - timedelta(days=365)

   # Query dates and temperature observations for the most active station for the previous year

   temperature_data = session.query(Measurement.date,Measurement.tobs)\
    .filter(Measurement.station == most_active_stations.first()[0], Measurement.date >= one_year_ago)\
    .all()
   
   # Convert the query results to a list of dictionaries
   
   temperature_list = [{'date': str(date), 'temperature': tobs} for date, tobs in temperature_data]

   # Return the JSON representation of the list
   json_representation = json.dumps(temperature_list, indent=4)
   print(json_representation)

   session.close()
   return jsonify(temperature_list)


## Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
## For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
## For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>")
def temp_start(start):

    # Query minimum, average, and maximum temperatures for the specified date range

    temperature_values = session.query(
    func.min(Measurement.tobs).label('min_temperature'),
    func.max(Measurement.tobs).label('max_temperature'),
    func.avg(Measurement.tobs).label('avg_temperature')
    ).filter(Measurement.date >= start)
    
     # Convert the query result to a dictionary
    temperature_values_list = [{"minTemp": tempdata.min_temperature, "maxTemp": tempdata.max_temperature, "avgTemp": tempdata.avg_temperature} for tempdata in temperature_values]   
     
     # Return the JSON representation of the dictionary
    session.close()
    return jsonify(temperature_values_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start,end):

     # Query minimum, average, and maximum temperatures for the specified date range

    temperature_values = session.query(
    func.min(Measurement.tobs).label('min_temperature'),
    func.max(Measurement.tobs).label('max_temperature'),
    func.avg(Measurement.tobs).label('avg_temperature')
    ).filter(Measurement.date >= start).filter(Measurement.date <= end)
    
    # Query minimum, average, and maximum temperatures for the specified date range
    temperature_values_list = [{"minTemp": tempdata.min_temperature, "maxTemp": tempdata.max_temperature, "avgTemp": tempdata.avg_temperature} for tempdata in temperature_values]   
     
     # Return the JSON representation of the dictionary
    session.close()
    return jsonify(temperature_values_list)

if __name__ == "__main__":
    app.run(debug=True)
  