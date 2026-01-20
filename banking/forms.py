from django import forms
from .models import Nasabah

class NasabahForm(forms.ModelForm):
    class Meta:
        model = Nasabah
        fields = ['nama_lengkap', 'nik', 'alamat', 'no_telepon']
        widgets = {
            'nama_lengkap': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Lengkap'}),
            'nik': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIK (KTP)'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Alamat Lengkap'}),
            'no_telepon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'No. Telepon'}),
        }
