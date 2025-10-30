# MVC Event Management System  
  
  This project is a web-based platform for organizing and managing events such as conferences, workshops and concerts. It allows administrators to manage events and users to register as attendees. This syetem is built using the Django framework, following MVC (Model-View-Control) architectural principles.  

## Getting Started
These instructions will get you a copy of the project, up and running on your local machine for development and testing purposes.  

### Prerequisities
+ Python (3.8 or higher)
+ Git
+ VS Code (Or any other IDE of your choice)

### Installation
1. Clone the repository:  
```
git clone https://github.com/Faith-Ncube/MVC-Event-Management-System.git
```

2. Install the required packages:  
```
pip install -r requirements.txt
```

3. Apply the database migrations:  
+ This will create the database file (`db.sqlite3`) and set up all the necessary tables.  
```
python manage.py makemigrations
```

```
python manage.py migrate
```  

### Running the Developemt Server
Once  the setup is complete, you can run the local development server:  

```
python manage.py runserver
```

The server will start, and then will be able to access the system in your web browser at `http://127.0.0.1:8000/`.  

### Testing the API (Tata's Work)
The project includes a set of API endpoints for interacting with the event data programatically. You can test these endpoints in your browser.  

**Note:** If the database is new, these endpoints will corresctly return empty lists (`[]`) because no data has been created yet. This is expected behaviour.  

#### Available Endpoints
You can test the following `GET` request by navigating to these URLs in your browser. 

1. **List All Events**  
+ **URL:** `https://127.0.0.1:8000/api/events/`
+ **Method:** `GET`
+ **Purpose:** Returns a list of all events in the system

2. **Retrieve a Single Event**  
+ **URL:** `https://127.0.0.1:8000/api/events/1/`
+ **Method:** `GET`
+ **Purpose:** Returns the detailed information for a single event with the specified ID

3. **List Attendees  for an Event**  
+ **URL:** `https://127.0.0.1:8000/api/events/1/attendees/`
+ **Method:** `GET`
+ **Purpose:** Returns a list of all attendees for a specific event.