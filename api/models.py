from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, VARCHAR
from sqlalchemy import Column, Float, Text, DateTime, Date, null

from uuid import uuid4


db = SQLAlchemy()

class Position(db.Model):
    """DB model for location tracking."""

    __tablename__ = "raw_location_tracking"

    location_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_time = Column(DateTime, nullable=False)
    shipment_number = Column(Text, nullable=False)

    def __init__(self, latitude, longitude, location_time, shipment_number):
        self.latitude = latitude
        self.longitude = longitude
        self.location_time = location_time
        self.shipment_number = shipment_number

    @property
    def serialize(self) -> dict:
        """For transforming object data into serializable format."""

        return {
            "location_uuid": self.location_uuid,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_time": self.location_time,
            "shipment_number": self.shipment_number
        }

class Shipment(db.Model):
    """DB model for shipments tracking.
    
    Returns:
        Dict: Dictionary of row values.
    """

    __tablename__ = "raw_shipments_tracking"

    shipment_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    shipment_number = Column(Text, nullable=False)
    collection_postcode = Column(VARCHAR(10), nullable=False)
    delivery_postcode = Column(VARCHAR(10), nullable=False)
    booking_date = Column(Date, nullable=False)
    scheduled_collection_date = Column(Date, nullable=False)
    scheduled_delivery_date = Column(Date, nullable=False)
    first_collection_schedule_earliest = Column(DateTime, nullable=False)
    first_collection_schedule_latest = Column(DateTime, nullable=False)
    last_delivery_schedule_earliest = Column(DateTime, nullable=False)
    last_delivery_schedule_latest = Column(DateTime, nullable=False)
    vehicle_type = Column(Text, nullable=False)
    delivered_at = Column(DateTime, nullable=True, default=None)

    def __init__(
        self,
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
        vehicle_type,
        delivered_at
    ):
        self.shipment_number = shipment_number
        self.collection_postcode = collection_postcode
        self.delivery_postcode = delivery_postcode
        self.booking_date = booking_date
        self.scheduled_collection_date = scheduled_collection_date
        self.scheduled_delivery_date = scheduled_delivery_date
        self.first_collection_schedule_earliest = first_collection_schedule_earliest
        self.first_collection_schedule_latest = first_collection_schedule_latest
        self.last_delivery_schedule_earliest = last_delivery_schedule_earliest
        self.last_delivery_schedule_latest = last_delivery_schedule_latest
        self.vehicle_type = vehicle_type
        self.delivered_at = delivered_at

    @property
    def serialize(self) -> dict:
        """For transforming object data into serializable format.
        
        Returns:
            Dict: Dictionary of row values.
        """

        return {
            "shipment_uuid": self.shipment_uuid,
            "shipment_number": self.shipment_number,
            "collection_postcode": self.collection_postcode,
            "delivery_postcode": self.delivery_postcode,
            "booking_date": self.booking_date,
            "scheduled_collection_date": self.scheduled_collection_date,
            "scheduled_delivery_date": self.scheduled_delivery_date,
            "first_collection_schedule_earliest": self.first_collection_schedule_earliest,
            "first_collection_schedule_latest": self.first_collection_schedule_latest,
            "last_delivery_schedule_earliest": self.last_delivery_schedule_earliest,
            "last_delivery_schedule_latest": self.last_delivery_schedule_latest,
            "vehicle_type": self.vehicle_type,
            "delivered_at": self.delivered_at
        }

    @property
    def was_delivered_on_time(self):
        """For determining if the shipment was delivered on time.
        
        Returns:
            Bool: True if delivered on time, otherwise False (including if not yet delivered).
        """

        if self.delivered_at:
            if self.delivered_at < self.last_delivery_schedule_latest:
                return True
            else:
                return False
        else:
            return False

if __name__ == "__main__":
    print(1)