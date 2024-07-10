# Import the dependencies.
from flask import Flask, jsonify
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
import datetime


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation_orm<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>" 
        f"/api/v1.0/start/end<br/>"
        f"Date should be in this format (08272017)"
    )
@app.route('/api/v1.0/precipitation_orm')
def passengers_orm():
    prev_year = datetime.date(2016, 8, 23)
    prec = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).order_by(Measurement.date.asc())
    session.close()
    precipitation = {date: prcp for date, prcp in prec}
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def passengers_raw():
    results = session.query(Measurement.station, func.count(Measurement.id).label('num_stations')) \
                 .group_by(Measurement.station) \
                 .order_by(func.count(Measurement.id).desc()) \
                 .all()
    session.close()
    stations = list(np.ravel(results))
    return jsonify(stations)

# start should be in format 2016-08-23
@app.route("/api/v1.0/tobs")
def tobs_start_orm():
    results1 = session.query(func.min(Measurement.tobs).label('min_value'),
                            func.max(Measurement.tobs).label('max_value'),
                            func.avg(Measurement.tobs).label('avg_value')).filter(Measurement.station == 'USC00519281').one()
    session.close()
    tobs = list(np.ravel(results1))
    return jsonify(tobs)

# start should be in format 2016-08-23
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def tobs_start_end_raw(start = None, end = None):
    query = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    if not end:
        start = datetime.datetime.strptime(start, "%m%d%Y")
        results = session.query(*query).filter(Measurement.date >= start).all()
        session.close()
        starts = list(np.ravel(results))
        return jsonify(starts)
    start = datetime.datetime.strptime(start, "%m%d%Y")
    end = datetime.datetime.strptime(end, "%m%d%Y")
    results = session.query(*query).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    starts = list(np.ravel(results))
    return jsonify(starts)

# Run the App
if __name__ == '__main__':
    app.run(debug=True)