# Import the dependencies.
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from flask import Flask, jsonify

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
# Define routes
@app.route("/")
def home():
    """Homepage - List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert query results to a dictionary and return JSON representation."""
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    station_list = [station[0] for station in results]
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query temperature observations of the most-active station for the previous year."""
    session = Session(engine)

    # Find the most active station
    most_active_station = session.query(Measurement.station)\
                                 .group_by(Measurement.station)\
                                 .order_by(func.count(Measurement.station).desc())\
                                 .first()[0]

    # Calculate the date one year from the last date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query temperature observations
    results = session.query(Measurement.date, Measurement.tobs)\
                     .filter(Measurement.station == most_active_station)\
                     .filter(Measurement.date >= one_year_ago)\
                     .all()

    session.close()

    tobs_data = [{"Date": date, "Temperature": tobs} for date, tobs in results]
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    """Calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date."""
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs).label("min_temp"),
                            func.avg(Measurement.tobs).label("avg_temp"),
                            func.max(Measurement.tobs).label("max_temp"))\
                    .filter(Measurement.date >= start)\
                    .all()

    session.close()

    temp_stats = {"TMIN": results[0][0], "TAVG": results[0][1], "TMAX": results[0][2]}
    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def temp_stats_range(start, end):
    """Calculate TMIN, TAVG, and TMAX for the specified start and end date range."""
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs).label("min_temp"),
                            func.avg(Measurement.tobs).label("avg_temp"),
                            func.max(Measurement.tobs).label("max_temp"))\
                    .filter(Measurement.date >= start)\
                    .filter(Measurement.date <= end)\
                    .all()

    session.close()

    temp_stats = {"TMIN": results[0][0], "TAVG": results[0][1], "TMAX": results[0][2]}
    return jsonify(temp_stats)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)