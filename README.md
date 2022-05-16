# DigiHaul
## Setup Instructions

1.  Extract contents of zip
2.  Open terminal and navigate to the project directory:
        `cd <path>/digihaul`
3.  Run the following command to build and run the containers:
        `docker-compose up --build`
4.  The database can be accessed with an SQL editor:
    host: localhost
    port: 5432
    database: digihaul
    username: postgres
    password: postgres

## Question 1
1.  The location tracking data feeds through to the API and can be viewed by\
    navigating to `http://localhost:5000/api/location_tracking`, whilst the\
    shipments data can be viewed at `http://localhost:5000/api/shipments_tracking`.
2.  Individual shipments can be tracked by navigating to
        `http://localhost:5000/api/location_tracking/<shipment_number>`
    and
        `http://localhost:5000/api/shipments_tracking/<shipment_number>`
3.  Data can be ingested by sending POST requests to the previous two URLs.\
    This can be done by opening a bash terminal and running, for example,
    to send a new set of coordinates for the `shipment_number` `SEZHUK-201218-000183`:
        ```
        {
            curl -X POST \
                -H 'Content-Type:application/json' \
                -d '{"location_time":"Thu, 28 Jan 2021 09:08:00 GMT", "latitude": 100.00, "longitude": 100.00}' \
                http://localhost:5000/api/location_tracking/SEZHUK-201218-000183
        }
        ```
    This POST request will also write the new data to the database.

    For adding new data to the shipments tracking data, a similar procedure can be followed.
    For example, to add a new shipment:
        ```
        {
            curl -X POST \
                -H 'Content-Type:application/json' \
                -d '{"booking_date":"Thu, 28 Jan 2021 09:08:00 GMT", "collection_postcode": "DG16 TEST", "delivery_postcode": "EH54 TEST", "first_collection_schedule_earliest":"Wed, 06 Jan 2021 14:00:00 GMT", "first_collection_schedule_latest":"Wed, 06 Jan 2021 16:00:00 GMT", "last_delivery_schedule_earliest":"Thu, 07 Jan 2021 06:30:00 GMT", "last_delivery_schedule_latest":"Thu, 07 Jan 2021 07:00:00 GMT", "scheduled_collection_date":"Wed, 06 Jan 2021 00:00:00 GMT", "scheduled_delivery_date":"Thu, 07 Jan 2021 00:00:00 GMT", "shipment_number":"TEST", "vehicle_type":"Tractor Unit / Curtain side", "delivered_at":null}' \
                http://localhost:5000/api/shipments_tracking
        }
        ```
    Further, to mark a particular `shipment_number` as having been delivered, a PATCH request can be sent to 
    `http://localhost:5000/api/shipments_tracking/<shipment_number>`. For example:
        `curl -X PATCH http://localhost:5000/api/location_tracking/TEST`

## Question 2
1.  Shipments are grouped together based on their collection date, then their outcode 
    (e.g. DG16 would be the outcode for the postcode DG16 5HT), then by vehicle type, 
    and then by delivery area (e.g. DG would be the area for postcode DG16 5HT).
    To see these aggregations, you can send a GET request to `http://localhost:5000/api/delivery_groups`
    or simply navigate to the address in a browser.
2.  To see the ratio of deliveries that arrived on time, send a GET request to 
    `http://localhost:5000/api/delivered_on_time`.