from sqlalchemy import Column, String, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ZipCodeDataset(Base):
    __tablename__ = 'zipcode_dataset'

    zip = Column(String, primary_key=True, index=True)
    lat = Column(Float)
    lng = Column(Float)
    city = Column(String)
    state_id = Column(String, index=True)
    state_name = Column(String, index=True)
    zcta = Column(Boolean)
    parent_zcta = Column(String, nullable=True)
    population = Column(Float)  # Using Float as it's more flexible for large numbers
    density = Column(Float)
    county_fips = Column(String, index=True)
    county_name = Column(String, index=True)
    county_weights = Column(JSON)  # Store the JSON object for county weights
    county_names_all = Column(String)  # Storing as pipe-separated values
    county_fips_all = Column(String)  # Storing as pipe-separated values
    imprecise = Column(Boolean)
    military = Column(Boolean)
    timezone = Column(String)

    def __repr__(self):
        return f"<ZipCodeDataset(zip='{self.zip}', city='{self.city}', state='{self.state_name}')>"
