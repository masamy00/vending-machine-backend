# Vending Machine End-Points
- postman collection to manually test the APIs
- file "FLapKap.postman_collection.json"
## Introduction
- REST API Server for vending machine operation
- The server only allows request methods [GET, POST, PUT, DELETE]
- The server only allows Content-Type : application/json
## Base URL

The server will run on port 3000
- http://localhost:3000

## Authentication

- Except /users (POST)  to create a user
- All the APIs requires 2 main headers
  1. User-Id : the user primary key which will return while creation
  2. Password : the user password

## Endpoints

### /users (GET) 
- Retrieve list of all users

### /users (POST) 
- Add new user
- body parameter
  - json object with keys
    - username (string)
    - role (string) - should be in (seller, buyer)
    - password (string)

### /users/{user_id} (PUT) 
- update user information
- body parameter
  - json object with keys
    - id (int) - should represent user id (primary key)
    - username (string)
    - role (string) - if the role changed from seller to buyer all the products of the user will be deleted
    - password (string)

### /users/{user_id} (DELETE) 
- delete a user
- if the user has "seller" role all the products of the user will be deleted also

### /products (GET) 
- Retrieve list of all products

### /products (POST) 
- Add new product
- only user with role "seller" can request
- body parameter
  - json object with keys
    - productName (string)
    - amountAvailable (integer) - should be in (seller, buyer)
    - cost (integer) - must be a number dividable by 5

### /products/{products_id} (PUT) 
- update product information
- body parameter
  - json object with keys
    - productName (string)
    - amountAvailable (integer) - should be in (seller, buyer)
    - cost (integer) - must be a number dividable by 5
  
### /products/{products_id} (DELETE) 
- delete a product
- only the seller of the product can remove

### /deposit (POST)
- perform deposit operation for user with buyer role
- json object with keys
    - depositAmount (integer) - must be in [5, 10, 20, 50, 100]

### /buy (GET, POST)
- perform purchase operation for user with buyer role
- json list of object - each object must have two keys
    - productId (integer) - represent a product id (primary key)
    - amount (integer) - qty of the product

### /reset (POST)
- perform reset operation for user with buyer role


