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
#  home route - shows available routes (and instructions for dynamic routes)
@app.route("/")
def home():
    """List all the available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
        f"Please input dates as YYYYMMDD. Dates should be between 20100101 and 20170823."
    )


# precipitation route - precip for final year of dataset
@app.route("/api/v1.0/precipitation")

# Convert the query results from precipitation analysis to a dictionary
def precipitation():

    # set up latest date/first date
    latest_date = dt.date(2017,8,23)
    first_date = latest_date - dt.timedelta(days=365)

    # Query measurement
    precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= first_date).order_by(Measurement.date).all()

     # Convert results into dictionary
    precip_dict = {}
    for eachrow in precip:
        precip_dict[eachrow[0]] = eachrow[1]

    session.close()

    return jsonify(precip_dict)


# stations route - list of all stations
@app.route("/api/v1.0/stations")

def stations():
    sta = session.query(Station.station).all()
    sta_list = list(np.ravel(sta))
    session.close()
    return sta_list


# tobs route - temp data for final year of dataset
@app.route("/api/v1.0/tobs")
def tobs():
    # set up latest date/first date
    latest_date = dt.date(2017,8,23)
    first_date = latest_date - dt.timedelta(days=365)

    # Query
    temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station=="USC00519281").\
    filter(Measurement.date >= first_date).all()

    temp_dict = {}
    for eachrow in temp:
        temp_dict[eachrow[0]] = eachrow[1]

    session.close()

    return jsonify(temp_dict)


# dynamic start date tobs route - user picks start date, returns temp stats for start date to end date of dataset
@app.route("/api/v1.0/<start>")
def tobs_start(start):

    # make the string into a date
    first_date = dt.date(int(start[0:4]),int(start[4:6]),int(start[6:]))

    # mark start/end dates of dataset
    data_start = dt.date(2010,1,1)
    data_end = dt.date(2017,8,23)

    # make sure the date is within range
    if(first_date >= data_start and first_date <= data_end):
        temp_agg = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
            filter(Measurement.date >= first_date)
        
        # save stats
        min_temp = temp_agg[0][0]
        max_temp = temp_agg[0][1]
        avg_temp = temp_agg[0][2]

        results_dict = {"min temp": min_temp, "max temp": max_temp, "avg temp": avg_temp}

        session.close()

        return jsonify(results_dict)

    else: return jsonify({f"error: date is either in the wrong format, or does not exist in the data's date range.", 404})


# dynamic start/end date tobs route - user picks start and end date, returns temp stats for that range
@app.route("/api/v1.0/<start>/<end>")
def tobs_start_end(start,end):

    # make the strings into a date
    start_date = dt.date(int(start[0:4]),int(start[4:6]),int(start[6:]))
    end_date = dt.date(int(end[0:4]),int(end[4:6]),int(end[6:]))

    # mark start/end dates of dataset
    data_start = dt.date(2010,1,1)
    data_end = dt.date(2017,8,23)

    # make sure the dates are within range
    if(start_date >= data_start and start_date <= data_end and end_date >= data_start and end_date <= data_end):
        temp_agg = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
            filter((Measurement.date >= start_date) & (Measurement.date <= end_date))
        
        # save stats
        min_temp = temp_agg[0][0]
        max_temp = temp_agg[0][1]
        avg_temp = temp_agg[0][2]

        results_dict = {"min temp": min_temp, "max temp": max_temp, "avg temp": avg_temp}

        session.close()

        return jsonify(results_dict)

    else: return jsonify({f"error: one of the dates is either in the wrong format, or does not exist in the data's date range.", 404})


if __name__ == "__main__":
    app.run(debug=True)