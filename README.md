# SCM: Supply Chain Management Project

## Introduction
This is a Supply Chain Management Project for managing and optimize 

## Main Features
- **Order management:** entering and updating orders, and real-time tracking of order statuses.
- **Inventory management:** monitoring stock levels, automated low-stock alerts to prevent shortages.
- **Demand forecasting:** forecasting module using statistical and machine learning models to predict future inventory needs.
- **Employee management:** including admin, warehouse staff and sales staff, with role-based access control and action history tracking optimized for fast-checking.
- **Reporting and visualization:** basic and effecective staffs' dashboard for KPIs, data visualizations for quick decision-making.
- **AI-Powered Product Entry (Auto Detect):** Add a deep learning model (PyTorch) to automatically detect the item. Users simply upload a product image and click 'Auto Detect' button, the result will auto-fill the product name.
## Technology Stack 
- **Language:** Python 3.11
- **Web Framework:** Django
- **Database:** PostgreSQL
- **AI & Data:** pandas, numpy, scikit-learn, statsmodels, matplotlib, pytorch

## Getting Started (Docker Setup)
To run this project locally, ensure you have Docker and Docker Desktop installed.

1. **Clone the repository and navigate to the project directory:**
   git clone github.com/hbduy03/SCM
   cd inventorySystem
2. **Start the system using Docker Compose:**
  docker-compose up --build -d
3. **Run database migrations:**
  docker-compose exec web python manage.py migrate
4. **Create a superuser account for the Admin dashboard:**
  docker-compose exec web python manage.py createsuperuser
5. Access the application:
Open your browser and navigate to http://localhost:8000 or http://localhost:8000/admin.

## Project Structure
<img width="212" height="401" alt="image" src="https://github.com/user-attachments/assets/24d7e173-5094-4b01-9061-b94f1f798d11" />

  ## Demo Website
<table>
  <tr>
    <td align="center">
      <b>Add Product (Auto Detect feature) </b><br>
      <img src="https://github.com/user-attachments/assets/022a1213-4230-47a0-a105-6669e6180098" alt="Add Product">
    </td>
    <td align="center">
      <b>Product List</b><br>
      <img src="https://github.com/user-attachments/assets/502b1263-e572-48e7-b111-50f208fd0cb1" alt="Product List">
    </td>
    <td align="center">
      <b>Deactivated Product List</b><br>
      <img src="https://github.com/user-attachments/assets/a7e6b0bf-8678-43c0-9c41-a22a322125db" alt="Deactivated Product List">
    </td>
  </tr>

  <tr>
    <td colspan="3" align="center">
      <b>Inventory Tracking</b><br>
      <img src="https://github.com/user-attachments/assets/d9d7429a-232b-4105-b5a0-c15a0ee32171" alt="Inventory Tracking">
    </td>
  </tr>

  <tr>
    <td align="center">
      <b>Stock In List</b><br>
      <img src="https://github.com/user-attachments/assets/c0972dac-47e1-46c4-b080-affb6cef7c71" alt="Stock In List">
    </td>
    <td align="center">
      <b>Stock In Detail</b><br>
      <img src="https://github.com/user-attachments/assets/a75cf7e8-4ea4-4529-a44d-a648a2d619ba" alt="Stock In Detail">
    </td>
    <td align="center">
      <b>Print Receipt</b><br>
      <img src="https://github.com/user-attachments/assets/45b69d79-8d80-4b61-b9ae-8ebac5478923" alt="Print Receipt">
    </td>
  </tr>

  <tr>
    <td align="center">
      <b>Stock Out List</b><br>
      <img width="1911" height="925" alt="image" src="https://github.com/user-attachments/assets/7090bec9-b317-4674-bdd0-6e8f8dfdb41a" />
    </td>
    <td align="center">
      <b>Stock Out Detail</b><br>
      <img width="1917" height="918" alt="image" src="https://github.com/user-attachments/assets/72a44ec0-f9a6-4e3c-992e-1d23786b3b87" />
    </td>
    <td align="center">
      <b>Print Receipt</b><br>
      <img width="1908" height="914" alt="image" src="https://github.com/user-attachments/assets/39e1a3a6-06e4-409f-896d-e1237e5a680d" />
    </td>
  </tr>


  <tr>
    <td align="center">
      <b>Order list</b><br>
      <img width="1919" height="847" alt="image" src="https://github.com/user-attachments/assets/530a53bc-0e52-4004-86e3-775b5ad67b23" />
    </td>
    <td align="center">
      <b>Order Details</b><br>
      <img width="1911" height="922" alt="image" src="https://github.com/user-attachments/assets/bfaf42d2-b47e-4ffe-8750-7c62827f7a55" />
    </td>
    <td align="center">
      <b>Print Receipt</b><br>
      <img width="1913" height="911" alt="image" src="https://github.com/user-attachments/assets/ccb3e8ff-f681-48a0-be03-6a348659dc39" />
    </td>
    </tr>
  </tr>
    <tr>
    <td colspan="3" align="center">
      <b> Admin dashboard (Demand focecasting and data visualizations) </b><br>
      <img width="1912" height="913" alt="image" src="https://github.com/user-attachments/assets/805e7c33-1077-4b96-9aac-70fc7e070da0" />
    </td>
  </tr>
      <tr>
    <td colspan="3" align="center">
     <img width="1918" height="919" alt="image" src="https://github.com/user-attachments/assets/9175dedf-f415-4227-bad9-cdca65f00f69" />
    </td>
  </tr>
<tr>
    <td align="center">
      <b>Staff List</b><br>
      <img width="1919" height="917" alt="image" src="https://github.com/user-attachments/assets/d24d7da2-029e-4a56-b948-4ab5acedb0b2" />
    </td>
    <td colspan="2" align="center">
      <b>Staff's action history tracking</b><br>
      <img width="1916" height="917" alt="image" src="https://github.com/user-attachments/assets/73e6b189-bcbd-4f79-bb75-a07cef4eebb1" />
    </td>
  </tr>

<tr>
    <td align="center">
      <b>User profile</b><br>
      <img width="1915" height="898" alt="image" src="https://github.com/user-attachments/assets/49f9e35e-e0ad-4a7a-bc26-3b4371777292" />
    </td>
    <td colspan="2" align="center">
      <b>Change password
      </b><br>
<img width="1919" height="910" alt="image" src="https://github.com/user-attachments/assets/2f14947c-4f13-489e-a9a8-afb357bbe565" />
    </td>
  </tr>

</table>
