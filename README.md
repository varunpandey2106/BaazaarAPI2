# BaazaarAPI2

BaazaarAPI2 is an E-commerce/E-Retail REST-API built using Django Rest Framework.
It has oauth powered social login, Notifications with Twilio and payment integration with Paystack.
It is an improved version of **[BaazaarAPI](https://github.com/varunpandey2106/BaazaarAPI.git)**




## Table of Contents

- [Project Name](#BaazaarAPI2)
  - [Technologies Used](#technologies-used)
  - [Features](#features)
  - [Getting Started](#getting-started)
    - [Installation](#installation)
  - [API Documentation](#api-documentation)
  - [Database](#database)
  - [Screenshots](#screenshots)
  - [Note](#Note)
  - [License](#license)
  


### Technologies Used

- **[Python](https://www.python.org/)**
- **[Django](https://www.djangoproject.com/)**
- **[Django Rest Framework](https://www.django-rest-framework.org/)**
- **[Postman](https://www.postman.com/)**
- **[Swagger](https://swagger.io/)**
- **[PostgreSQL](https://www.postgresql.org/)**
- **[Twilio](https://www.twilio.com/en-us)**
- **[Paystack](https://paystack.com/)**
- **[Django allauth](https://docs.allauth.org/en/latest/)**
- **[Docker](https://www.docker.com/)**
- **[Drawsql](https://drawsql.app/)**



## Features

- **User Management and Authentication**
- **Product Management**
- **Shopping Cart Management**
- **Notifications**
- **Payment Integration**
- **Third party Integrations**



## Getting Started

### Installation

**1. Clone the repository:**

```bash
git clone https://github.com/varunpandey2106/BaazaarAPI2.git
cd BaazaarAPI2
code .
```

**2. Install dependencies:**

```python
cd BaazaarAPI2
virtualenv venv
pip install -r requirements.txt
```


**3. Start the project:**
   
```python
python manage.py runserver
```

**4. access at:**
-***http://127.0.0.1:8000/***
-***https://baazaarapi2-1.onrender.com/***



## API DOCUMENTATION:
**Visit https://baazaarapi2-1.onrender.com/swagger/ for API documentation** 
**Will add a Postman collection soon!**




## Database:
-**Create a postgres database and configure project settings, the schema architecture is as follows:**
![Screenshot 2023-10-22 232420](https://github.com/varunpandey2106/DReactDashboard/assets/77747699/39cb8e2d-f133-4321-8b59-e5440b4121a6)
-**For development on my local machine, I used Postgres, for deployment, I used Railway.**

##  Note:
-**This API has been deployed on the free tier of render. It has production and service lags,it might shut down in the future, hence I have added a screenrecording of the relevant workflow.Twilio was successfully implemented in **[BaazaarAPI](https://github.com/varunpandey2106/BaazaarAPI.git)** but unfortunately I am out of free credits. However, the code is open for usage and I have added screenshots.**

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

