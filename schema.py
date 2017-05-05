"""
Schema for the STReserve application.

:Author:     Maded Batara III
:Version:    v20170503
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///:memory:', echo=True)
Base = declarative_base()

class Chemical(Base):
    """
    Defines the table `chemicals`, describing the attributes of a chemical
    stored in the laboratory.
    
    Columns:
        id (Integer, primary_key): ID of chemical.
        name (String): Name of chemical.
        state (Integer): Chemical's current state of matter. 1 for liquid,
            2 for solid.
        qty: Amount of chemical left in storage, in milliliters (for liquid 
            chemicals) and grams (for solid chemicals).
    """
    __tablename__ = 'chemicals'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    state = Column(Integer)
    qty = Column(Integer)

class Equipment(Base):
    """
    Defines the table `equipment`, describing the attributes of glasswares/
    supplies/apparatus/equipment stored in the laboratory.
    
    Columns:
        id (Integer, primary_key): ID of equipment
        name (String): Name of chemical.
        is_consumable (Boolean): True if  
        qty: Number of equipment left in storage.
    """
    __tablename__ = 'equipment'

    id = Column(Integer, primary_key=True) 
    name = Column(String)
    is_consumable = Column(Boolean)
    qty = Column(Integer)

class ChemicalLog(Base):
    __tablename__ = 'chemical_log'

    id = Column(Integer, primary_key=True):
    group_code = Column(Integer)
    reserved_id = Column(Integer)
    time_procured = Column(DateTime)

class EquipmentLog(Base):
    __tablename__ = 'equipment_log'

    id = Column(Integer, primary_key=True):
    group_code = Column(Integer)
    reserved_id = Column(Integer)
    time_procured = Column(DateTime)
    time_returned = Column(DateTime)

    