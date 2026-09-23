from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Farmer(Base):
    __tablename__ = "farmers"

    farmer_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    phone_number: Mapped[str] = mapped_column(String(30))
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    preferred_language: Mapped[str | None] = mapped_column(String(30), nullable=True)
    farms: Mapped[list["Farm"]] = relationship(back_populates="farmer")


class Farm(Base):
    __tablename__ = "farms"

    farm_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    farmer_id: Mapped[int | None] = mapped_column(ForeignKey("farmers.farmer_id"), nullable=True)
    farm_name: Mapped[str] = mapped_column(String(120))
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    crop: Mapped[str | None] = mapped_column(String(100), nullable=True)
    device_id: Mapped[str] = mapped_column(String(50))
    farmer: Mapped[Farmer | None] = relationship(back_populates="farms")
    readings: Mapped[list["SensorReading"]] = relationship(back_populates="farm")


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    __table_args__ = (Index("ix_sensor_readings_farm_timestamp", "farm_id", "timestamp"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farm_id: Mapped[str] = mapped_column(ForeignKey("farms.farm_id"), index=True)
    device_id: Mapped[str] = mapped_column(String(50))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    soil_moisture: Mapped[float] = mapped_column(Float)
    soil_ph: Mapped[float] = mapped_column(Float)
    temperature: Mapped[float] = mapped_column(Float)
    humidity: Mapped[float] = mapped_column(Float)
    light: Mapped[float] = mapped_column(Float)
    rain_detected: Mapped[bool] = mapped_column(Boolean)
    water_level: Mapped[float] = mapped_column(Float)
    pump_status: Mapped[bool] = mapped_column(Boolean)
    farm: Mapped[Farm] = relationship(back_populates="readings")


class IrrigationEvent(Base):
    __tablename__ = "irrigation_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farm_id: Mapped[str] = mapped_column(ForeignKey("farms.farm_id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    duration_seconds: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(500))
    pump_status: Mapped[bool] = mapped_column(Boolean)
    command_id: Mapped[str | None] = mapped_column(String(80), nullable=True, unique=True)
    farm: Mapped[Farm] = relationship()

    @property
    def duration_sec(self) -> int:
        return self.duration_seconds


class SMSLog(Base):
    __tablename__ = "sms_logs"
    __table_args__ = (Index("ix_sms_logs_farm_timestamp", "farm_id", "timestamp"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    farm_id: Mapped[str] = mapped_column(ForeignKey("farms.farm_id"), index=True)
    recipient: Mapped[str] = mapped_column(String(30))
    message: Mapped[str] = mapped_column(String(1000))
    status: Mapped[str] = mapped_column(String(30))
    provider_status: Mapped[str | None] = mapped_column(String(80), nullable=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)