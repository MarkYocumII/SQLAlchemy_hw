import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread':False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session=Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/START_DATE<br/>"
        f"/api/v1.0/start_date/end_date/START_DATE/END_DATE<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitatin values for each date"""
    # Query all passengers
    results = session.query(Measurement).all()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_precip = []
    for measurement in results:
        precip_dict = {}
        precip_dict[f"{measurement.date}"] = measurement.prcp
        all_precip.append(precip_dict)

    return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of all temperatures in the past year"""
    # Query all measurements and find latest date
    date_result = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #convert to string and remove special characters
    latest_date = str(date_result).strip("')''(','")

    #convert latest date to datetime format
    latest_date= dt.datetime.strptime(latest_date, "%Y-%m-%d")
    
    # Perform a query to retrieve the data and precipitation scores
    #identify start date for query from 12 months (365 days) prior
    query_date = latest_date - dt.timedelta(days=365)

    #create query statement for all dates and precipation totals within last year
    temp_dates = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > query_date).all()

    # Convert list of tuples into normal list
    all_temps = list(np.ravel(temp_dates))

    return jsonify(all_temps)

@app.route("/api/v1.0/start_date/<start_date>")
def calc_temps(start_date):
#When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
    temp_list = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    return jsonify(temp_list)

@app.route("/api/v1.0/start_date/end_date/<start_date>/<end_date>")
def calc_both_temps(start_date, end_date):
#When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
    
    temp_list_both = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date < end_date).all()
    return jsonify(temp_list_both)

if __name__ == '__main__':
    app.run(debug=True)

