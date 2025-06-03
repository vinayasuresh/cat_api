from sqlalchemy import Column, String, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ZipCode2Dataset(Base):
    __tablename__ = 'zipcode2_dataset'

    zip_code = Column(String, primary_key=True, index=True)  # Renamed from 'zip' to 'zip_code' for clarity
    usps_city_name = Column(String)  # Official USPS city name
    usps_state_code = Column(String, index=True)  # Official USPS State Code
    state_name = Column(String, index=True)  # Official State Name
    zcta = Column(Boolean)
    zcta_parent = Column(String, nullable=True)
    population = Column(Float)  # Using Float as it's more flexible for large numbers
    density = Column(Float)
    primary_county_code = Column(String, index=True)  # Primary Official County Code
    primary_county_name = Column(String)  # Primary Official County Name
    county_weights = Column(JSON)  # Store the JSON object for county weights
    county_names = Column(String)  # Official County Names as comma-separated list
    county_codes = Column(String, index=True)  # Official County Codes as comma-separated list
    imprecise = Column(Boolean)
    military = Column(Boolean)
    timezone = Column(String)
    geo_point = Column(String)  # Lat/Long as a string

    def __repr__(self):
        return f"<ZipCode2Dataset(zip_code='{self.zip_code}', city='{self.usps_city_name}', state='{self.usps_state_code}')>"
