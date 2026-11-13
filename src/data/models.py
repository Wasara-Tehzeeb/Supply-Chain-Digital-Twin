from sqlalchemy import Integer, String, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from datetime import date
from sqlalchemy import Date

class Base(DeclarativeBase):
    pass


class Supplier(Base):
    __tablename__ = "suppliers"


    __table_args__ = (
        CheckConstraint(
            "average_lead_time_days >= 0",
            name="ck_supplier_lead_time_nonnegative"
        ),
        CheckConstraint(
            "reliability_score >= 0 AND reliability_score <= 1",
            name="ck_supplier_reliability_range"
        ),
    )

    supplier_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    supplier_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    location: Mapped[str] = mapped_column(
        String(150), nullable=False
    )

    average_lead_time_days: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    reliability_score: Mapped[float] = mapped_column(
        Float, nullable=False
    )


class Warehouse(Base):
    __tablename__ = "warehouses"

    __table_args__ = (
        CheckConstraint(
            "capacity >= 0",
            name="ck_warehouse_capacity_nonnegative"
        ),
    )

    warehouse_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    warehouse_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    location: Mapped[str] = mapped_column(
        String(150), nullable=False
    )

    capacity: Mapped[int] = mapped_column(
        Integer, nullable=False
    )


class Retailer(Base):
    __tablename__ = "retailers"

    retailer_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    retailer_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    location: Mapped[str] = mapped_column(
        String(150), nullable=False
    )


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        CheckConstraint(
            "unit_price >= 0",
            name="ck_product_price_nonnegative"
        ),
    )

    product_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    product_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    unit_price: Mapped[float] = mapped_column(
        Float, nullable=False
    )

    supplier_id: Mapped[int] = mapped_column(
        ForeignKey("suppliers.supplier_id"),
        nullable=False
    )


class Inventory(Base):
    __tablename__ = "inventory"


    __table_args__ = (
        CheckConstraint(
            "(warehouse_id IS NOT NULL AND retailer_id IS NULL) OR "
            "(warehouse_id IS NULL AND retailer_id IS NOT NULL)",
            name="ck_inventory_single_location"
        ),
        CheckConstraint(
            "quantity >= 0",
            name="ck_inventory_quantity_nonnegative"
        ),
        CheckConstraint(
            "reorder_point >= 0",
            name="ck_inventory_reorder_nonnegative"
        ),
        CheckConstraint(
            "safety_stock >= 0",
            name="ck_inventory_safety_nonnegative"
        ),
    )

    inventory_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.product_id"),
        nullable=False
    )

    warehouse_id: Mapped[int | None] = mapped_column(
        ForeignKey("warehouses.warehouse_id"),
        nullable=True
    )

    retailer_id: Mapped[int | None] = mapped_column(
        ForeignKey("retailers.retailer_id"),
        nullable=True
    )

    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    reorder_point: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    safety_stock: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

class Order(Base):
    __tablename__ = "orders"


    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_order_quantity_positive"
        ),
        CheckConstraint(
            "expected_delivery_date >= order_date",
            name="ck_order_delivery_date"
        ),
        CheckConstraint(
            "source_type IN ('supplier', 'warehouse')",
            name="ck_order_source_type"
        ),
        CheckConstraint(
            "destination_type IN ('warehouse', 'retailer')",
            name="ck_order_destination_type"
        ),
        CheckConstraint(
            "source_id > 0 AND destination_id > 0",
            name="ck_order_location_ids"
        ),
        CheckConstraint(
            "status IN ('pending', 'shipped', 'delivered', 'cancelled')",
            name="ck_order_status"
        ),
    )


    order_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.product_id"),
        nullable=False
    )

    source_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )

    source_id: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    destination_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )

    destination_id: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    order_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )

    expected_delivery_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30), nullable=False
    )


class Shipment(Base):
    __tablename__ = "shipments"

    __table_args__ = (
        CheckConstraint(
            "expected_arrival_date >= shipped_date",
            name="ck_shipment_expected_arrival"
        ),
        CheckConstraint(
            "actual_arrival_date IS NULL OR actual_arrival_date >= shipped_date",
            name="ck_shipment_actual_arrival"
        ),
        CheckConstraint(
            "status IN ('in_transit', 'delivered', 'delayed', 'cancelled')",
            name="ck_shipment_status"
        ),
    )

    shipment_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.order_id"),
        nullable=False
    )

    shipped_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )

    expected_arrival_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )

    actual_arrival_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30), nullable=False
    )


class DemandHistory(Base):
    __tablename__ = "demand_history"

    __table_args__ = (
        CheckConstraint(
            "quantity_sold >= 0",
            name="ck_demand_quantity_nonnegative"
        ),
    )

    demand_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.product_id"),
        nullable=False
    )

    retailer_id: Mapped[int] = mapped_column(
        ForeignKey("retailers.retailer_id"),
        nullable=False
    )

    demand_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )

    quantity_sold: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
