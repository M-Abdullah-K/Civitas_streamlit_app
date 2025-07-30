import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import uuid
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import hashlib

@dataclass
class User:
    id: str
    username: str
    full_name: str
    email: str
    phone: str
    role: str
    cnic: Optional[str]
    trust_score: int
    created_date: datetime
    password_hash: str

@dataclass
class Committee:
    id: str
    title: str
    description: Optional[str]
    monthly_amount: int
    total_members: int
    current_members: int
    duration: int
    committee_type: str
    category: str
    payment_frequency: str
    status: str
    admin_id: str
    created_date: datetime

@dataclass
class Payment:
    id: str
    committee_id: str
    user_id: str
    amount: int
    payment_date: datetime
    status: str
    transaction_id: Optional[str]
    payment_method: str

@dataclass
class Payout:
    id: str
    committee_id: str
    user_id: str
    amount: int
    payout_date: datetime
    status: str
    payout_method: str

class DatabaseManager:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('PGHOST', 'localhost'),
            'database': os.getenv('PGDATABASE', 'civitas'),
            'user': os.getenv('PGUSER', 'postgres'),
            'password': os.getenv('PGPASSWORD', ''),
            'port': os.getenv('PGPORT', '5432')
        }
        self.initialize_database()

    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(**self.connection_params)
        except psycopg2.Error as e:
            print(f"Database connection error: {e}")
            # Fallback to in-memory storage for demo
            return None

    def initialize_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        if not conn:
            print("Using in-memory storage - database connection failed")
            self._init_fallback_storage()
            return

        try:
            with conn.cursor() as cur:
                # Create tables
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id VARCHAR(36) PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        full_name VARCHAR(100) NOT NULL,
                        email VARCHAR(100) NOT NULL,
                        phone VARCHAR(20) NOT NULL,
                        role VARCHAR(20) DEFAULT 'member',
                        cnic VARCHAR(20),
                        trust_score INTEGER DEFAULT 85,
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS committees (
                        id VARCHAR(36) PRIMARY KEY,
                        title VARCHAR(100) NOT NULL,
                        description TEXT,
                        monthly_amount INTEGER NOT NULL,
                        total_members INTEGER NOT NULL,
                        current_members INTEGER DEFAULT 0,
                        duration INTEGER NOT NULL,
                        committee_type VARCHAR(20) DEFAULT 'public',
                        category VARCHAR(50) DEFAULT 'General',
                        payment_frequency VARCHAR(20) DEFAULT 'monthly',
                        status VARCHAR(20) DEFAULT 'active',
                        admin_id VARCHAR(36) REFERENCES users(id),
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS committee_members (
                        id VARCHAR(36) PRIMARY KEY,
                        committee_id VARCHAR(36) REFERENCES committees(id),
                        user_id VARCHAR(36) REFERENCES users(id),
                        position INTEGER,
                        joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(committee_id, user_id)
                    )
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS payments (
                        id VARCHAR(36) PRIMARY KEY,
                        committee_id VARCHAR(36) REFERENCES committees(id),
                        user_id VARCHAR(36) REFERENCES users(id),
                        amount INTEGER NOT NULL,
                        payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(20) DEFAULT 'pending',
                        transaction_id VARCHAR(100),
                        payment_method VARCHAR(50) DEFAULT 'bank_transfer'
                    )
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS payouts (
                        id VARCHAR(36) PRIMARY KEY,
                        committee_id VARCHAR(36) REFERENCES committees(id),
                        user_id VARCHAR(36) REFERENCES users(id),
                        amount INTEGER NOT NULL,
                        payout_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(20) DEFAULT 'pending',
                        payout_method VARCHAR(50) DEFAULT 'bank_transfer'
                    )
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS committee_invitations (
                        id VARCHAR(36) PRIMARY KEY,
                        committee_id VARCHAR(36) REFERENCES committees(id),
                        invited_user_id VARCHAR(36) REFERENCES users(id),
                        invited_by_id VARCHAR(36) REFERENCES users(id),
                        invitation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status VARCHAR(20) DEFAULT 'pending',
                        response_date TIMESTAMP,
                        message TEXT
                    )
                """)

                # Create demo admin user if not exists
                self._create_demo_users(cur)

                conn.commit()
                print("Database initialized successfully")

        except psycopg2.Error as e:
            print(f"Database initialization error: {e}")
            conn.rollback()
        finally:
            conn.close()

    def _init_fallback_storage(self):
        """Initialize fallback in-memory storage"""
        if not hasattr(self, 'fallback_data'):
            self.fallback_data = {
                'users': {},
                'committees': {},
                'committee_members': {},
                'payments': {},
                'payouts': {}
            }
            # Add demo users
            demo_admin_id = str(uuid.uuid4())
            demo_member_id = str(uuid.uuid4())

            self.fallback_data['users'][demo_admin_id] = User(
                id=demo_admin_id,
                username='demo_admin',
                full_name='Demo Admin',
                email='admin@civitas.pk',
                phone='+92-300-1234567',
                role='admin',
                cnic='12345-1234567-1',
                trust_score=95,
                created_date=datetime.now(),
                password_hash=hashlib.sha256('password'.encode()).hexdigest()
            )

            self.fallback_data['users'][demo_member_id] = User(
                id=demo_member_id,
                username='demo_member',
                full_name='Demo Member',
                email='member@civitas.pk',
                phone='+92-300-7654321',
                role='member',
                cnic='54321-7654321-5',
                trust_score=88,
                created_date=datetime.now(),
                password_hash=hashlib.sha256('password'.encode()).hexdigest()
            )

    def _create_demo_users(self, cur):
        """Create demo users for testing"""
        # Check if demo users exist
        cur.execute("SELECT username FROM users WHERE username IN ('demo_admin', 'demo_member')")
        existing_users = [row[0] for row in cur.fetchall()]

        if 'demo_admin' not in existing_users:
            admin_id = str(uuid.uuid4())
            password_hash = hashlib.sha256('password'.encode()).hexdigest()
            cur.execute("""
                INSERT INTO users (id, username, password_hash, full_name, email, phone, role, cnic, trust_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (admin_id, 'demo_admin', password_hash, 'Demo Admin', 'admin@civitas.pk', 
                  '+92-300-1234567', 'admin', '12345-1234567-1', 95))

        if 'demo_member' not in existing_users:
            member_id = str(uuid.uuid4())
            password_hash = hashlib.sha256('password'.encode()).hexdigest()
            cur.execute("""
                INSERT INTO users (id, username, password_hash, full_name, email, phone, role, cnic, trust_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (member_id, 'demo_member', password_hash, 'Demo Member', 'member@civitas.pk', 
                  '+92-300-7654321', 'member', '54321-7654321-5', 88))

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user login"""
        conn = self.get_connection()
        if not conn:
            # Fallback authentication
            for user in self.fallback_data['users'].values():
                if (user.username == username and 
                    user.password_hash == hashlib.sha256(password.encode()).hexdigest()):
                    return {
                        'id': user.id,
                        'username': user.username,
                        'full_name': user.full_name,
                        'email': user.email,
                        'phone': user.phone,
                        'role': user.role,
                        'trust_score': user.trust_score,
                        'cnic': user.cnic
                    }
            return None

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cur.execute("""
                    SELECT id, username, full_name, email, phone, role, trust_score, cnic
                    FROM users 
                    WHERE username = %s AND password_hash = %s
                """, (username, password_hash))

                user = cur.fetchone()
                return dict(user) if user else None

        except psycopg2.Error as e:
            print(f"Authentication error: {e}")
            return None
        finally:
            conn.close()

    def create_user(self, username: str, password: str, full_name: str, email: str, 
                   phone: str, role: str, cnic: Optional[str] = None) -> bool:
        """Create new user"""
        conn = self.get_connection()
        if not conn:
            # Fallback user creation
            for user in self.fallback_data['users'].values():
                if user.username == username:
                    return False

            user_id = str(uuid.uuid4())
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            self.fallback_data['users'][user_id] = User(
                id=user_id,
                username=username,
                full_name=full_name,
                email=email,
                phone=phone,
                role=role,
                cnic=cnic,
                trust_score=85,
                created_date=datetime.now(),
                password_hash=password_hash
            )
            return True

        try:
            with conn.cursor() as cur:
                user_id = str(uuid.uuid4())
                password_hash = hashlib.sha256(password.encode()).hexdigest()

                cur.execute("""
                    INSERT INTO users (id, username, password_hash, full_name, email, phone, role, cnic)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, username, password_hash, full_name, email, phone, role, cnic))

                conn.commit()
                return True

        except psycopg2.IntegrityError:
            conn.rollback()
            return False
        except psycopg2.Error as e:
            print(f"User creation error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = self.get_connection()
        if not conn:
            # Fallback
            user = self.fallback_data['users'].get(user_id)
            if user:
                return {
                    'id': user.id,
                    'username': user.username,
                    'full_name': user.full_name,
                    'email': user.email,
                    'phone': user.phone,
                    'role': user.role,
                    'trust_score': user.trust_score,
                    'cnic': user.cnic
                }
            return None

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, username, full_name, email, phone, role, trust_score, cnic
                    FROM users WHERE id = %s
                """, (user_id,))

                user = cur.fetchone()
                return dict(user) if user else None

        except psycopg2.Error as e:
            print(f"Get user error: {e}")
            return None
        finally:
            conn.close()

    def create_committee(self, title: str, description: Optional[str], monthly_amount: int,
                        total_members: int, duration: int, committee_type: str,
                        category: str, payment_frequency: str, admin_id: str) -> bool:
        """Create new committee"""
        conn = self.get_connection()
        committee_id = str(uuid.uuid4())

        if not conn:
            # Fallback committee creation
            self.fallback_data['committees'][committee_id] = Committee(
                id=committee_id,
                title=title,
                description=description,
                monthly_amount=monthly_amount,
                total_members=total_members,
                current_members=1,
                duration=duration,
                committee_type=committee_type,
                category=category,
                payment_frequency=payment_frequency,
                status='active',
                admin_id=admin_id,
                created_date=datetime.now()
            )

            # Add admin as first member
            member_id = str(uuid.uuid4())
            self.fallback_data['committee_members'][member_id] = {
                'id': member_id,
                'committee_id': committee_id,
                'user_id': admin_id,
                'position': 1,
                'joined_date': datetime.now()
            }
            return True

        try:
            with conn.cursor() as cur:
                # Create committee
                cur.execute("""
                    INSERT INTO committees (id, title, description, monthly_amount, total_members,
                                         current_members, duration, committee_type, category,
                                         payment_frequency, admin_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (committee_id, title, description, monthly_amount, total_members, 1,
                      duration, committee_type, category, payment_frequency, admin_id))

                # Add admin as first member
                member_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO committee_members (id, committee_id, user_id, position)
                    VALUES (%s, %s, %s, %s)
                """, (member_id, committee_id, admin_id, 1))

                conn.commit()
                return True

        except psycopg2.Error as e:
            print(f"Committee creation error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_user_committees(self, user_id: str) -> List[Committee]:
        """Get committees for a user"""
        conn = self.get_connection()
        if not conn:
            # Fallback
            committees = []
            for member in self.fallback_data['committee_members'].values():
                if member['user_id'] == user_id:
                    committee = self.fallback_data['committees'].get(member['committee_id'])
                    if committee:
                        committees.append(committee)
            return committees

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT c.* FROM committees c
                    JOIN committee_members cm ON c.id = cm.committee_id
                    WHERE cm.user_id = %s
                    ORDER BY c.created_date DESC
                """, (user_id,))

                rows = cur.fetchall()
                return [Committee(**dict(row)) for row in rows]

        except psycopg2.Error as e:
            print(f"Get user committees error: {e}")
            return []
        finally:
            conn.close()

    def get_public_committees_for_user(self, user_id: str) -> List[Committee]:
        """Get public committees that user hasn't joined"""
        conn = self.get_connection()
        if not conn:
            # Fallback
            committees = []
            user_committee_ids = {member['committee_id'] for member in self.fallback_data['committee_members'].values() 
                                if member['user_id'] == user_id}

            for committee in self.fallback_data['committees'].values():
                if (committee.committee_type == 'public' and 
                    committee.id not in user_committee_ids and
                    committee.current_members < committee.total_members):
                    committees.append(committee)
            return committees

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT c.* FROM committees c
                    WHERE c.committee_type = 'public' 
                    AND c.current_members < c.total_members
                    AND c.id NOT IN (
                        SELECT cm.committee_id FROM committee_members cm 
                        WHERE cm.user_id = %s
                    )
                    ORDER BY c.created_date DESC
                """, (user_id,))

                rows = cur.fetchall()
                return [Committee(**dict(row)) for row in rows]

        except psycopg2.Error as e:
            print(f"Get public committees error: {e}")
            return []
        finally:
            conn.close()

    def join_committee(self, committee_id: str, user_id: str) -> bool:
        """Join a committee"""
        conn = self.get_connection()
        if not conn:
            # Fallback
            committee = self.fallback_data['committees'].get(committee_id)
            if committee and committee.current_members < committee.total_members:
                # Check if user already joined
                for member in self.fallback_data['committee_members'].values():
                    if member['committee_id'] == committee_id and member['user_id'] == user_id:
                        return False

                # Add member
                member_id = str(uuid.uuid4())
                position = committee.current_members + 1
                self.fallback_data['committee_members'][member_id] = {
                    'id': member_id,
                    'committee_id': committee_id,
                    'user_id': user_id,
                    'position': position,
                    'joined_date': datetime.now()
                }

                # Update committee
                committee.current_members += 1
                return True
            return False

        try:
            with conn.cursor() as cur:
                # Check if committee has space
                cur.execute("""
                    SELECT current_members, total_members FROM committees 
                    WHERE id = %s
                """, (committee_id,))

                result = cur.fetchone()
                if not result or result[0] >= result[1]:
                    return False

                # Get next position
                position = result[0] + 1

                # Add member
                member_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO committee_members (id, committee_id, user_id, position)
                    VALUES (%s, %s, %s, %s)
                """, (member_id, committee_id, user_id, position))

                # Update committee member count
                cur.execute("""
                    UPDATE committees SET current_members = current_members + 1
                    WHERE id = %s
                """, (committee_id,))

                conn.commit()
                return True

        except psycopg2.IntegrityError:
            conn.rollback()
            return False
        except psycopg2.Error as e:
            print(f"Join committee error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_member_position_in_committee(self, committee_id: str, user_id: str) -> int:
        """Get member's position in committee payout queue"""
        conn = self.get_connection()
        if not conn:
            # Fallback
            for member in self.fallback_data['committee_members'].values():
                if member['committee_id'] == committee_id and member['user_id'] == user_id:
                    return member['position']
            return 0

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT position FROM committee_members
                    WHERE committee_id = %s AND user_id = %s
                """, (committee_id, user_id))

                result = cur.fetchone()
                return result[0] if result else 0

        except psycopg2.Error as e:
            print(f"Get member position error: {e}")
            return 0
        finally:
            conn.close()

    def get_user_payment_history(self, user_id: str) -> List[Payment]:
        """Get payment history for user"""
        conn = self.get_connection()
        if not conn:
            # Fallback - return empty list
            return []

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM payments
                    WHERE user_id = %s
                    ORDER BY payment_date DESC
                """, (user_id,))

                rows = cur.fetchall()
                return [Payment(**dict(row)) for row in rows]

        except psycopg2.Error as e:
            print(f"Get payment history error: {e}")
            return []
        finally:
            conn.close()

    def update_user_profile(self, user_id: str, full_name: str, email: str, 
                           phone: str, cnic: Optional[str]) -> bool:
        """Update user profile"""
        conn = self.get_connection()
        if not conn:
            # Fallback
            user = self.fallback_data['users'].get(user_id)
            if user:
                user.full_name = full_name
                user.email = email
                user.phone = phone
                user.cnic = cnic
                return True
            return False

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE users 
                    SET full_name = %s, email = %s, phone = %s, cnic = %s
                    WHERE id = %s
                """, (full_name, email, phone, cnic, user_id))

                conn.commit()
                return cur.rowcount > 0

        except psycopg2.Error as e:
            print(f"Update profile error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def update_committee_settings(self, committee_id: str, title: str, description: Optional[str],
                                 status: str, payment_frequency: str, category: str, 
                                 committee_type: str) -> bool:
        """Update committee settings"""
        conn = self.get_connection()
        if not conn:
            # Fallback
            committee = self.fallback_data['committees'].get(committee_id)
            if committee:
                committee.title = title
                committee.description = description
                committee.status = status
                committee.payment_frequency = payment_frequency
                committee.category = category
                committee.committee_type = committee_type
                return True
            return False

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE committees 
                    SET title = %s, description = %s, status = %s, 
                        payment_frequency = %s, category = %s, committee_type = %s
                    WHERE id = %s
                """, (title, description, status, payment_frequency, category, committee_type, committee_id))

                conn.commit()
                return cur.rowcount > 0

        except psycopg2.Error as e:
            print(f"Update committee settings error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete_committee(self, committee_id: str) -> bool:
        """Delete committee and all related data"""
        conn = self.get_connection()
        if not conn:
            # Fallback
            if committee_id in self.fallback_data['committees']:
                del self.fallback_data['committees'][committee_id]
                # Remove committee members
                members_to_remove = [mid for mid, member in self.fallback_data['committee_members'].items() 
                                   if member['committee_id'] == committee_id]
                for mid in members_to_remove:
                    del self.fallback_data['committee_members'][mid]
                return True
            return False

        try:
            with conn.cursor() as cur:
                # Delete in proper order due to foreign key constraints
                cur.execute("DELETE FROM payments WHERE committee_id = %s", (committee_id,))
                cur.execute("DELETE FROM payouts WHERE committee_id = %s", (committee_id,))
                cur.execute("DELETE FROM committee_members WHERE committee_id = %s", (committee_id,))
                cur.execute("DELETE FROM committees WHERE id = %s", (committee_id,))

                conn.commit()
                return cur.rowcount > 0

        except psycopg2.Error as e:
            print(f"Delete committee error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_all_users_for_invitation(self, admin_id: str) -> List[Dict[str, Any]]:
        """Get all users for invitation purposes (only username and id)"""
        conn = self.get_connection()
        if not conn:
            # Fallback - exclude only the admin user
            users = []
            for user in self.fallback_data['users'].values():
                if user.id != admin_id:
                    users.append({
                        'id': user.id,
                        'username': user.username,
                        'trust_score': user.trust_score
                    })
            return users

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, username, trust_score
                    FROM users 
                    WHERE id != %s
                    ORDER BY username
                """, (admin_id,))

                rows = cur.fetchall()
                return [dict(row) for row in rows]

        except psycopg2.Error as e:
            print(f"Get users for invitation error: {e}")
            return []
        finally:
            conn.close()

    def send_committee_invitation(self, committee_id: str, invited_user_id: str, 
                                 invited_by_id: str, message: str = None) -> bool:
        """Send invitation to join private committee"""
        conn = self.get_connection()
        if not conn:
            # Fallback
            invitation_id = str(uuid.uuid4())
            if not hasattr(self, 'fallback_invitations'):
                self.fallback_invitations = {}

            self.fallback_invitations[invitation_id] = {
                'id': invitation_id,
                'committee_id': committee_id,
                'invited_user_id': invited_user_id,
                'invited_by_id': invited_by_id,
                'invitation_date': datetime.now(),
                'status': 'pending',
                'message': message,
                'response_date': None
            }
            return True

        try:
            with conn.cursor() as cur:
                invitation_id = str(uuid.uuid4())
                cur.execute("""
                    INSERT INTO committee_invitations 
                    (id, committee_id, invited_user_id, invited_by_id, message)
                    VALUES (%s, %s, %s, %s, %s)
                """, (invitation_id, committee_id, invited_user_id, invited_by_id, message))

                conn.commit()
                return True

        except psycopg2.IntegrityError:
            conn.rollback()
            return False
        except psycopg2.Error as e:
            print(f"Send invitation error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_user_invitations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending invitations for a user"""
        conn = self.get_connection()
        if not conn:
            # Fallback
            invitations = []
            if hasattr(self, 'fallback_invitations'):
                for inv in self.fallback_invitations.values():
                    if inv['invited_user_id'] == user_id and inv['status'] == 'pending':
                        committee = self.fallback_data['committees'].get(inv['committee_id'])
                        if committee:
                            invitations.append({
                                'id': inv['id'],
                                'committee_title': committee.title,
                                'committee_id': inv['committee_id'],
                                'invited_by_id': inv['invited_by_id'],
                                'invitation_date': inv['invitation_date'],
                                'message': inv['message']
                            })
            return invitations

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT ci.id, ci.committee_id, ci.invited_by_id, ci.invitation_date, 
                           ci.message, c.title as committee_title, u.username as invited_by_username
                    FROM committee_invitations ci
                    JOIN committees c ON ci.committee_id = c.id
                    JOIN users u ON ci.invited_by_id = u.id
                    WHERE ci.invited_user_id = %s AND ci.status = 'pending'
                    ORDER BY ci.invitation_date DESC
                """, (user_id,))

                rows = cur.fetchall()
                return [dict(row) for row in rows]

        except psycopg2.Error as e:
            print(f"Get user invitations error: {e}")
            return []
        finally:
            conn.close()

    def respond_to_invitation(self, invitation_id: str, response: str) -> bool:
        """Respond to committee invitation (accept/reject)"""
        conn = self.get_connection()
        if not conn:
            # Fallback
            if hasattr(self, 'fallback_invitations') and invitation_id in self.fallback_invitations:
                invitation = self.fallback_invitations[invitation_id]
                invitation['status'] = response
                invitation['response_date'] = datetime.now()

                # If accepted, join the committee
                if response == 'accepted':
                    return self.join_committee(invitation['committee_id'], invitation['invited_user_id'])
                return True
            return False

        try:
            with conn.cursor() as cur:
                # Update invitation status
                cur.execute("""
                    UPDATE committee_invitations 
                    SET status = %s, response_date = CURRENT_TIMESTAMP
                    WHERE id = %s AND status = 'pending'
                """, (response, invitation_id))

                if cur.rowcount == 0:
                    return False

                # If accepted, get invitation details and join committee
                if response == 'accepted':
                    cur.execute("""
                        SELECT committee_id, invited_user_id
                        FROM committee_invitations
                        WHERE id = %s
                    """, (invitation_id,))

                    result = cur.fetchone()
                    if result:
                        committee_id, user_id = result
                        # Join the committee
                        success = self._join_committee_internal(cur, committee_id, user_id)
                        if not success:
                            conn.rollback()
                            return False

                conn.commit()
                return True

        except psycopg2.Error as e:
            print(f"Respond to invitation error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def _join_committee_internal(self, cur, committee_id: str, user_id: str) -> bool:
        """Internal method to join committee (used within transactions)"""
        try:
            # Check if committee has space
            cur.execute("""
                SELECT current_members, total_members FROM committees 
                WHERE id = %s
            """, (committee_id,))

            result = cur.fetchone()
            if not result or result[0] >= result[1]:
                return False

            # Get next position
            position = result[0] + 1

            # Add member
            member_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO committee_members (id, committee_id, user_id, position)
                VALUES (%s, %s, %s, %s)
            """, (member_id, committee_id, user_id, position))

            # Update committee member count
            cur.execute("""
                UPDATE committees SET current_members = current_members + 1
                WHERE id = %s
            """, (committee_id,))

            return True

        except psycopg2.IntegrityError:
            return False

    def get_committee_invitations(self, committee_id: str) -> List[Dict[str, Any]]:
        """Get all invitations for a committee"""
        conn = self.get_connection()
        if not conn:
            # Fallback
            invitations = []
            if hasattr(self, 'fallback_invitations'):
                for inv in self.fallback_invitations.values():
                    if inv['committee_id'] == committee_id:
                        user = self.fallback_data['users'].get(inv['invited_user_id'])
                        if user:
                            invitations.append({
                                'id': inv['id'],
                                'invited_username': user.username,
                                'status': inv['status'],
                                'invitation_date': inv['invitation_date'],
                                'response_date': inv['response_date']
                            })
            return invitations

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT ci.id, u.username as invited_username, ci.status, 
                           ci.invitation_date, ci.response_date
                    FROM committee_invitations ci
                    JOIN users u ON ci.invited_user_id = u.id
                    WHERE ci.committee_id = %s
                    ORDER BY ci.invitation_date DESC
                """, (committee_id,))

                rows = cur.fetchall()
                return [dict(row) for row in rows]

        except psycopg2.Error as e:
            print(f"Get committee invitations error: {e}")
            return []
        finally:
            conn.close()

    def get_pending_join_requests(self, committee_id: str) -> List[Dict[str, Any]]:
        """Get pending join requests for a private committee"""
        conn = self.get_connection()
        if not conn:
            # Fallback - return mock data for demo
            return [
                {
                    'id': 'req_1',
                    'name': 'Ahmad Hassan',
                    'trust_score': 88,
                    'requested_date': '2025-01-29'
                },
                {
                    'id': 'req_2', 
                    'name': 'Fatima Khan',
                    'trust_score': 92,
                    'requested_date': '2025-01-28'
                }
            ]

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT ci.id, u.full_name as name, u.trust_score,
                           ci.invitation_date::date as requested_date
                    FROM committee_invitations ci
                    JOIN users u ON ci.invited_user_id = u.id
                    WHERE ci.committee_id = %s AND ci.status = 'pending'
                    ORDER BY ci.invitation_date DESC
                """, (committee_id,))

                rows = cur.fetchall()
                return [dict(row) for row in rows]

        except psycopg2.Error as e:
            print(f"Get pending join requests error: {e}")
            return []
        finally:
            conn.close()

    def approve_join_request(self, request_id: str, committee_id: str) -> bool:
        """Approve a join request"""
        return self.respond_to_invitation(request_id, 'accepted')

    def reject_join_request(self, request_id: str) -> bool:
        """Reject a join request"""
        return self.respond_to_invitation(request_id, 'rejected')

    def get_committee_activity(self, committee_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activity for a committee"""
        conn = self.get_connection()
        if not conn:
            # Fallback - return mock recent activity
            return [
                {
                    'activity_type': 'member_joined',
                    'description': 'New member Ahmad Hassan joined the committee',
                    'timestamp': '2025-01-29 14:30:00',
                    'user_name': 'Ahmad Hassan'
                },
                {
                    'activity_type': 'payment_received',
                    'description': 'Payment received from Fatima Khan - Rs. 10,000',
                    'timestamp': '2025-01-29 10:15:00',
                    'user_name': 'Fatima Khan'
                },
                {
                    'activity_type': 'committee_created',
                    'description': 'Committee was created',
                    'timestamp': '2025-01-28 16:45:00',
                    'user_name': 'Admin'
                }
            ]

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get member joins
                cur.execute("""
                    SELECT 'member_joined' as activity_type,
                           CONCAT(u.full_name, ' joined the committee') as description,
                           cm.joined_date as timestamp,
                           u.full_name as user_name
                    FROM committee_members cm
                    JOIN users u ON cm.user_id = u.id
                    WHERE cm.committee_id = %s
                    
                    UNION ALL
                    
                    SELECT 'payment_received' as activity_type,
                           CONCAT('Payment received from ', u.full_name, ' - Rs. ', p.amount) as description,
                           p.payment_date as timestamp,
                           u.full_name as user_name
                    FROM payments p
                    JOIN users u ON p.user_id = u.id
                    WHERE p.committee_id = %s AND p.status = 'completed'
                    
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (committee_id, committee_id, limit))

                rows = cur.fetchall()
                return [dict(row) for row in rows]

        except psycopg2.Error as e:
            print(f"Get committee activity error: {e}")
            return []
        finally:
            conn.close()