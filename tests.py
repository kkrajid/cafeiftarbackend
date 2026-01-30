"""
Comprehensive test suite for Cafe Iftar Backend
Tests all API endpoints and finds bugs
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.branches.models import Branch
from apps.tables.models import Table
from apps.reservations.models import Reservation
from apps.menu.models import MenuItem
from apps.deals.models import Deal
from apps.inquiries.models import Inquiry
from apps.gallery.models import GalleryImage
from datetime import date, time, timedelta
from decimal import Decimal

User = get_user_model()

class AuthenticationTests(TestCase):
    """Test authentication endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
    
    def test_login_success(self):
        """Test successful login"""
        response = self.client.post('/api/auth/login/', {
            'username': 'testadmin',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())
    
    def test_login_invalid_credentials(self):
        """Test login with wrong password"""
        response = self.client.post('/api/auth/login/', {
            'username': 'testadmin',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_current_user(self):
        """Test getting current user details"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['username'], 'testadmin')
    
    def test_get_current_user_unauthorized(self):
        """Test getting user without authentication"""
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BranchTests(TestCase):
    """Test branch management endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='pass123',
            role='admin'
        )
        self.branch = Branch.objects.create(
            name='Test Branch',
            address='123 Test St',
            phone='+91 1234567890',
            hours='9 AM - 10 PM',
            status='active'
        )
    
    def test_list_branches_public(self):
        """Test public can list branches"""
        response = self.client.get('/api/branches/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # DRF returns paginated response: {"count": N, "results": [...]}
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            self.assertEqual(len(data['results']), 1)
        else:
            self.assertEqual(len(data), 1)
    
    def test_create_branch_requires_auth(self):
        """Test creating branch requires authentication"""
        response = self.client.post('/api/branches/', {
            'name': 'New Branch',
            'address': '456 New St',
            'phone': '+91 9876543210',
            'hours': '10 AM - 11 PM'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_branch_with_auth(self):
        """Test admin can create branch"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/branches/', {
            'name': 'New Branch',
            'address': '456 New St',
            'phone': '+919876543210',
            'hours': '10 AM - 11 PM',
            'status': 'active'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TableTests(TestCase):
    """Test table management and availability"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser('admin', password='pass')
        self.branch = Branch.objects.create(
            name='Test Branch',
            address='123 St',
            phone='1234567890',
            hours='9-10'
        )
        self.table = Table.objects.create(
            table_id='T1',
            name='Table 1',
            seats=4,
            status='active',
            location='Main Hall',
            branch=self.branch
        )
    
    def test_list_tables_by_branch(self):
        """Test filtering tables by branch"""
        response = self.client.get(f'/api/tables/?branch={self.branch.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            self.assertEqual(len(data['results']), 1)
        else:
            self.assertEqual(len(data), 1)
    
    def test_check_availability_no_reservations(self):
        """Test availability when no reservations exist"""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        response = self.client.get(
            f'/api/tables/availability/?branch={self.branch.id}&date={tomorrow}&time=19:00&guests=2'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        if isinstance(data, dict) and 'results' in data:
            self.assertGreater(len(data['results']), 0)
        else:
            self.assertGreater(len(data), 0)
    
    def test_check_availability_with_reservation(self):
        """Test availability excludes reserved tables"""
        tomorrow = date.today() + timedelta(days=1)
        Reservation.objects.create(
            branch=self.branch,
            table=self.table,
            customer_name='Test',
            phone='1234567890',
            email='test@test.com',
            date=tomorrow,
            time=time(19, 0),
            guests=4,
            status='confirmed'
        )
        response = self.client.get(
            f'/api/tables/availability/?branch={self.branch.id}&date={tomorrow.isoformat()}&time=19:00&guests=2'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should not include the reserved table
        table_ids = [t['id'] for t in response.json()]
        self.assertNotIn(self.table.id, table_ids)


class ReservationTests(TestCase):
    """Test reservation creation and management"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser('admin', password='pass')
        self.branch = Branch.objects.create(
            name='Test Branch',
            address='123 St',
            phone='1234567890',
            hours='9-10'
        )
        self.table = Table.objects.create(
            table_id='T1',
            name='Table 1',
            seats=4,
            status='active',
            location='Main',
            branch=self.branch
        )
    
    def test_create_reservation_public(self):
        """Test public can create reservation"""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        response = self.client.post('/api/reservations/', {
            'branch': self.branch.id,
            'table': self.table.id,
            'customer_name': 'John Doe',
            'phone': '+91 9876543210',
            'email': 'john@example.com',
            'date': tomorrow,
            'time': '19:00:00',
            'guests': 4,
            'special_requests': 'Window seat'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIn('confirmation_id', data)
        self.assertTrue(data['confirmation_id'].startswith('CI'))
    
    def test_reservation_generates_unique_confirmation_id(self):
        """Test each reservation gets unique confirmation ID"""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        res1 = self.client.post('/api/reservations/', {
            'branch': self.branch.id,
            'table': self.table.id,
            'customer_name': 'User 1',
            'phone': '1111111111',
            'email': 'user1@test.com',
            'date': tomorrow,
            'time': '18:00:00',
            'guests': 2
        })
        res2 = self.client.post('/api/reservations/', {
            'branch': self.branch.id,
            'table': self.table.id,
            'customer_name': 'User 2',
            'phone': '2222222222',
            'email': 'user2@test.com',
            'date': tomorrow,
            'time': '20:00:00',
            'guests': 2
        })
        self.assertNotEqual(
            res1.json()['confirmation_id'],
            res2.json()['confirmation_id']
        )
    
    def test_lookup_by_confirmation_id(self):
        """Test looking up reservation by confirmation ID"""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        create_response = self.client.post('/api/reservations/', {
            'branch': self.branch.id,
            'table': self.table.id,
            'customer_name': 'Test User',
            'phone': '1234567890',
            'email': 'test@test.com',
            'date': tomorrow,
            'time': '19:00:00',
            'guests': 2
        })
        conf_id = create_response.json()['confirmation_id']
        
        lookup_response = self.client.get(f'/api/reservations/by_confirmation/?confirmation_id={conf_id}')
        self.assertEqual(lookup_response.status_code, status.HTTP_200_OK)
        self.assertEqual(lookup_response.json()['confirmation_id'], conf_id)
    
    def test_confirm_reservation_requires_auth(self):
        """Test confirming reservation requires admin"""
        reservation = Reservation.objects.create(
            branch=self.branch,
            table=self.table,
            customer_name='Test',
            phone='1234567890',
            email='test@test.com',
            date=date.today() + timedelta(days=1),
            time=time(19, 0),
            guests=2,
            status='pending'
        )
        response = self.client.patch(f'/api/reservations/{reservation.id}/confirm/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_confirm_reservation_as_admin(self):
        """Test admin can confirm reservation"""
        self.client.force_authenticate(user=self.admin)
        reservation = Reservation.objects.create(
            branch=self.branch,
            table=self.table,
            customer_name='Test',
            phone='1234567890',
            email='test@test.com',
            date=date.today() + timedelta(days=1),
            time=time(19, 0),
            guests=2,
            status='pending'
        )
        response = self.client.patch(f'/api/reservations/{reservation.id}/confirm/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, 'confirmed')


class MenuTests(TestCase):
    """Test menu item management"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser('admin', password='pass')
        self.menu_item = MenuItem.objects.create(
            name='Test Dish',
            description='Delicious test dish',
            category='Main Course',
            price=Decimal('500.00'),  # Fixed: decimal not string
            is_veg=True,
            is_spicy=False,
            status='in_stock'
        )
    
    def test_list_menu_public(self):
        """Test public can view menu"""
        response = self.client.get('/api/menu/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.json()), 0)
    
    def test_filter_by_category(self):
        """Test filtering menu by category"""
        response = self.client.get('/api/menu/?category=Main Course')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_by_veg(self):
        """Test filtering vegetarian items"""
        response = self.client.get('/api/menu/?is_veg=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DealTests(TestCase):
    """Test promotional deals"""
    
    def setUp(self):
        self.client = APIClient()
        self.deal = Deal.objects.create(
            title='Test Deal',
            description='Test description',
            code='TEST15',
            discount_type='percentage',  # Fixed: structured discount
            discount_value=Decimal('15.00'),
            valid_from=date.today(),  # Fixed: proper dates
            valid_until=date.today() + timedelta(days=30),
            tag='Limited',
            status='active'
        )
    
    def test_validate_active_code(self):
        """Test validating an active promo code"""
        response = self.client.post('/api/deals/validate/', {'code': 'TEST15'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()['valid'])
    
    def test_validate_invalid_code(self):
        """Test validating non-existent code"""
        response = self.client.post('/api/deals/validate/', {'code': 'INVALID'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.json()['valid'])
    
    def test_validate_expired_code(self):
        """Test validating expired code"""
        self.deal.status = 'expired'
        self.deal.save()
        response = self.client.post('/api/deals/validate/', {'code': 'TEST15'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class InquiryTests(TestCase):
    """Test customer inquiries"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser('admin', password='pass')
    
    def test_create_inquiry_public(self):
        """Test public can submit inquiry"""
        response = self.client.post('/api/inquiries/', {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message content'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_inquiries_requires_auth(self):
        """Test listing inquiries requires admin"""
        response = self.client.get('/api/inquiries/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_status_requires_auth(self):
        """Test updating inquiry status requires admin"""
        inquiry = Inquiry.objects.create(
            name='Test',
            email='test@test.com',
            subject='Test',
            message='Message',
            status='new'
        )
        response = self.client.patch(
            f'/api/inquiries/{inquiry.id}/update_status/',
            {'status': 'read'}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GalleryTests(TestCase):
    """Test gallery image management"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_list_gallery_public(self):
        """Test public can view gallery"""
        response = self.client.get('/api/gallery/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_by_category(self):
        """Test filtering gallery by category"""
        response = self.client.get('/api/gallery/?category=culinary')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
