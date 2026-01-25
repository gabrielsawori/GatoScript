# banking/models.py
from django.db import models
from django.contrib.auth.models import User
import random
import datetime

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

    TIPE_AKUN = (
        ('PRIBADI', 'Rekening Pribadi'),
        ('BISNIS', 'Rekening Bisnis'),
    )

    nasabah = models.ForeignKey(Nasabah, on_delete=models.CASCADE, related_name='rekening')
    no_rekening = models.CharField(max_length=10, unique=True, editable=False)
    saldo = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    jenis = models.CharField(max_length=10, choices=JENIS_TABUNGAN, default='SILVER')
    tipe = models.CharField(max_length=10, choices=TIPE_AKUN, default='PRIBADI')
    aktif = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Generate no rekening otomatis jika belum ada (10 digit acak)
        if not self.no_rekening:
            self.no_rekening = str(random.randint(1000000000, 9999999999))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.no_rekening} - {self.nasabah.nama_lengkap} ({self.get_tipe_display()})"

class Tagihan(models.Model):
    JENIS_LAYANAN = (
        ('LISTRIK', 'Listrik / PLN'),
        ('INTERNET', 'Internet / Wifi'),
        ('PAJAK', 'Pajak'),
        ('BELANJA', 'Belanja / E-Commerce'),
        ('LAINNYA', 'Lainnya'),
    )

    STATUS_TAGIHAN = (
        ('BELUM', 'Belum Dibayar'),
        ('LUNAS', 'Lunas'),
    )

    nomor_tagihan = models.CharField(max_length=20, unique=True, editable=False)
    pembuat = models.ForeignKey(Rekening, on_delete=models.CASCADE, related_name='tagihan_dibuat')
    jenis_layanan = models.CharField(max_length=20, choices=JENIS_LAYANAN)
    jumlah = models.DecimalField(max_digits=15, decimal_places=2)
    deskripsi = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=STATUS_TAGIHAN, default='BELUM')

    pembayar = models.ForeignKey(Rekening, on_delete=models.SET_NULL, null=True, blank=True, related_name='tagihan_dibayar')
    waktu_dibuat = models.DateTimeField(auto_now_add=True)
    waktu_dibayar = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.nomor_tagihan:
            # Generate format: INV-YYMMDD-RANDOM
            now = datetime.datetime.now().strftime("%y%m%d")
            rand = random.randint(1000, 9999)
            self.nomor_tagihan = f"INV{now}{rand}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nomor_tagihan} - {self.deskripsi}"

class Transaksi(models.Model):
    JENIS_TRANSAKSI = (
        ('SETOR', 'Setor Tunai'),
        ('TARIK', 'Tarik Tunai'),
        ('TRANSFER', 'Transfer Sesama'),
        ('BAYAR', 'Pembayaran Tagihan'),
    )

    rekening = models.ForeignKey(Rekening, on_delete=models.CASCADE)
    teller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) # Siapa yang melayani
    jenis = models.CharField(max_length=10, choices=JENIS_TRANSAKSI)
    nominal = models.DecimalField(max_digits=15, decimal_places=2)
    keterangan = models.CharField(max_length=100, blank=True)
    waktu = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.jenis} - {self.nominal}"
