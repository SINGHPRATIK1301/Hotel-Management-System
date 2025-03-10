# Hotel-Management-System
A comprehensive desktop application for managing hotel operations, built with Python and Tkinter.

## Features

### 1. Room Management
- Add, update, and remove rooms
- View room status and details
- Book rooms for guests
- Track room availability

### 2. Booking Management
- Create new bookings
- View booking history
- Search bookings by customer name
- Track check-in and check-out dates

### 3. Billing System
- Generate bills for bookings
- Calculate taxes and discounts
- Generate payment QR codes
- Create and save invoices
- Multiple payment methods (Cash, Credit Card, QR Code)

### 4. Staff Management
- Add and manage staff members
- Process staff salaries
- Track salary history
- Manage staff status and details

### 5. Hotel Services
- Request hotel services (cleaning, laundry, food, etc.)
- Manage service catalog
- Track service requests
- View service history

### 6. Reports & Analytics
- Weekly analytics
- Monthly analytics
- Booking trends
- Revenue analysis
- Occupancy rates

## Requirements

### Python Version
- Python 3.6 or higher

### Required Libraries
```
tkinter (built-in)
sqlite3 (built-in)
qrcode==7.4.2
Pillow==10.0.0
```

## Installation

1. Clone the repository or download the source code
2. Install the required libraries:
```bash
pip install qrcode pillow
```

## Database Structure

The system uses SQLite database with the following tables:

1. `rooms`
   - Room details and availability
   - Room types and rates

2. `bookings`
   - Guest booking information
   - Check-in/out dates
   - Total amounts

3. `bills`
   - Billing information
   - Payment details
   - Tax and discount calculations

4. `services`
   - Hotel service catalog
   - Service prices and categories

5. `service_requests`
   - Service request tracking
   - Request status and details

6. `staff`
   - Staff member information
   - Employment details

7. `salary_payments`
   - Staff salary records
   - Payment history

8. `analytics`
   - System analytics data
   - Performance metrics

## File Structure

```
HMS/
├── hms.py              # Main application file
├── hotel.db           # SQLite database file
└── README.md          # This file
```

## Usage

1. Run the application:
```bash
python hms.py
```

2. Use the sidebar navigation to access different features:
   - Room Management
   - Booking History
   - Billing System
   - Staff Management
   - Services
   - Reports & Analytics

## Features in Detail

### Room Management
- Add new rooms with details (number, type, rate)
- Update room information
- Remove rooms from the system
- Book rooms for guests
- Track room availability status

### Booking System
- Create new bookings with guest details
- View and search booking history
- Track check-in and check-out dates
- Calculate booking amounts

### Billing System
- Generate bills for completed bookings
- Apply tax rates (10%)
- Add discounts
- Generate payment QR codes
- Create printable invoices
- Track payment status

### Staff Management
- Add new staff members
- Track staff details and status
- Process monthly salaries
- View salary history
- Manage staff positions and roles

### Hotel Services
- Request various hotel services
- Track service requests
- Manage service catalog
- View service history
- Calculate service charges

### Reports & Analytics
- View weekly performance metrics
- Analyze monthly trends
- Track booking patterns
- Monitor revenue and occupancy
- Generate financial reports

## Acknowledgments

- Built with Python and Tkinter
- Uses SQLite for data storage
- QR code generation using qrcode library
- Image processing with Pillow 
