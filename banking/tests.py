from django.test import TestCase, Client
from django.urls import reverse
from .models import Nasabah, Rekening, Transaksi

class BankingTests(TestCase):
    def setUp(self):
        self.nasabah1 = Nasabah.objects.create(
            nama_lengkap="Andi", nik="123456789", no_telepon="08123456789", alamat="Jl. A"
        )
        self.rekening1 = Rekening.objects.create(nasabah=self.nasabah1, jenis='SILVER', saldo=100000)
        # Force specific number for easy testing, but since it's auto-generated if empty, we update it
        self.rekening1.no_rekening = "1111111111"
        self.rekening1.save()

        self.nasabah2 = Nasabah.objects.create(
            nama_lengkap="Budi", nik="987654321", no_telepon="08987654321", alamat="Jl. B"
        )
        self.rekening2 = Rekening.objects.create(nasabah=self.nasabah2, jenis='GOLD', saldo=50000)
        self.rekening2.no_rekening = "2222222222"
        self.rekening2.save()

        self.client = Client()

    def test_setor_tunai(self):
        response = self.client.post(reverse('setor_tunai'), {
            'no_rekening': '1111111111',
            'nominal': '50000'
        })
        self.rekening1.refresh_from_db()
        self.assertEqual(self.rekening1.saldo, 150000)
        self.assertTrue(Transaksi.objects.filter(rekening=self.rekening1, jenis='SETOR', nominal=50000).exists())

    def test_tarik_tunai(self):
        response = self.client.post(reverse('tarik_tunai'), {
            'no_rekening': '1111111111',
            'nominal': '50000'
        })
        self.rekening1.refresh_from_db()
        self.assertEqual(self.rekening1.saldo, 50000)
        self.assertTrue(Transaksi.objects.filter(rekening=self.rekening1, jenis='TARIK', nominal=50000).exists())

    def test_tarik_tunai_insufficient(self):
        response = self.client.post(reverse('tarik_tunai'), {
            'no_rekening': '1111111111',
            'nominal': '200000'
        })
        self.rekening1.refresh_from_db()
        self.assertEqual(self.rekening1.saldo, 100000) # Saldo tidak berubah

    def test_transfer(self):
        response = self.client.post(reverse('transfer'), {
            'rek_asal': '1111111111',
            'rek_tujuan': '2222222222',
            'nominal': '50000'
        })
        self.rekening1.refresh_from_db()
        self.rekening2.refresh_from_db()

        self.assertEqual(self.rekening1.saldo, 50000)
        self.assertEqual(self.rekening2.saldo, 100000)

        self.assertTrue(Transaksi.objects.filter(rekening=self.rekening1, jenis='TRANSFER').exists())
        self.assertTrue(Transaksi.objects.filter(rekening=self.rekening2, jenis='TRANSFER').exists())

    def test_create_nasabah(self):
        response = self.client.post(reverse('tambah_nasabah'), {
            'nama_lengkap': 'Citra',
            'nik': '1122334455',
            'alamat': 'Jl. C',
            'no_telepon': '08111222333'
        })
        self.assertTrue(Nasabah.objects.filter(nik='1122334455').exists())
        # Check if rekening is auto created
        nasabah = Nasabah.objects.get(nik='1122334455')
        self.assertTrue(Rekening.objects.filter(nasabah=nasabah).exists())
