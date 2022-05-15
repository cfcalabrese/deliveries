-- Inserting csv data into tables
-- GPS tracking
create temporary table temp_raw_location_tracking (
    latitude numeric not null,
    longitude numeric not null,
    location_time timestamp not null,
    shipment_number text not null
);

copy temp_raw_location_tracking from '/pgdata/tracking.csv' delimiter ',' csv header;

insert into raw_location_tracking (
	latitude,
	longitude,
	location_time,
	shipment_number
)
select
	*
from
	temp_raw_location_tracking;

drop table temp_raw_location_tracking;
-------------------------------------------------------------------------------------------
-- Shipments
create temporary table temp_raw_shipments_tracking (
    shipment_number text not null,
	collection_postcoode varchar(10) not null,
    delivery_postcode varchar(10) not null,
    booking_date date not null,
	scheduled_collection_date date not null,
    scheduled_delivery_date date not null,
    first_collection_schedule_earliest timestamp not null,
    first_collection_schedule_latest timestamp not null,
    last_delivery_schedule_earliest timestamp not null,
    last_delivery_schedule_latest timestamp not null,
    vehicle_type text not null
);

copy temp_raw_shipments_tracking from '/pgdata/shipments.csv' delimiter ',' csv header;

insert into raw_shipments_tracking (
	shipment_number,
    collection_postcode,
    delivery_postcode,
    booking_date,
    scheduled_collection_date,
    scheduled_delivery_date,
    first_collection_schedule_earliest,
    first_collection_schedule_latest,
    last_delivery_schedule_earliest,
    last_delivery_schedule_latest,
    vehicle_type
)
select 
	*
from
	temp_raw_shipments_tracking;

drop table temp_raw_shipments_tracking;