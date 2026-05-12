# BreakMoney - High Level Design (HLD)

## 1. Overview

**BreakMoney** is a Django-based expense sharing platform inspired by Splitwise. It enables users to track shared expenses in groups and automatically calculates the minimum number of payments needed to settle all debts using a debt simplification (netting) algorithm.

**Live:** https://yuvieee01.pythonanywhere.com/
**Tech Stack:** Python 3, Django 5+, PostgreSQL/SQLite, Bootstrap 5, Django Templates

---

## 2. Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                  │
│  ┌─────────────┐     ┌──────────────┐    ┌─────────────┐                   │
│  │   Browser   │────▶│  Bootstrap 5 │───▶│   Django    │                   │
│  │  (Django    │◀────│   Templates  │◀───│   Views     │                   │
│  │   Templates)│     │   (HTML/CSS) │    │             │                   │
│  └─────────────┘     └──────────────┘    └───────┬─────┘                   │
└──────────────────────────────────────────────────┼─────────────────────────┘
                                                   │
┌──────────────────────────────────────────────────┼─────────────────────────┐
│                          DJANGO APP LAYER        │                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  │  ┌────────────┐         │
│  │  accounts  │  │   friends  │  │   groups   │◀─┼─▶│   ledger   │         │
│  │            │  │            │  │            │  │  │            │         │
│  │  - User    │  │-Friendship │  │  - Group   │  │  │-Dashboard  │         │
│  │  - Auth    │  │  - Invite  │  │  - Member  │  │  │-Balance    │         │
│  └────────────┘  └────────────┘  └─────┬──────┘  │  └─────┬──────┘         │
│                                        │         │        │                │
│  ┌────────────┐  ┌────────────┐  ┌─────┴──────┐  │  ┌─────┴──────┐         │
│  │  expenses  │  │ settlements│  │   audit    │◀─┼─▶│  selectors │         │
│  │            │  │            │  │            │  │  │            │         │
│  │  - Expense │  │-Settlement │  │-ActivityLog│  │  │-get_all_   │         │
│  │  - Split   │  │            │  │            │  │  │  balances  │         │
│  └────────────┘  └────────────┘  └────────────┘  │  └─────┬──────┘         │
│                                                  │        │                │
│  ┌─────────────────────────────────────────────┐ │        │                │
│  │              ledger/services.py             │─┘        │                │
│  │           simplify_debts() + dashboard      │          │                │
│  └─────────────────────────────────────────────┘          │                │
└──────────────────────────────────────────────────┼────────┼────────────────┘
                                                   │        │
┌──────────────────────────────────────────────────┼────────┼────────────────┐
│                          DATA LAYER              │        │                │
│                                                  │        │                │
│  ┌──────────────────────────────────────────────┐│        │                │
│  │                  Django ORM                  ││        │                │
│  └──────────────────────────────────────────────┘│        │                │
│                        │                         │        │                │
│                    ┌───┴───┐                     │        │                │
│                    ▼       ▼                     │        │                │
│           ┌────────────┐ ┌───────────┐           │        │                │
│           │ PostgreSQL │ │  SQLite   │           │        │                │
│           │(Production)│ │(Dev only) │           │        │                │
│           └────────────┘ └───────────┘           │        │                │
└──────────────────────────────────────────────────┴────────┴────────────────┘
```

---

## 3. Application Modules

### 3.1 accounts
**Purpose:** User authentication and profile management

| Model | Description |
|-------|-------------|
| `User` | Custom user model using email as username |
| `EmailVerificationToken` | Email verification with hashed tokens |

**Features:**
- Email/password authentication
- Email verification with token hashing
- User preferences (currency, timezone, notifications)

---

### 3.2 friends
**Purpose:** Friend connections between users

| Model | Description |
|-------|-------------|
| `Friendship` | Bidirectional friendship between two users |
| `FriendInvitation` | Pending invite to unregistered emails |

---

### 3.3 groups
**Purpose:** Group management and membership

| Model | Description |
|-------|-------------|
| `Group` | Expense group with name, description, icon |
| `GroupMember` | User membership with role (ADMIN/MEMBER) |

**Business Logic:**
- Only group members can view group expenses
- Only ADMINs can remove members or delete groups
- Any member can invite others

---

### 3.4 expenses
**Purpose:** Expense tracking and splitting

| Model | Description |
|-------|-------------|
| `Expense` | Expense with amount, date, category, split_type |
| `ExpenseParticipant` | Per-user paid/owed amounts per expense |

**Split Types:**
| Type | Description |
|------|-------------|
| `EQUAL` | Divide equally among participants |
| `EXACT` | Specify exact amounts per person |
| `PERCENTAGE` | Percentage-based splits |
| `SHARES` | Weighted shares |
| `ADJUSTMENT` | Manual adjustment amounts |

**Categories:** FOOD, RENT, TRAVEL, UTILITIES, OTHER

---

### 3.5 settlements
**Purpose:** Recording debt payments

| Model | Description |
|-------|-------------|
| `Settlement` | Payment from one user to another |

---

### 3.6 ledger
**Purpose:** Dashboard and balance calculations

**Key Function:** `simplify_debts(group=None)`
- Implements debt netting algorithm
- Minimizes number of transactions to settle all debts
- Returns optimal payment instructions

---

### 3.7 audit
**Purpose:** Activity logging

| Model | Description |
|-------|-------------|
| `ActivityLog` | Tracks actions (expense added, payment, etc.) |

---

## 4. Core Algorithm: Debt Simplification

```
┌─────────────────────────────────────────────────────────────────┐
│                    simplify_debts() Algorithm                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Calculate balance for each user:                            │
│     balance = sum(amount_paid) - sum(amount_owed)               │
│                                                                 │
│  2. Classify users:                                             │
│     • Debtors (balance < 0) → owe money                         │
│     • Creditors (balance > 0) → are owed                        │
│                                                                 │
│  3. Sort both lists by amount (descending)                      │
│                                                                 │
│  4. Match largest debtor with largest creditor:                 │
│     settle_amount = min(debt, credit)                           │
│     Update balances, advance pointers                           │
│                                                                 │
│  5. Merge duplicate transactions into single payments           │
│                                                                 │
│  6. Return minimal transaction set                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Example:
  ┌──────────────────────────────────────────────────┐
  │  Before (6 potential payments):                  │
  │  A→B: $20, A→C: $10, B→A: $5, B→C: $15,          │
  │  C→A: $10, C→B: $10                              │
  │                                                  │
  │  After simplification (2 payments):              │
  │  B→C: $15, B→A: $10                              │
  └──────────────────────────────────────────────────┘
```

---

## 5. Data Flow

```
User Action: "Add Expense"
──────────────────────────

  [Browser]
     │ POST /expenses/add/
     ▼
  [expenses/views.py] ──── expense_form.html
     │
     ▼
  [Save Expense + Participants to DB]
     │
     ▼
  [audit/ActivityLog] ──── "EXPENSE_ADDED"
     │
     ▼
  [Redirect to group detail]

User Action: "View Balances"
────────────────────────────

  [Browser]
     │ GET /ledger/dashboard/
     ▼
  [ledger/views.py] ──── dashboard.html
     │
     ▼
  [ledger/services/simplify_debts()]
     │
     ├── [groups/selectors/get_all_user_balances()]
     │       └── Query: expenses + settlements per user
     │
     ▼
  [Return minimal transactions]
     │
     ▼
  [Render dashboard with "You owe" / "You are owed" lists]
```

---

## 6. Database Schema

```
┌──────────────────────────────────────────────────────────────────┐
│                        accounts_user                             │
├──────────────────────────────────────────────────────────────────┤
│ id │ email │ password │ first_name │ last_name │ default_currency│
├────┼───────┼──────────┼────────────┼───────────┼─────────────────┤
│ PK │  UK   │          │            │           │                 │
└──────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌──────────────────┐   ┌─────────────────┐
│ groups_group  │   │friends_friendship│   │friends_friend   │
├───────────────┤   ├──────────────────┤   │  _invitation    │
│ id (PK)       │   │ id (PK)          │   ├─────────────────┤
│ name          │   │ user1_id (FK)    │   │ id (PK)         │
│ description   │   │ user2_id (FK)    │   │ sender_id (FK)  │
│ created_by_id │   │ created_at       │   │ email           │
└───────┬───────┘   └──────────────────┘   │ status          │
        │                                  └─────────────────┘
        │
        ▼
┌───────────────────────┐     ┌───────────────────────┐
│  groups_groupmember   │     │     expenses_expense  │
├───────────────────────┤     ├───────────────────────┤
│ id (PK)               │     │ id (PK)               │
│ group_id (FK)         │◀────│ group_id (FK)         │
│ user_id (FK)          │     │ description           │
│ role (ADMIN/MEMBER)   │     │ amount (Decimal)      │
│ joined_at             │     │ date                  │
└───────────────────────┘     │ category              │
        │                     │ split_type            │
        │                     │ created_by_id (FK)    │
        ▼                     └───────────┬───────────┘
┌───────────────────────┐                 │
│expenses_expense       │                 ▼
│_participant           │     ┌───────────────────────┐
├───────────────────────┤     │   settlements         │
│ id (PK)               │     │   _settlement         │
│ expense_id (FK)       │     ├───────────────────────┤
│ user_id (FK)          │     │ id (PK)               │
│ amount_paid           │     │ payer_id (FK)         │
│ amount_owed           │◀────│ receiver_id (FK)      │
│ weight                │     │ group_id (FK)         │
└───────────────────────┘     │ amount                │
                              │ date                  │
                              └───────────────────────┘

┌────────────────────────┐
│    audit_activitylog   │
├────────────────────────┤
│ id (PK)                │
│ user_id (FK)           │
│ group_id (FK)          │
│ action_type            │
│ description            │
│ created_at             │
└────────────────────────┘
```

---

## 7. URL Structure

```
/                          → ledger:dashboard (home)
/accounts/                 → Login, Register, Logout
/accounts/register/        → Registration
/accounts/login/           → Login
/accounts/logout/          → Logout
/accounts/verify/<token>/  → Email verification

/friends/                  → Friend list
/friends/invite/           → Send friend invite

/groups/                   → Group list
/groups/create/            → Create group
/groups/<id>/              → Group detail
/groups/<id>/add/          → Add member

/expenses/add/             → Add expense
/expenses/<id>/edit/       → Edit expense
/expenses/<id>/delete/     → Delete expense

/settlements/add/          → Record payment

/activity/                 → Activity log
```

---

## 8. Security Model

| Protection | Implementation |
|------------|----------------|
| Authentication | Email-based with hashed password |
| Authorization | Group membership checks in views |
| CSRF | Django CSRF middleware + tokens |
| SQL Injection | ORM (parameterized queries) |
| XSS | Django template auto-escaping |
| Email Tokens | SHA-256 hashed, time-limited |

**Access Control:**
- Users can only view groups they are members of
- Only ADMINs can remove members or delete groups
- Balance calculations use `select_related` to prevent N+1

---

## 9. Environment Configuration

```bash
# Database (PostgreSQL for production)
DJANGO_ENV=production          # or "development"
DB_NAME=breakmoney
DB_USER=postgres
DB_PASSWORD=xxx
DB_HOST=localhost
DB_PORT=5432

# Security
DJANGO_SECRET_KEY=xxx
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=example.com

# Email
DJANGO_EMAIL_HOST=smtp.pythonanywhere.com
DJANGO_EMAIL_PORT=587
DJANGO_EMAIL_HOST_USER=xxx
DJANGO_EMAIL_HOST_PASSWORD=xxx
```

---

## 10. Future Enhancements (Roadmap)

| Feature | Description |
|---------|-------------|
| Docker | Containerization for deployment |
| WebSockets | Real-time notifications (Django Channels) |
| OCR | Receipt scanning with Tesseract/AWS Textract |
| ML Analytics | Spending prediction with scikit-learn |
| CI/CD | GitHub Actions for testing/deployment |