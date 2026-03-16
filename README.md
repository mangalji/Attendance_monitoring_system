## Student Information System (Django)

A full-featured **Student Information System** built with **Django 6**, designed to help institutes manage **student profiles, attendance records, and fee payments** in one place.  
This project provides separate dashboards for **Managers** and **Students**, with role-based access, attendance analytics, fee tracking, and in-app notifications.

---

###  Features

- **Role-based Authentication**
  - Login using **email and password**
  - Smart redirect based on role: **Admin**, **Manager**, or **Student**
  - Protected views using custom decorators for manager and student roles

- **Student Management (Manager)**
  - Add new students with:
    - Basic user details (email, name, etc.)
    - Detailed student profile (roll number, contact info, etc.)
    - Parent information
  - View all students in a sortable list
  - View individual student details
  - Edit student details (by manager)
  - Delete student records (with confirmation)
  - **Reset student password** from the manager panel

- **Student Self Service**
  - Student dashboard with personal information
  - Edit/update own profile details
  - View notifications (fee updates, reminders, etc.)
  - Secure password reset via **“Forgot Password”** page using:
    - Registered email  
    - Registered phone  
    - Roll number  
    - New password + confirm password

- **Attendance Management**
  - Upload monthly attendance from **Excel** files
  - Robust parsing of Excel:
    - Reads roll numbers
    - Parses **in-time**, **out-time**, and calculates **total hours**
    - Ignores invalid/empty cells gracefully
  - Manager/Administrator attendance view:
    - Filter by **date range** or **month**
    - Shows daily attendance grid per student
    - Highlights:
      - **Green** for sufficient hours (e.g. ≥ 6 hours)
      - **Red** for low attendance
    - Totals for **hours worked** and **days present**
  - Student attendance view:
    - Student can view **own attendance** for selected month or date range
    - Same color-coded visualization and totals
  - Generate **PDF attendance report**:
    - Based on selected date range or month
    - Downloadable as an attachment

- **Fees Management**
  - Central **Fee Manager** view for managers/admins
  - For each student:
    - Track **total fees**
    - Track **paid amount**
    - Calculate pending fees from records
  - Upload multiple **fee receipts** (e.g., installments)
  - Automatically create fee record if missing
  - Integrated with notifications:
    - Student gets a notification when fees are updated
    - Manager can send **fee reminders** to students

- **Notifications System**
  - Notifications stored in the database
  - Types such as **fee update** and **fee reminder**
  - Student notification page:
    - Shows all notifications with latest first
    - Unread count support
  - Mark notifications as read

- **Modern UI (Bootstrap)**
  - Uses **Bootstrap 5** for clean and responsive layouts
  - User-friendly forms for login, forgot password, student CRUD, attendance upload, etc.

---

###  Project Structure (High Level)

- `student_info_system/`
  - Core project settings, URLs, WSGI/ASGI configuration
- `accounts/`
  - Custom user-related logic:
    - Student and Manager profiles
    - Parent model
    - Login/logout
    - Dashboards
    - Student management CRUD
    - Notifications
    - Student password reset logic
- `attendance/`
  - Attendance models and views
  - Excel upload & parsing with **pandas**
  - Monthly/period views for manager and students
  - PDF report generation utilities
- `fees/`
  - Fee records and views
  - Fee manager dashboard
  - Receipt uploads
  - Fee reminders and notifications
- `templates/`
  - `login.html`
  - `manager/…` (dashboard, add/edit/view student, reset password, delete confirm)
  - `student/…` (dashboard, edit profile, notifications, forgot password, attendance)
  - `attendance/…` (upload, view, student_view)
  - `fees/…` (fee manager, student view)
  - `registration/…` (password change views)
- `media/`
  - Stores uploaded **receipt PDFs** and other media files

---

###  Tech Stack

- **Backend**: Django 6.x, Python 3.x
- **Database**: SQLite (default, easy to switch to PostgreSQL/MySQL)
- **Frontend**: Django templates + **Bootstrap 5**
- **Other Libraries**:
  - `pandas` – parsing Excel-based attendance sheets
  - `fpdf2` – generating attendance PDF reports
  - `Pillow` – image handling for uploaded photos
  - Django messages framework for user feedback
- **Authentication**: Django’s built-in auth system with custom profiles

---

###  Getting Started

#### 1. Clone the repository

```bash
git clone https://github.com/mangalji/Attendance_monitoring_system.git
cd <Attendance_monitoring_system>
```

#### 2. Create & activate a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Apply database migrations

```bash
python manage.py migrate
```

#### 5. Create a superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

#### 6. Run the development server

```bash
python manage.py runserver
```

Then open `http://127.0.0.1:8000/` in your browser.

---

###  Default URL Overview

- **Root** (`/`)
  - Redirects:
    - Admins → `/admin/`
    - Managers → `manager_dashboard`
    - Students → `student_dashboard`
    - Guests → `login`
- **Authentication & Accounts**
  - `/accounts/login/` (via `user_login` view, or as configured)
  - `/accounts/logout/`
  - `/accounts/manager_dashboard/`
  - `/accounts/student_dashboard/`
  - Student CRUD URLs under `/accounts/…` (view, add, edit, delete, reset password)
- **Attendance**
  - `/attendance/upload/` – upload Excel, manager only
  - `/attendance/view/` – manager/admin view
  - `/attendance/student/` – student self view
  - `/attendance/download_report/` – PDF export
- **Fees**
  - `/fees/manager/` – fee manager dashboard
  - `/fees/update/<student_id>/` – update fees & receipts
  - `/fees/reminder/<student_id>/` – send fee reminder
  - `/fees/student/` – student fee view
- **Notifications**
  - `/accounts/notifications/` – student notifications list
  - `/accounts/notifications/<pk>/read/` – mark as read

*(Exact URLs may vary slightly; see `urls.py` in each app.)*

---

###  Attendance Upload Format (Excel)

- Designed for **monthly attendance** import.
- The view:
  - Starts reading data from row 4 (`start_row = 4`)
  - Uses a specific column for roll number
  - Each cell for a day contains:
    - `IN_TIME OUT_TIME` (e.g. `10:00 18:30`)
- For each valid cell:
  - Computes `total_hours = out_time - in_time`
  - Saves/updates an `AttendanceRecord` for that student and date
- If a student roll number from the sheet does not exist in the system, that row is skipped gracefully.

You can adapt the Excel format or logic in `attendance/views.py` as needed.

---

###  Notifications & Fee Reminders

- Whenever fees are updated:
  - A **Notification** is created for the student:  
    “Your fees record has been updated. Total paid fees: ₹X”
- Managers can manually send a **fee reminder**:
  - Message like: “Reminder! Please pay your pending fees as soon as possible.”
- Students can see all these notifications in their notification page, with unread counts and read status.

---

###  Forgot Password Flow (Student)

- Accessible from the **“Forgot Password”** page (e.g., `/student/forgot_password/`).
- Student must enter:
  - Registered email
  - Registered phone
  - Roll number
  - New password + confirmation
- If details match, the system updates the password and the student can log in with the new credentials.

---

###  Possible Improvements

- Add email or SMS integration for notifications and fee reminders.
- Replace SQLite with PostgreSQL for production.
- Add CSV export for fee and attendance reports.
- Enhance analytics: monthly attendance summaries, charts, etc.
- Add parent login to see student fees and attendance.

---

###  License

You can add a license section here, for example:

> This project is licensed under the MIT License – feel free to use and modify it as needed.
