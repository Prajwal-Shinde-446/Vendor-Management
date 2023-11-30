# Vendor-Management

## Table of Contents

1. Overview
2. Setup Instructions
3. Login Info
4. Authentication
5. Api endpoints

## Overview ##
Develop a Vendor Management System using Django and Django REST Framework. This
system will handle vendor profiles, track purchase orders, and calculate vendor performance
metrics.

## Setup Instructions ##

1. Clone the Repository:
git clone https://github.com/Prajwal-Shinde-446/Vendor-Management.git

2. Install Dependencies:

navigate to project use command -> cd vendor_management

Install the following
pip install Django
pip install restframework
pip install curl
# note the commands to install dependencies might differ as per the subsystem being used #

## Note
There are two ways to perform operations you can choose as per your convinience

## 1. Using Django Dashboard
Alternatively, you can perform these operations through the Django Dashboard:

1. Navigate to the Django admin interface (usually available at http://127.0.0.1:8000/admin/ or http://127.0.0.1:8000/).
2. Log in with your superuser credentials.(The LOGIN credentials are give below)
3. Access the respective sections for Vendors or Purchase Orders.
4. Use the provided forms and interfaces to create, update, or delete records.

## 2. Using `curl` from Shell Terminal using Endpoints mentioned below
You can interact with the API by making HTTP requests using `curl` from your shell terminal.



## LOGIN INFO ##
username = prajwal
password = Draken446

## Authentication Token ##
2e5bcf26f6067f61696005fd5958bfbc83f90ede


## Example request
curl -X GET http://127.0.0.1:8000/api/protected-endpoint/ -H "Authorization: 2e5bcf26f6067f61696005fd5958bfbc83f90ede"


## API ENDPOINTS ##

## Vendor Requests

## 1. Get a List of Vendors Details:
curl -X GET http://127.0.0.1:8000/api/vendors/ -H "Authorization: Token your_superuser_token_here" 

## 2. Get Details of a Specific Vendor by Using Vendor Code as PK:
curl -X GET http://127.0.0.1:8000/api/vendors/vendor_code_here/ -H "Authorization: Token your_superuser_token_here"

## 3. Create a Vendor:
curl -X POST http://127.0.0.1:8000/api/vendors/ -H "Content-Type: application/json" -H "Authorization: Token your_superuser_token_here" -d '{"name": "New Vendor", "contact_details": "Contact Info", "address": "Vendor Address"}'

## 4. Update an Existing Vendor:
curl -X PATCH http://127.0.0.1:8000/api/vendors/vendor_code_here/ -H "Content-Type: application/json" -H "Authorization: Token your_superuser_token_here" -d '{"name": "Updated Vendor Name"}'

## 5. Delete a Vendor:
curl -X DELETE http://127.0.0.1:8000/api/vendors/vendor_code_here/ -H "Authorization: Token your_superuser_token_here"

## 6. To Get Performance Metrices
curl -X GET http://127.0.0.1:8000/api/vendors/vendor_code_here/performance/ -H "Authorization: Token your_superuser_token_here"

## Purchase Order Requests

## 1. Get a List of Purchase Orders:
curl -X GET http://127.0.0.1:8000/api/purchase_orders/ -H "Authorization: Token your_superuser_token_here"

## 2. Get Details of a Specific Purchase Order by Using PO Number as PK:
curl -X GET http://127.0.0.1:8000/api/purchase_orders/po_number_here/ -H "Authorization: Token your_superuser_token_here"

## 3. Create a Purchase Order:
curl -X POST http://127.0.0.1:8000/api/purchase_orders/ -H "Content-Type: application/json" -H "Authorization: Token your_superuser_token_here" -d '{"vendor": 1, "order_date": "2023-01-01", "delivery_date": "2023-01-10", "items": [{"name": "Item1", "quantity": 5}], "quantity": 5, "status": "Pending"}'

## 4. Update an Existing Purchase Order:
curl -X PATCH http://127.0.0.1:8000/api/purchase_orders/po_number_here/ -H "Content-Type: application/json" -H "Authorization: Token your_superuser_token_here" -d '{"status": "Completed", "quality_rating": 4.5}'

## 5. Delete an Existing Purchase Order
curl -X DELETE http://127.0.0.1:8000/api/purchase_orders/po_number_here/ -H "Authorization: Token your_superuser_token_here"

## 6. Request to Acknowledge a Purchase Order
curl -X POST http://localhost:8000/api/purchase_orders/po_number_here/acknowledge/ -H "Authorization: Token your_superuser_token_here"


