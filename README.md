# Python-APIs
Use REST APIs with Flask and Python

Working with a virtual environment:
- virtualenv venv --python=python3.8
- source venv/bin/activate

Packages required:
- Flask
- Flask-JWT-Extended
- Flask-SQLAlchemy
- Flask-RESTful
- Marshmallow
- Flask-Marshmallow
- Marshmallow-SQLAchemy

With this APIs you can:
- Create (register) Users. Get all the creatd Users, get a User by ID, delete a User by ID
- Login and Logout
- Create Stores. Get all the created Stores, get a store by name, delete a store by name
- Create Items for a sotre. Get all the created Items, get an itme by name, delete an item by name

When running python3 app.py, a database called "data.bd" will be generated with the required tables. 
All the information from the APIs wil be stored and retrieved from the tables.

API collection added as: "APIs.postman_collection.json"
