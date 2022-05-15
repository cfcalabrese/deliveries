from flask import Flask, jsonify, request, Response
from models import db, Position, Shipment
from pandas import DataFrame, to_datetime
from numpy import where
import yaml

from pathlib import Path
from datetime import datetime
from re import sub


cwd = Path(__file__).parent.resolve()
cfg_path = fr"{cwd}/config.yaml"

with open(cfg_path) as f:
    cfg = yaml.safe_load(f)
    username = cfg['POSTGRES']['USERNAME']
    password = cfg['POSTGRES']['PASSWORD']
    db_host = cfg['POSTGRES']['POSTGRES_HOST']
    db_port = cfg['POSTGRES']['POSTGRES_PORT']
    db_name = cfg['POSTGRES']['POSTGRES_DB']

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    fr"postgresql://{username}:{password}@{db_host}:{db_port}/{db_name}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db.init_app(app)

@app.route("/api/location_tracking", methods=["GET"])
def all_tracking_data() -> Response:
    """Function for handling GET requests to see all shipment tracking data."""

    try:
        positions = Position.query.all()
        response = {
            "status": "success",
            "data": [pos.serialize for pos in positions]
        }

    except Exception as e:
        error_msg = "Error: " + str(e)
        response = {
            "status": "failure",
            "message": f"{error_msg}"
        }

    return jsonify(response)

@app.route("/api/location_tracking/<shipment_number>", methods=["GET", "POST"])
def singular_location_tracking(shipment_number: str) -> Response:
    """Function for handling GET requests to retrieve single shipment locations
    and POST requests for new shipment coordinates.
    """

    if request.method == "GET":
        try:
            positions = Position.query.filter_by(
                shipment_number=shipment_number
            ).order_by(Position.location_time)

            response = {
                "status": "success",
                "data": [pos.serialize for pos in positions]
            }

        except Exception as e:
            error_msg = "Error: " + str(e)
            response = {
                "status": "failure",
                "message": f"{error_msg}"
            }

    elif request.method == "POST":
        try:
            post_data = request.get_json()
            new_record = Position(
                shipment_number=shipment_number,
                **post_data
            )

            db.session.add(new_record)
            db.session.commit()

            response = {
                "status": "success",
                "record_added": new_record.serialize
            }

        except Exception as e:
            error_msg = "Error: " + str(e)
            response = {
                "status": "failure",
                "message": f"{error_msg}"
            }

    return jsonify(response)

@app.route("/api/shipments_tracking", methods=["GET", "POST"])
def all_shipments_data() -> Response:
    """Function for handling GET requests to retrieve all shipments
    and handling POST requests to add new shipments.
    """

    if request.method == "GET":
        try:
            shipments = Shipment.query.all()
            response = {
                "status": "success",
                "data": [shipment.serialize for shipment in shipments]
            }

        except Exception as e:
            error_msg = "Error: " + str(e)
            response = {
                "status": "failure",
                "message": f"{error_msg}"
            }
    
    elif request.method == "POST":
        try:
            post_data = request.get_json()
            new_record = Shipment(**post_data)
            db.session.add(new_record)
            db.session.commit()
            response = {
                "status": "success",
                "message": new_record.serialize
            }

        except Exception as e:
            error_msg = "Error: " + str(e)
            response = {
                "status": "failed",
                "message": f"{error_msg}"
            }

    return jsonify(response)

@app.route("/api/shipments_tracking/<shipment_number>", methods=["GET"])
def singular_shipment_tracking(shipment_number: str) -> Response:
    """Function for handling GET requests to retrieve data on single shipments."""

    try:
        shipments = Shipment.query.filter_by(
            shipment_number=shipment_number
        ).order_by(
            Shipment.booking_date,
            Shipment.scheduled_collection_date
        )

        response = {
            "status": "success",
            "data": [shipment.serialize for shipment in shipments]
        }
        
    except Exception as e:
        error_msg = "Error: " + str(e)
        response = {
            "status": "failure",
            "message": f"{error_msg}"
        }
    
    return jsonify(response)

@app.route("/api/shipments_tracking/<shipment_number>", methods=["PATCH"])
def mark_as_delivered(shipment_number: str) -> Response:
    """Sends an update to mark a given shipment as delivered,
    with timestamp of the CURRENT date and time.
    """

    try:
        # delivered at is set as the moment in which the
        # PATCH request is sent.
        delivered_at = datetime.now()
        shipment_to_update = Shipment.query.filter_by(
            shipment_number=shipment_number
        ).first()

        shipment_to_update.delivered_at = delivered_at
        db.session.commit()
        response = {
            "status": "success",
            "message": f"""
                {shipment_to_update.shipment_number} 
                delivered at {delivered_at}.
            """
        }

    except Exception as e:
        error_msg = "Error: " + str(e)
        response = {
            "status": "failure",
            "message": f"{error_msg}"
        }

    return jsonify(response)


@app.route("/api/delivered_on_time", methods=["GET"])
def weekly_delivered_on_time() -> Response:
    """Calculates the percentage of shipments delivered
    on in each week.
    """
    try:
        delivered_shipments = Shipment.query.filter(
            Shipment.delivered_at != None
        )

        delivered_dict = [s.serialize for s in delivered_shipments]
        delivered_df = DataFrame(data=delivered_dict)
        delivered_df["scheduled_delivery_week"] = delivered_df[
            "scheduled_delivery_date"
        ].apply(
            lambda x: to_datetime(x).strftime('%Y-w%W')
        )

        delivered_df["delivered_on_time"] = where(
            delivered_df.delivered_at <= delivered_df.last_delivery_schedule_latest,
            1,
            0
        )

        # total no. deliveries
        grouped_count = delivered_df[[
            "scheduled_delivery_week",
            "delivered_on_time"
        ]].groupby(
            "scheduled_delivery_week"
        ).count()

        # total no. deliveries on time
        grouped_sum = delivered_df[[
            "scheduled_delivery_week",
            "delivered_on_time"
        ]].groupby(
            "scheduled_delivery_week"
        ).sum()

        # calculation for percentage of shipments delivered on time
        # 100 * (no. deliveries on time)/(total deliveries)
        grouped_df = 100 * grouped_sum / grouped_count

        # reset index and delete unused dfs
        grouped_df.reset_index(inplace=True)
        del grouped_sum
        del grouped_count

        response = {
            "status": "success",
            "data": grouped_df.to_dict(orient="records")
        }

    except Exception as e:
        error_msg = "Error: " + str(e)
        response = {
            "status": "failure",
            "message": f"{error_msg}"
        }

    return jsonify(response)

@app.route("/api/delivery_groups/", methods=["GET"])
def calculate_delivery_groups():
    all_undelivered_shipments = Shipment.query.filter(
        Shipment.delivered_at == None
    )

    all_undelivered_shipments = [
        s.serialize for s in all_undelivered_shipments
    ]

    for v in all_undelivered_shipments:

        # extract with outcode from the delivery postcode
        # e.g. the outcode for the postcode DG16 5HT
        # would be DG16
        v["collection_outcode"] = v["collection_postcode"].split(" ")[0]

        # extracting the delivery area from the delivery postcode
        # e.g. the delivery area for the postcode DG16 5HT
        # would be DG
        v["delivery_area"] = sub(r"\d+", "", v["delivery_postcode"].split(" ")[0])
        

    # unique vehicle types
    vehicle_types = set(
            v["vehicle_type"] for v in all_undelivered_shipments
    )

    # unique collection outcodes
    coll_outcodes = set(
            v["collection_outcode"] for v in all_undelivered_shipments
    )

    # unique delivery areas
    del_areas = set(
            v["delivery_area"] for v in all_undelivered_shipments
    )

    # unique scheduled collection days
    coll_days = set(
        v["scheduled_collection_date"] for v in all_undelivered_shipments
    )

    delivery_groups = []
    for day in coll_days:
        filtered_by_day = list(
            filter(lambda d: d["scheduled_collection_date"] ==\
                day, all_undelivered_shipments
            )
        )
        for outcode in coll_outcodes:
            filtered_by_outcode = list(
                filter(lambda d: d["collection_outcode"] ==\
                    outcode, filtered_by_day
                )
            )

            for vehicle_type in vehicle_types:
                filtered_by_vt = list(
                    filter(lambda d: d["vehicle_type"] ==\
                        vehicle_type, filtered_by_outcode
                    )
                )

                for area in del_areas:
                    filtered_by_area = list(
                        filter(lambda d: d["delivery_area"] ==\
                            area, filtered_by_vt
                        )
                    )

                    if len(filtered_by_area) > 0:
                        shipment_dict = {
                            str(day): {
                                outcode: {
                                    vehicle_type: {
                                        area: filtered_by_area
                                    }
                                }
                            }
                        }

                        delivery_groups.append(shipment_dict)

                    else:
                        pass      
    
    response = {
        "status": "success",
        "test": delivery_groups,
    }

    return jsonify(response)

if __name__ == "__main__":
    app.run()