from django import forms
from django.forms import ValidationError


class ExpenseForm(forms.Form):
    e_id = forms.CharField(required=True)
    current_user = forms.CharField(widget=forms.HiddenInput)
    type = forms.CharField(required=True, label="收支")
    category = forms.CharField(required=True, label="分類")
    date = forms.DateField(required=True, label="日期")
    amount = forms.FloatField(required=True, label="金額")
    desc = forms.CharField(
        required=False, label="備註", widget=forms.Textarea(attrs={"rows": 3})
    )

    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
