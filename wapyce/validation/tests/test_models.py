"""
Tests for models of validation app.
"""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase

from wapyce.validation.models import Site
from wapyce.validation.models import Page
from wapyce.validation.models import Validation

# Create your tests here.
class TestSite(TestCase):
    """
    Test for site model.
    """

    def tearDown(self):
        sites = Site.objects.all()
        for site in sites:
            site.delete()

    def test_normal_save(self):
        """
        Test if django persist a valid site object.
        """

        site = Site(
            name='Site',
            base_url='http://www.example.com/',
            github_url='https://github.com/carlsonsantana/wapyce'
        )
        site.full_clean()
        site.save()
        self.assertEqual(site, Site.objects.all().order_by('?').first())

    def test_unique_base_url(self):
        """
        Test unique base url constraint.
        """

        with transaction.atomic(), self.assertRaises(IntegrityError):
            site1 = Site(
                name='Site1',
                base_url='http://www.example.com/',
                github_url='https://github.com/carlsonsantana/wapyce'
            )
            site1.save()
            site2 = Site(
                name='Site2',
                base_url='http://www.example.com/',
                github_url='https://github.com/carlsonsantana/wapyce1'
            )
            site2.save()

    def test_unique_github_url(self):
        """
        Test unique github url constraint.
        """

        with transaction.atomic(), self.assertRaises(IntegrityError):
            site1 = Site(
                name='Site1',
                base_url='http://www.example1.com/',
                github_url='https://github.com/carlsonsantana/wapyce'
            )
            site1.save()
            site2 = Site(
                name='Site2',
                base_url='http://www.example2.com/',
                github_url='https://github.com/carlsonsantana/wapyce'
            )
            site2.save()

    def test_valid_github_url(self):
        """
        Test if django persists a invalid github url.
        """

        with self.assertRaises(ValidationError):
            site = Site(
                name='Site',
                base_url='http://www.example.com/',
                github_url='https://www.w3.org/TR/WCAG20/'
            )
            site.full_clean()
            site.save()

class TestValidation(TestCase):
    """
    Test for validation model.
    """

    def setUp(self):
        self.site = Site(
            name='Site',
            base_url='http://www.example.com/',
            github_url='https://github.com/carlsonsantana/wapyce'
        )
        self.site.save()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@github.com',
            password='user1password'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@github.com',
            password='user2password'
        )

    def tearDown(self):
        validations = Validation.objects.filter(site=self.site)
        for validation in validations:
            pages = Page.objects.filter(validation_site=validation)
            for page in pages:
                page.delete()
            validation.delete()
        self.site.delete()
        self.user1.delete()
        self.user2.delete()

    def test_normal_save(self):
        """
        Test if django persist a valid validation object.
        """

        validation1 = Validation(site=self.site, user=self.user1)
        validation1.save()
        validation1.cancel_validation()
        validation2 = Validation(site=self.site, user=self.user2)
        validation2.save()
        page = Page(validation_site=validation2, page_url=self.site.base_url)
        page.save()
        validation2.finish_validation()

        self.assertEqual(2, Validation.objects.all().count())

    def test_unique_validation_user(self):
        """
        Test unique active validation by user constraint.
        """

        with self.assertRaises(ValidationError):
            validation1 = Validation(site=self.site, user=self.user1)
            validation1.save()
            validation2 = Validation(site=self.site, user=self.user1)
            validation2.clean()
            validation2.save()

class TestPage(TestCase):
    """
    Test for validated page model.
    """

    def setUp(self):
        self.site = Site(
            name='Site',
            base_url='http://www.example.com/',
            github_url='https://github.com/carlsonsantana/wapyce'
        )
        self.site.save()
        self.user = User.objects.create_user(
            username='user',
            email='user@github.com',
            password='userpassword'
        )
        self.validation = Validation(site=self.site, user=self.user)
        self.validation.save()

    def tearDown(self):
        pages = Page.objects.filter(validation_site=self.validation)
        for page in pages:
            page.delete()
        self.validation.delete()
        self.site.delete()
        self.user.delete()

    def test_normal_save(self):
        """
        Test if django persist a valid validated page object.
        """

        page = Page(
            validation_site=self.validation,
            page_url=self.site.base_url
        )
        page.clean()
        page.save()
        self.assertEqual(
            page,
            Page.objects.filter(
                validation_site=self.validation
            ).order_by('?').first()
        )

    def test_valid_page_url(self):
        """
        Test a valid page url constraint.
        """

        with self.assertRaises(ValidationError):
            page = Page(
                validation_site=self.validation,
                page_url='https://github.com/carlsonsantana/wapyce'
            )
            page.clean()
            page.save()
