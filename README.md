# District Temp Ranker Documentation

District Temp Ranker is a FastAPI project that provides APIs for retrieving information about the coolest districts and offering travel advice based on temperature comparisons.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Running the Project](#running-the-project)
- [API Endpoints](#api-endpoints)
  - [1. Get Coolest Districts](#1-get-coolest-districts)
  - [2. Travel Advice](#2-travel-advice)

## Getting Started

### Prerequisites

Before running the project, ensure you have the following prerequisites installed:

- **Python 3.7+**: You need Python installed on your system.
- **Pip (Python package manager)**: You'll use pip to install project dependencies.

### Installation

To install the DistrictTempRanker project and its dependencies, follow these steps:

1. Clone the project repository:

   ```bash
   git clone https://github.com/your/project.git
   cd DistrictTempRanker
   pip install -r requirements.txt
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   The project will start, and the APIs will be accessible at http://localhost:8000
## API Endpoints
### 1. Get Coolest Districts
  - URL: /coolest-districts
  - HTTP Method: GET
  - Description: Retrieve the ten coolest districts based on average temperature.
  - Parameters: None
### 2. Travel Advice
  - URL: /travel-advice
  - HTTP Method: GET
  - Description: Get travel advice based on temperature comparisons.
  - Parameters:
    - user_longitude (float): Longitude of the user's location.
    - user_latitude (float): Latitude of the user's location.
    - destination_longitude (float): Longitude of the travel destination.
    - destination_latitude (float): Latitude of the travel destination.
    - travel_date (str): Date of travel in YYYY-MM-DD format.

## Documentation
  -  http://localhost:8000/docs

