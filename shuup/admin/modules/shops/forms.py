# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2016, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the AGPLv3 license found in the
# LICENSE file in the root directory of this source tree.
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from shuup import configuration
from shuup.admin.forms.widgets import MediaChoiceWidget
from shuup.core.models import MutableAddress, Shop
from shuup.core.utils.form_mixins import ProtectedFieldsMixin
from shuup.utils.i18n import get_current_babel_locale
from shuup.utils.multilanguage_model_form import MultiLanguageModelForm


class ShopBaseForm(ProtectedFieldsMixin, MultiLanguageModelForm):
    change_protect_field_text = _("This field cannot be changed since there are existing orders for this shop.")

    class Meta:
        model = Shop
        exclude = ("owner", "options", "contact_address")

    def __init__(self, **kwargs):
        initial_languages = [i[0] for i in kwargs.get("languages", [])]
        super(ShopBaseForm, self).__init__(**kwargs)
        self.fields["logo"].widget = MediaChoiceWidget(clearable=True)
        locale = get_current_babel_locale()
        self.fields["currency"] = forms.ChoiceField(
            choices=sorted(locale.currencies.items()),
            required=True,
            label=_("Currency")
        )
        self.fields["languages"] = forms.MultipleChoiceField(
            choices=settings.LANGUAGES,
            initial=initial_languages,
            required=True,
            label=_("Languages")
        )
        self.disable_protected_fields()

    def save(self):
        obj = super(ShopBaseForm, self).save()
        languages = set(self.cleaned_data.get("languages"))
        shop_languages = [(code, name) for code, name in settings.LANGUAGES if code in languages]
        configuration.set(obj, "languages", shop_languages)
        return obj


class ContactAddressForm(forms.ModelForm):
    class Meta:
        model = MutableAddress
        fields = (
            "prefix", "name", "suffix", "name_ext",
            "phone", "email",
            "street", "street2", "street3",
            "postal_code", "city",
            "region_code", "region",
            "country"
        )


class ShopLanguagesWizardForm(forms.Form):
    languages = forms.MultipleChoiceField(choices=settings.LANGUAGES, required=True, label=_("Supported Languages"))


class ShopWizardForm(MultiLanguageModelForm):
    class Meta:
        model = Shop
        fields = ("public_name", "currency", "prices_include_tax")
        labels = {
            "public_name": _("Shop name")
        }

    def __init__(self, **kwargs):
        super(ShopWizardForm, self).__init__(**kwargs)
        locale = get_current_babel_locale()
        self.fields["prices_include_tax"].help_text = _(
            "Show storefront products with tax pre-calculated into the price. "
            "Note this behavior can be overridden for customer groups."
        )
        self.fields["currency"] = forms.ChoiceField(
            choices=sorted(locale.currencies.items()),
            required=True,
            label=_("Currency")
        )

    def save(self):
        obj = super(ShopWizardForm, self).save()
        obj.name = obj.public_name
        obj.save()


class ShopAddressWizardForm(forms.ModelForm):
    class Meta:
        model = MutableAddress
        fields = ("name", "street", "postal_code", "city", "country", "region_code", "region")
        widgets = {
            "region_code": forms.Select(choices=[])
        }
        labels = {
            "name": _("Shop Owner Name"),
            "postal_code": _("Zip/Postal code"),
            "region_code": _("State/Province")
        }
