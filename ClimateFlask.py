import numpy as np
import datetime as dt
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

###########################

# Database Setup

###########################
engine=create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

###########################
# Flask Setup
###########################
app = Flask(__name__)

###########################

# Flask Routes

###########################
@app.route("/")
def welcome():
    """List all available routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start> and /api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # return query results
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    last_year = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > year_ago).\
        order_by(Measurement.date).all()

    session.close()
    # create a dictionary using date as key and prcp as values
    prcp_results = []
    for prcp, date in last_year:
        prcp_one = {}
        prcp_one["date"] = date
        prcp_one["prcp"] = prcp
        prcp_results.append(prcp_one)

    return jsonify (prcp_results)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # return list of stations
    stations1 = session.query(Measurement.station).all()
    
    session.close()

    # jsonify
    all_stations = list(np.ravel(stations1))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # return list of temperature and dates for the busiest station
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    busiest_station2 = most_active_stations[0][0]

    station_temp = session.query(Measurement.date, Measurement.tobs).group_by(Measurement.date).\
        filter(Measurement.station == busiest_station2).\
        filter(Measurement.date <= '2017-08-23').filter(Measurement.date >= '2016-08-24').all()

    session.close()

    # jsonify
    station_temp = list(np.ravel(station_temp))

    return jsonify(station_temp)


@app.route("/api/v1.0/<start>")
def start(start_date):
    # Create our session(link) from Python to the DB
    session = Session(engine)
    # calc_temps function
    calc_temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).all()

    session.close()

    start = list.append(np.ravel(calc_temps))

    return jsonify (start)



@app.route("/api/v1.0/<start>/<end>")

def start_end(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    calc_temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()

    session.close()

    start_end = list.append(np.ravel(calc_temps))

    return jsonify (start_end)


if __name__ == "__main__":
    app.run(debug=True)