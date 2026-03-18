# BreakMoney – Expense Management & Debt Simplification Platform

**BreakMoney** is a robust, backend-driven expense-sharing application built with **Django 5+**. Inspired by Splitwise, it simplifies group finances through a custom netting algorithm that minimizes the number of transactions required to settle debts.

**Live at:** https://yuvieee01.pythonanywhere.com/

## 🚀 Key Features

* **Advanced Splitting Logic:** Support for equal splits, exact amounts, percentages, shares, and adjustments.
* **Smart Netting Algorithm:** Implements a debt-simplification engine to calculate the most efficient path for group settlements.
* **Modular Architecture:** Built with a scalable Django app structure, ensuring clean separation of concerns between user management, group dynamics, and financial transactions.
* **Persistent User Ecosystem:** Comprehensive authentication system with friend management and group-based access control.
* **Real-time Balance Tracking:** Uses optimized Django ORM queries to provide instant updates on "Who owes whom" across multiple groups.

## 🛠️ Technical Stack

* **Backend:** Python, Django 5+
* **Database:** Relational (SQLite/PostgreSQL) via Django ORM
* **Frontend:** Bootstrap 5, Django Templates (Server-Rendered)
* **Logic:** Custom Financial Algorithms (Debt Simplification)

## 📂 Project Structure

```text
breakmoney/
├── core/               # Authentication & User Profiles
├── expenses/           # Splitting logic & Transaction models
├── groups/             # Group management & Membership logic
├── templates/          # Responsive Bootstrap-based views
└── static/             # Custom CSS & JavaScript
```
## ⚙️ Installation
###Clone the repository:
```bash
git clone [https://github.com/yuvieee01/breakmoney.git](https://github.com/yuvieee01/breakmoney.git)
cd breakmoney
```

###Set up a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

###Install dependencies:
```bash
pip install -r requirements.txt
```
###Run migrations & start server:
```bash
python manage.py migrate
python manage.py runserver
```
===================================================
## 🗺️ Future Roadmap
### Infrastructure & DevOps:

[ ] Containerization: Dockerize the application for consistent development and deployment environments.

[ ] AWS Deployment: Host the platform on AWS (EC2/RDS) with an S3 bucket for media/static file management.

[ ] CI/CD Pipeline: Implement GitHub Actions for automated testing and deployment.

### Enhanced Intelligence & Features:

[ ] Predictive Spending Analytics: Integrate a lightweight Scikit-learn model to categorize expenses and predict monthly budget overruns.

[ ] OCR Integration: Use Tesseract or AWS Textract to automatically parse receipts and populate expense fields.

[ ] Real-time Notifications: Implement Django Channels (WebSockets) for instant alerts on new expenses or settlement requests.
