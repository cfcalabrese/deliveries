drop extension if exists "uuid-ossp";
create extension if not exists "uuid-ossp";

-- Creation of raw_shipments_tracking table
create table if not exists raw_shipments_tracking (
    shipment_uuid uuid default uuid_generate_v4 () primary key,
    shipment_number text not null,
    collection_postcode varchar(10) not null,
    delivery_postcode varchar(10) not null,
    booking_date date not null,
    scheduled_collection_date date not null,
    scheduled_delivery_date date not null,
    first_collection_schedule_earliest timestamp not null,
    first_collection_schedule_latest timestamp not null,
    last_delivery_schedule_earliest timestamp not null,
    last_delivery_schedule_latest timestamp not null,
    vehicle_type text not null,
    delivered_at timestamp default null
);

-- Creation of raw_location_tracking table
create table if not exists raw_location_tracking (
    location_uuid uuid default uuid_generate_v4 () primary key,
    latitude numeric not null,
    longitude numeric not null,
    location_time timestamp not null,
    shipment_number text not null
);