"""
Models of validation app.
"""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from wapyce.core.models import CoreModel
from .validators import validate_github_url

# Create your models here.

class Site(CoreModel):
    """
    The Site class is a model that represents a site that will be validated.
    """

    ACTIVE = 0
    DEACTIVATED = 1
    STATUS_CHOICES = (
        (ACTIVE, _('Active')),
        (DEACTIVATED, _('Deactivated')),
    )

    name = models.CharField(max_length=100, verbose_name=_('Name'))
    base_url = models.URLField(unique=True, verbose_name=_('Base URL'))
    github_url = models.URLField(
        unique=True,
        verbose_name=_('Github repository'),
        validators=[validate_github_url]
    )
    status = models.IntegerField(
        default=ACTIVE,
        choices=STATUS_CHOICES,
        verbose_name=_('Site status')
    )

    class Meta:
        """
        Metadata class of site model.
        """

        verbose_name = _('Site')

    def __str__(self):
        return '{} ({})'.format(self.name, self.base_url)

    @property
    def active(self):
        """
        Check that the site is active.

        :return: True if the site is active or False if not.
        :rtype: bool
        """

        return self.status == Site.ACTIVE

    @property
    def canceled(self):
        """
        Check that the site is deactivated.

        :return: True if the site is deactivated or False if not.
        :rtype: bool
        """

        return self.status == Site.DEACTIVATED

class Validation(CoreModel):
    """
    The Validation class is a model that represents a validation of site.
    """

    STARTED = 0
    CANCELED = 1
    FINISHED = 2
    STATUS_CHOICES = (
        (STARTED, _('Started')),
        (CANCELED, _('Canceled')),
        (FINISHED, _('Finished')),
    )

    site = models.ForeignKey(
        Site,
        on_delete=models.PROTECT,
        verbose_name=_('Site')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_('User')
    )
    start_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Start date')
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('End date')
    )
    status = models.IntegerField(
        default=STARTED,
        choices=STATUS_CHOICES,
        verbose_name=_('Validation status')
    )

    class Meta:
        """
        Metadata class of validation model.
        """

        verbose_name = _('Validation')

    def clean(self):
        super(Validation, self).clean()

        query = Validation.objects.filter(
            user=self.user,
            status=Validation.STARTED
        )
        if self.id:
            query = query.exclude(id=self.id)
        if query.exists():
            raise ValidationError(
                _('Already exists a validation for the same user.')
            )

    @property
    def started(self):
        """
        Check that the validation is started.

        :return: True if the validation is started or False if not.
        :rtype: bool
        """

        return self.status == Validation.STARTED

    @property
    def canceled(self):
        """
        Check that the validation is canceled.

        :return: True if the validation is canceled or False if not.
        :rtype: bool
        """

        return self.status == Validation.CANCELED

    @property
    def finished(self):
        """
        Check that the validation is finished.

        :return: True if the validation is finished or False if not.
        :rtype: bool
        """

        return self.status == Validation.FINISHED

    def cancel_validation(self):
        """
        Cancel the validation, when the user not finish the validation of all
        pages of site.
        """

        if self.started:
            self.status = Validation.CANCELED
            self.end_date = timezone.now()
            self.save()
        else:
            raise ValidationError(
                _('Only started validations can be canceled.')
            )

    def finish_validation(self):
        """
        Finish the validation, when the user validate all pages of site.
        """

        if self.started:
            if not Page.objects.filter(validation_site=self).exists():
                raise ValidationError(
                    _(
                        'The validation can be finished when at least one page'
                        + ' has validated.'
                    )
                )

            self.status = Validation.FINISHED
            self.end_date = timezone.now()
            self.save()
        else:
            raise ValidationError(
                _('Only started validations can be finished.')
            )

class Page(CoreModel):
    """
    The Page class is a model that represents a validated page of site.
    """

    validation_site = models.ForeignKey(
        Validation,
        on_delete=models.PROTECT,
        verbose_name=_('Validation')
    )
    page_url = models.URLField(verbose_name=_('Page URL'))

    class Meta:
        """
        Metadata class of validated page model.
        """

        verbose_name = _('Validated page')
        unique_together = ('validation_site', 'page_url')

    def __str__(self):
        return self.page_url

    def clean(self):
        super(Page, self).clean()

        base_url = self.validation_site.site.base_url
        if not self.page_url.startswith(base_url):
            raise ValidationError(
                _('The page URL must starts with "{}".').format(base_url)
            )
