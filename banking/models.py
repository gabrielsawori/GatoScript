# banking/models.py
from django.db import models
from django.contrib.auth.models import User
import random

class Nasabah(models.Model):
    # Data diri nasabah (dikelola CS)
    nama_lengkap = models.CharField(max_length=100)
    nik = models.CharField(max_length=16, unique=True, help_text="Nomor KTP")
    alamat = models.TextField()
    no_telepon = models.CharField(max_length=15)
    tanggal_gabung = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_lengkap

class Rekening(models.Model):
    JENIS_TABUNGAN = (
        ('SILVER', 'Galaxy Silver'),
        ('GOLD', 'Galaxy Gold'),
        ('PLATINUM', 'Galaxy Platinum'),
    )

    nasabah = models.ForeignKey(Nasabah, on_delete=models.CASCADE, related_name='rekening')
    no_rekening = models.CharField(max_length=10, unique=True, editable=False)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    jenis = models.CharField(max_length=10, choices=JENIS_TABUNGAN, default='SILVER')
    aktif = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Generate no rekening otomatis jika belum ada (10 digit acak)
        if not self.no_rekening:
            self.no_rekening = str(random.randint(1000000000, 9999999999))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.no_rekening} - {self.nasabah.nama_lengkap}"

class Transaksi(models.Model):
    JENIS_TRANSAKSI = (
        ('SETOR', 'Setor Tunai'),
        ('TARIK', 'Tarik Tunai'),
        ('TRANSFER', 'Transfer Sesama'),
    )

    rekening = models.ForeignKey(Rekening, on_delete=models.CASCADE)
    teller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) # Siapa yang melayani
    jenis = models.CharField(max_length=10, choices=JENIS_TRANSAKSI)
    nominal = models.DecimalField(max_digits=12, decimal_places=2)
    keterangan = models.CharField(max_length=100, blank=True)
    waktu = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.jenis} - {self.nominal}"