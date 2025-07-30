from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum

class UserRole(Enum):
    MEMBER = "member"
    ADMIN = "admin"

class CommitteeType(Enum):
    PUBLIC = "public"
    PRIVATE = "private"

class PaymentFrequency(Enum):
    MONTHLY = "monthly"
    BI_MONTHLY = "bi_monthly"

class PaymentStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class CommitteeStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class User:
    id: str
    username: str
    password_hash: str
    full_name: str
    email: str
    phone: str
    role: UserRole
    cnic: Optional[str] = None
    trust_score: int = 85
    created_date: datetime = None
    last_login: Optional[datetime] = None
    is_active: bool = True

@dataclass
class Committee:
    id: str
    title: str
    description: Optional[str]
    monthly_amount: int
    total_members: int
    current_members: int = 0
    duration: int = 12
    committee_type: CommitteeType = CommitteeType.PUBLIC
    category: str = "General"
    payment_frequency: PaymentFrequency = PaymentFrequency.MONTHLY
    status: CommitteeStatus = CommitteeStatus.ACTIVE
    admin_id: str = None
    created_date: datetime = None
    start_date: Optional[datetime] = None
    next_payout_date: Optional[datetime] = None

@dataclass
class CommitteeMember:
    id: str
    committee_id: str
    user_id: str
    position: int
    joined_date: datetime
    is_active: bool = True
    payout_preference: str = "bank_transfer"

@dataclass
class Payment:
    id: str
    committee_id: str
    user_id: str
    amount: int
    payment_date: datetime
    due_date: datetime
    status: PaymentStatus
    transaction_id: Optional[str] = None
    payment_method: str = "bank_transfer"
    notes: Optional[str] = None

@dataclass
class Payout:
    id: str
    committee_id: str
    user_id: str
    amount: int
    payout_date: datetime
    status: PaymentStatus
    payout_method: str = "bank_transfer"
    transaction_id: Optional[str] = None
    notes: Optional[str] = None

@dataclass
class PayoutSchedule:
    id: str
    committee_id: str
    user_id: str
    scheduled_date: datetime
    position: int
    is_completed: bool = False

@dataclass
class TrustScoreHistory:
    id: str
    user_id: str
    old_score: int
    new_score: int
    change_reason: str
    change_date: datetime
    committee_id: Optional[str] = None

@dataclass
class Notification:
    id: str
    user_id: str
    title: str
    message: str
    notification_type: str
    created_date: datetime
    read_date: Optional[datetime] = None
    is_read: bool = False
    related_id: Optional[str] = None  # Can be committee_id, payment_id, etc.

# Database schema SQL
DATABASE_SCHEMA = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    role VARCHAR(20) DEFAULT 'member' CHECK (role IN ('member', 'admin')),
    cnic VARCHAR(20),
    trust_score INTEGER DEFAULT 85 CHECK (trust_score >= 0 AND trust_score <= 100),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Committees table
CREATE TABLE IF NOT EXISTS committees (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    monthly_amount INTEGER NOT NULL CHECK (monthly_amount > 0),
    total_members INTEGER NOT NULL CHECK (total_members >= 2),
    current_members INTEGER DEFAULT 0 CHECK (current_members >= 0),
    duration INTEGER NOT NULL CHECK (duration >= 1),
    committee_type VARCHAR(20) DEFAULT 'public' CHECK (committee_type IN ('public', 'private')),
    category VARCHAR(50) DEFAULT 'General',
    payment_frequency VARCHAR(20) DEFAULT 'monthly' CHECK (payment_frequency IN ('monthly', 'bi_monthly')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'cancelled')),
    admin_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    start_date TIMESTAMP,
    next_payout_date TIMESTAMP
);

-- Committee members table
CREATE TABLE IF NOT EXISTS committee_members (
    id VARCHAR(36) PRIMARY KEY,
    committee_id VARCHAR(36) REFERENCES committees(id) ON DELETE CASCADE,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    payout_preference VARCHAR(50) DEFAULT 'bank_transfer',
    UNIQUE(committee_id, user_id),
    UNIQUE(committee_id, position)
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id VARCHAR(36) PRIMARY KEY,
    committee_id VARCHAR(36) REFERENCES committees(id) ON DELETE CASCADE,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL CHECK (amount > 0),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'failed', 'refunded')),
    transaction_id VARCHAR(100),
    payment_method VARCHAR(50) DEFAULT 'bank_transfer',
    notes TEXT
);

-- Payouts table
CREATE TABLE IF NOT EXISTS payouts (
    id VARCHAR(36) PRIMARY KEY,
    committee_id VARCHAR(36) REFERENCES committees(id) ON DELETE CASCADE,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL CHECK (amount > 0),
    payout_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'failed', 'refunded')),
    payout_method VARCHAR(50) DEFAULT 'bank_transfer',
    transaction_id VARCHAR(100),
    notes TEXT
);

-- Payout schedule table
CREATE TABLE IF NOT EXISTS payout_schedule (
    id VARCHAR(36) PRIMARY KEY,
    committee_id VARCHAR(36) REFERENCES committees(id) ON DELETE CASCADE,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    scheduled_date TIMESTAMP NOT NULL,
    position INTEGER NOT NULL,
    is_completed BOOLEAN DEFAULT false,
    UNIQUE(committee_id, position)
);

-- Trust score history table
CREATE TABLE IF NOT EXISTS trust_score_history (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    old_score INTEGER NOT NULL,
    new_score INTEGER NOT NULL,
    change_reason VARCHAR(255) NOT NULL,
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    committee_id VARCHAR(36) REFERENCES committees(id) ON DELETE SET NULL
);

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_date TIMESTAMP,
    is_read BOOLEAN DEFAULT false,
    related_id VARCHAR(36)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_committees_admin ON committees(admin_id);
CREATE INDEX IF NOT EXISTS idx_committees_type ON committees(committee_type);
CREATE INDEX IF NOT EXISTS idx_committee_members_committee ON committee_members(committee_id);
CREATE INDEX IF NOT EXISTS idx_committee_members_user ON committee_members(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_committee ON payments(committee_id);
CREATE INDEX IF NOT EXISTS idx_payments_user ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payouts_committee ON payouts(committee_id);
CREATE INDEX IF NOT EXISTS idx_payouts_user ON payouts(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read);
"""
