# Supply Chain Digital Twin – Database Schema

## 1. Suppliers
Stores supplier information.

- supplier_id (Primary Key)
- supplier_name
- location
- average_lead_time_days
- reliability_score

## 2. Warehouses
Stores warehouse information.

- warehouse_id (Primary Key)
- warehouse_name
- location
- capacity

## 3. Retailers
Stores retailer information.

- retailer_id (Primary Key)
- retailer_name
- location

## 4. Products
Stores product information.

- product_id (Primary Key)
- product_name
- category
- unit_price
- supplier_id (Foreign Key)

## 5. Inventory
Tracks stock at warehouses and retailers.

- inventory_id (Primary Key)
- product_id (Foreign Key)
- warehouse_id (Foreign Key, nullable)
- retailer_id (Foreign Key, nullable)
- quantity
- reorder_point
- safety_stock

## 6. Orders
Stores customer and replenishment orders.

- order_id (Primary Key)
- product_id (Foreign Key)
- source_type
- source_id
- destination_type
- destination_id
- quantity
- order_date
- expected_delivery_date
- status

## 7. Shipments
Tracks product movements.

- shipment_id (Primary Key)
- order_id (Foreign Key)
- shipped_date
- expected_arrival_date
- actual_arrival_date
- status

## 8. Demand History
Stores historical product demand.

- demand_id (Primary Key)
- product_id (Foreign Key)
- retailer_id (Foreign Key)
- demand_date
- quantity_sold