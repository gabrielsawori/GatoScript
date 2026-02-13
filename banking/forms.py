from django import forms
from .models import Nasabah, Tagihan

class NasabahForm(forms.ModelForm):
    # Field tambahan untuk memilih tipe akun saat pendaftaran nasabah baru
    TIPE_AKUN = (
        ('PRIBADI', 'Rekening Pribadi'),
        ('BISNIS', 'Rekening Bisnis'),
    )
    tipe_akun = forms.ChoiceField(choices=TIPE_AKUN, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Nasabah
        fields = ['nama_lengkap', 'nik', 'alamat', 'no_telepon']
        widgets = {
            'nama_lengkap': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Lengkap'}),
            'nik': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIK (KTP)'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Alamat Lengkap'}),
            'no_telepon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'No. Telepon'}),
        }

class TagihanForm(forms.ModelForm):
    no_rekening_bisnis = forms.CharField(
        max_length=20,
        label="No. Rekening Bisnis (Pembuat)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan No. Rekening Bisnis'})
    )

    class Meta:
        model = Tagihan
        fields = ['jenis_layanan', 'jumlah', 'deskripsi']
        widgets = {
            'jenis_layanan': forms.Select(attrs={'class': 'form-select'}),
            'jumlah': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Jumlah Tagihan'}),
            'deskripsi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Keterangan Tagihan'}),
        }

class BayarTagihanForm(forms.Form):
    nomor_tagihan = forms.CharField(
        max_length=30,
        label="Nomor Tagihan",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: INV...'})
    )
    no_rekening_pembayar = forms.CharField(
        max_length=20,
        label="No. Rekening Pembayar",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan No. Rekening Anda'})
    )
