# Church Management System (CMS)

A modern, offline-first desktop application developed in Python (PyQt6) and SQLite designed to digitize church administrative workflows, safeguard sensitive membership records, automate attendance analytics, and streamline financial records.

---

## Problem Statement & Context

In local church administration or management, very important operational records such as membership information, weekly attendance, and tithe or offering statements are often kept in physical logbooks or shared across informal messaging conversations like WhatsApp. This operational system introduces severe vulnerabilities:

- Risk of Total Data Loss: Physical logbooks can be lost or damaged by fire, water or even misplaced.
- Security and Privacy risks: Unsecured messaging channels can expose sensitive member and financial information to unauthorized people.
- Risk of data loss: Losing an account or damaging the main administrator's phone can result in permanent loss of chat-based records.

---

## Re-Engineering Journey: From VB.NET to Python

This project serves as a ground-up re-engineering of an earlier system originally implemented in VB.NET. While the initial version successfully replaced paper records, real-world deployment revealed key engineering and system limitations:

- Difficult to modify and maintain: The system is difficult to customize and requires significant effort to maintain.
- Limited access control: Fixed permissions made it difficult to assign different levels of access to users based on their roles.
- Weak security: The system used basic login security that needed stronger protection for real-world use.

To address these limitations, the system was redesigned in Python, using PyQt6 for a modular user interface, SQLite for storing and managing data, and PBKDF2-HMAC-SHA256 to securely protect user credentials.

---

## Core Features

- Secure Login: User passwords are protected using PBKDF2-HMAC-SHA256 encryption with unique salts and 100,000 hashing iterations for each user.

- Role-Based Access Control (RBAC): Users have different levels of access based on their roles:
  - Main Admin: Full system access, including user management and administrative controls.
  - Church Admin: Access to membership, attendance, and reporting features.
  - Finance Officer: Access to financial records, transactions, and financial reports.
  - Data Entry: Limited access for updating member information and recording attendance.

- Dashboard: Displays important information such as the number of active members, financial balance, and average attendance.

- Member Records: Allows users to add, edit, search, and manage member information. Members can be categorized as Active, Inactive, or Visitor, with options to export records as PDF or CSV files.

- Attendance Tracking: Records attendance for weekly services and church events and automatically calculates attendance rates.

- Financial Records: Records income and expenses, calculates the current balance, and provides filtered financial records for review.

- User Management: Allows administrators to create and manage user accounts, change user roles, reset passwords, and remove accounts.

---

## Tech Stack

- Language: Python 3.12+
- GUI Framework: PyQt6
- Database Engine: SQLite3
- Security: Python hashlib (PBKDF2-HMAC-SHA256)
- Reporting: ReportLab (PDF Generation), CSV Engine
- Packaging: PyInstaller (Windows .exe distribution)

---

## Repository Structure

```text
church_management_system/
├── database/            # Database initialization and connection handling
├── ui/                  # PyQt6 UI tabs, dialogs, and main window components
├── utils/               # Cryptographic security, export utilities, and database updaters
├── main.py              # Application entry point
├── database.py          # Primary SQLite data management class
├── .gitignore           # Excluded binaries, builds, and local database instances
└── README.md            # Project documentation

git add docs/screenshots/
git add README.md
git commit -m "docs: fix image markdown formatting and upload screenshots"
git push origin main
@'
# Church Management System (CMS)

A modern, offline-first desktop application developed in Python (PyQt6) and SQLite designed to digitize church administrative workflows, safeguard sensitive membership records, automate attendance analytics, and streamline financial records.

---

## Problem Statement & Context

In local church administration or management, very important operational records such as membership information, weekly attendance, and tithe or offering statements are often kept in physical logbooks or shared across informal messaging conversations like WhatsApp. This operational system introduces severe vulnerabilities:

- Risk of Total Data Loss: Physical logbooks can be lost or damaged by fire, water or even misplaced.
- Security and Privacy risks: Unsecured messaging channels can expose sensitive member and financial information to unauthorized people.
- Risk of data loss: Losing an account or damaging the main administrator's phone can result in permanent loss of chat-based records.

---

## Re-Engineering Journey: From VB.NET to Python

This project serves as a ground-up re-engineering of an earlier system originally implemented in VB.NET. While the initial version successfully replaced paper records, real-world deployment revealed key engineering and system limitations:

- Difficult to modify and maintain: The system is difficult to customize and requires significant effort to maintain.
- Limited access control: Fixed permissions made it difficult to assign different levels of access to users based on their roles.
- Weak security: The system used basic login security that needed stronger protection for real-world use.

To address these limitations, the system was redesigned in Python, using PyQt6 for a modular user interface, SQLite for storing and managing data, and PBKDF2-HMAC-SHA256 to securely protect user credentials.

---

## Core Features

- Secure Login: User passwords are protected using PBKDF2-HMAC-SHA256 encryption with unique salts and 100,000 hashing iterations for each user.

- Role-Based Access Control (RBAC): Users have different levels of access based on their roles:
  - Main Admin: Full system access, including user management and administrative controls.
  - Church Admin: Access to membership, attendance, and reporting features.
  - Finance Officer: Access to financial records, transactions, and financial reports.
  - Data Entry: Limited access for updating member information and recording attendance.

- Dashboard: Displays important information such as the number of active members, financial balance, and average attendance.

- Member Records: Allows users to add, edit, search, and manage member information. Members can be categorized as Active, Inactive, or Visitor, with options to export records as PDF or CSV files.

- Attendance Tracking: Records attendance for weekly services and church events and automatically calculates attendance rates.

- Financial Records: Records income and expenses, calculates the current balance, and provides filtered financial records for review.

- User Management: Allows administrators to create and manage user accounts, change user roles, reset passwords, and remove accounts.

---

## Tech Stack

- Language: Python 3.12+
- GUI Framework: PyQt6
- Database Engine: SQLite3
- Security: Python hashlib (PBKDF2-HMAC-SHA256)
- Reporting: ReportLab (PDF Generation), CSV Engine
- Packaging: PyInstaller (Windows .exe distribution)

---

## Repository Structure

```text
church_management_system/
├── database/            # Database initialization and connection handling
├── ui/                  # PyQt6 UI tabs, dialogs, and main window components
├── utils/               # Cryptographic security, export utilities, and database updaters
├── main.py              # Application entry point
├── database.py          # Primary SQLite data management class
├── .gitignore           # Excluded binaries, builds, and local database instances
└── README.md            # Project documentation
