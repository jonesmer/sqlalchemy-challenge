# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all the available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")

# Convert the query results from precipitation analysis to a dictionary
def precipitation():

    # set up latest date/first date
    latest_date = dt.date(2017,8,23)
    first_date = latest_date - dt.timedelta(days=365)

    # Query measurement
    precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= first_date)

     # Convert list of tuples into normal list
    precip_list = list(np.ravel(precip))
    return jsonify(precip_list)

@app.route("/api/v1.0/stations")
def stations():
    sta = session.query(Station.station)

    return jsonify(sta)

@app.route("/api/v1.0/tobs")
def tobs():
    # set up latest date/first date
    latest_date = dt.date(2017,8,23)
    first_date = latest_date - dt.timedelta(days=365)

    # Query
    temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station=="USC00519281").\
    filter(Measurement.date >= first_date)

    temp_list = list(np.ravel(temp))
    return jsonify(temp_list)

# @app.route("/api/v1.0/<start>")
# def tobs_start(start_date):


# @app.route("/api/v1.0/<start>/<end>")