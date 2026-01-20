from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from .models import Nasabah, Rekening, Transaksi
from .forms import NasabahForm

def dashboard(request):
    total_nasabah = Nasabah.objects.count()
    total_rekening = Rekening.objects.count()
    total_saldo = Rekening.objects.aggregate(Sum('saldo'))['saldo__sum'] or 0
    recent_transactions = Transaksi.objects.order_by('-waktu')[:5]

    context = {
        'total_nasabah': total_nasabah,
        'total_rekening': total_rekening,
        'total_saldo': total_saldo,
        'recent_transactions': recent_transactions
    }
    return render(request, 'banking/dashboard.html', context)

def setor_tunai(request):
    if request.method == 'POST':
        no_rekening = request.POST.get('no_rekening')
        nominal = request.POST.get('nominal')

        try:
            rekening = Rekening.objects.get(no_rekening=no_rekening)
            nominal_dec = int(nominal)
            if nominal_dec <= 0:
                raise ValueError("Nominal harus positif")

            with transaction.atomic():
                rekening.saldo += nominal_dec
                rekening.save()

                Transaksi.objects.create(
                    rekening=rekening,
                    jenis='SETOR',
                    nominal=nominal_dec,
                    keterangan='Setoran via Loket Web'
                )

            messages.success(request, f"Sukses! Saldo {rekening.nasabah.nama_lengkap} bertambah Rp {nominal}")
            return redirect('dashboard')

        except Rekening.DoesNotExist:
            messages.error(request, "Nomor Rekening tidak ditemukan!")
        except ValueError:
            messages.error(request, "Nominal harus angka positif!")

    return render(request, 'banking/setor.html')

def tarik_tunai(request):
    if request.method == 'POST':
        no_rekening = request.POST.get('no_rekening')
        nominal = request.POST.get('nominal')

        try:
            rekening = Rekening.objects.get(no_rekening=no_rekening)
            nominal_dec = int(nominal)
            if nominal_dec <= 0:
                raise ValueError("Nominal harus positif")

            if rekening.saldo >= nominal_dec:
                with transaction.atomic():
                    rekening.saldo -= nominal_dec
                    rekening.save()

                    Transaksi.objects.create(
                        rekening=rekening,
                        jenis='TARIK',
                        nominal=nominal_dec,
                        keterangan='Penarikan via Loket Web'
                    )
                messages.success(request, f"Sukses! Penarikan Rp {nominal} dari {rekening.nasabah.nama_lengkap} berhasil.")
                return redirect('dashboard')
            else:
                messages.error(request, "Saldo tidak mencukupi!")

        except Rekening.DoesNotExist:
            messages.error(request, "Nomor Rekening tidak ditemukan!")
        except ValueError:
            messages.error(request, "Nominal harus angka positif!")

    return render(request, 'banking/tarik.html')

def transfer(request):
    if request.method == 'POST':
        rek_asal = request.POST.get('rek_asal')
        rek_tujuan = request.POST.get('rek_tujuan')
        nominal = request.POST.get('nominal')

        try:
            if rek_asal == rek_tujuan:
                messages.error(request, "Tidak bisa transfer ke rekening sendiri!")
                return render(request, 'banking/transfer.html')

            pengirim = Rekening.objects.get(no_rekening=rek_asal)
            penerima = Rekening.objects.get(no_rekening=rek_tujuan)
            nominal_dec = int(nominal)
            if nominal_dec <= 0:
                raise ValueError("Nominal harus positif")

            if pengirim.saldo >= nominal_dec:
                with transaction.atomic():
                    pengirim.saldo -= nominal_dec
                    pengirim.save()

                    penerima.saldo += nominal_dec
                    penerima.save()

                    # Catat untuk pengirim
                    Transaksi.objects.create(
                        rekening=pengirim,
                        jenis='TRANSFER',
                        nominal=nominal_dec,
                        keterangan=f'Transfer ke {penerima.nasabah.nama_lengkap} ({rek_tujuan})'
                    )

                    # Catat untuk penerima
                    Transaksi.objects.create(
                        rekening=penerima,
                        jenis='TRANSFER',
                        nominal=nominal_dec,
                        keterangan=f'Transfer masuk dari {pengirim.nasabah.nama_lengkap} ({rek_asal})'
                    )

                messages.success(request, "Transfer Berhasil!")
                return redirect('dashboard')
            else:
                messages.error(request, "Saldo pengirim tidak mencukupi!")

        except Rekening.DoesNotExist:
            messages.error(request, "Salah satu Nomor Rekening tidak ditemukan!")
        except ValueError:
            messages.error(request, "Nominal harus angka positif!")

    return render(request, 'banking/transfer.html')

def nasabah_list(request):
    nasabah = Nasabah.objects.all().order_by('-tanggal_gabung')
    return render(request, 'banking/nasabah_list.html', {'nasabah_list': nasabah})

def tambah_nasabah(request):
    if request.method == 'POST':
        form = NasabahForm(request.POST)
        if form.is_valid():
            nasabah = form.save()
            # Auto create rekening default
            Rekening.objects.create(nasabah=nasabah, jenis='SILVER', saldo=0)
            messages.success(request, f"Nasabah {nasabah.nama_lengkap} berhasil ditambahkan! Rekening otomatis dibuat.")
            return redirect('nasabah_list')
    else:
        form = NasabahForm()
    return render(request, 'banking/nasabah_form.html', {'form': form})

def rekening_detail(request, no_rekening):
    rekening = get_object_or_404(Rekening, no_rekening=no_rekening)
    riwayat = Transaksi.objects.filter(rekening=rekening).order_by('-waktu')
    return render(request, 'banking/rekening_detail.html', {'rekening': rekening, 'riwayat': riwayat})
