from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from .models import Nasabah, Rekening, Transaksi, Tagihan
from .forms import NasabahForm, TagihanForm, BayarTagihanForm
from decimal import Decimal, InvalidOperation
from django.utils import timezone

# Safety threshold
SAFE_DECIMAL_LIMIT = Decimal('1e14')

def dashboard(request):
    total_nasabah = Nasabah.objects.count()
    total_rekening = Rekening.objects.count()
    total_saldo = Rekening.objects.filter(saldo__lt=SAFE_DECIMAL_LIMIT).aggregate(Sum('saldo'))['saldo__sum'] or 0
    recent_transactions = Transaksi.objects.filter(nominal__lt=SAFE_DECIMAL_LIMIT).order_by('-waktu')[:5]

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
            nominal_dec = Decimal(nominal)
            if nominal_dec <= 0: raise ValueError("Nominal harus positif")
            with transaction.atomic():
                rekening = Rekening.objects.select_for_update().get(no_rekening=no_rekening)
                rekening.saldo += nominal_dec
                rekening.save()
                Transaksi.objects.create(rekening=rekening, jenis='SETOR', nominal=nominal_dec, keterangan='Setoran via Loket Web')
            messages.success(request, f"Sukses! Saldo {rekening.nasabah.nama_lengkap} bertambah Rp {nominal_dec:,.2f}")
            return redirect('dashboard')
        except Rekening.DoesNotExist: messages.error(request, "Nomor Rekening tidak ditemukan!")
        except (ValueError, InvalidOperation): messages.error(request, "Nominal harus angka positif!")
    return render(request, 'banking/setor.html')

def tarik_tunai(request):
    if request.method == 'POST':
        no_rekening = request.POST.get('no_rekening')
        nominal = request.POST.get('nominal')
        try:
            nominal_dec = Decimal(nominal)
            if nominal_dec <= 0: raise ValueError("Nominal harus positif")
            with transaction.atomic():
                rekening = Rekening.objects.select_for_update().get(no_rekening=no_rekening)
                if rekening.saldo >= nominal_dec:
                    rekening.saldo -= nominal_dec
                    rekening.save()
                    Transaksi.objects.create(rekening=rekening, jenis='TARIK', nominal=nominal_dec, keterangan='Penarikan via Loket Web')
                    messages.success(request, f"Sukses! Penarikan Rp {nominal_dec:,.2f} dari {rekening.nasabah.nama_lengkap} berhasil.")
                    return redirect('dashboard')
                else: messages.error(request, "Saldo tidak mencukupi!")
        except Rekening.DoesNotExist: messages.error(request, "Nomor Rekening tidak ditemukan!")
        except (ValueError, InvalidOperation): messages.error(request, "Nominal harus angka positif!")
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
            nominal_dec = Decimal(nominal)
            if nominal_dec <= 0: raise ValueError("Nominal harus positif")
            with transaction.atomic():
                pengirim = Rekening.objects.select_for_update().get(no_rekening=rek_asal)
                penerima = Rekening.objects.select_for_update().get(no_rekening=rek_tujuan)
                if pengirim.saldo >= nominal_dec:
                    pengirim.saldo -= nominal_dec
                    pengirim.save()
                    penerima.saldo += nominal_dec
                    penerima.save()
                    Transaksi.objects.create(rekening=pengirim, jenis='TRANSFER', nominal=nominal_dec, keterangan=f'Transfer ke {penerima.nasabah.nama_lengkap} ({rek_tujuan})')
                    Transaksi.objects.create(rekening=penerima, jenis='TRANSFER', nominal=nominal_dec, keterangan=f'Transfer masuk dari {pengirim.nasabah.nama_lengkap} ({rek_asal})')
                    messages.success(request, "Transfer Berhasil!")
                    return redirect('dashboard')
                else: messages.error(request, "Saldo pengirim tidak mencukupi!")
        except Rekening.DoesNotExist: messages.error(request, "Salah satu Nomor Rekening tidak ditemukan!")
        except (ValueError, InvalidOperation): messages.error(request, "Nominal harus angka positif!")
    return render(request, 'banking/transfer.html')

def nasabah_list(request):
    nasabah = Nasabah.objects.all().order_by('-tanggal_gabung')
    return render(request, 'banking/nasabah_list.html', {'nasabah_list': nasabah})

def tambah_nasabah(request):
    if request.method == 'POST':
        form = NasabahForm(request.POST)
        if form.is_valid():
            nasabah = form.save()
            tipe_akun = form.cleaned_data.get('tipe_akun', 'PRIBADI') # Handle if not present, though form should have it
            # Auto create rekening based on selection
            Rekening.objects.create(nasabah=nasabah, jenis='SILVER', tipe=tipe_akun, saldo=0)
            messages.success(request, f"Nasabah {nasabah.nama_lengkap} ({tipe_akun}) berhasil ditambahkan!")
            return redirect('nasabah_list')
    else:
        form = NasabahForm()
    return render(request, 'banking/nasabah_form.html', {'form': form})

def rekening_detail(request, no_rekening):
    rekening = get_object_or_404(Rekening, no_rekening=no_rekening)
    riwayat = Transaksi.objects.filter(rekening=rekening, nominal__lt=SAFE_DECIMAL_LIMIT).order_by('-waktu')
    return render(request, 'banking/rekening_detail.html', {'rekening': rekening, 'riwayat': riwayat})

# --- FITUR BARU: TAGIHAN ---

def buat_tagihan(request):
    if request.method == 'POST':
        form = TagihanForm(request.POST)
        if form.is_valid():
            no_rek_bisnis = form.cleaned_data['no_rekening_bisnis']
            try:
                rek_bisnis = Rekening.objects.get(no_rekening=no_rek_bisnis)
                if rek_bisnis.tipe != 'BISNIS':
                    messages.error(request, "Hanya Rekening BISNIS yang bisa membuat tagihan!")
                    return render(request, 'banking/buat_tagihan.html', {'form': form})

                tagihan = form.save(commit=False)
                tagihan.pembuat = rek_bisnis
                tagihan.save()
                messages.success(request, f"Tagihan Berhasil Dibuat! Nomor Tagihan: {tagihan.nomor_tagihan}")
                return redirect('buat_tagihan')
            except Rekening.DoesNotExist:
                messages.error(request, "Nomor Rekening Bisnis tidak ditemukan!")
    else:
        form = TagihanForm()
    return render(request, 'banking/buat_tagihan.html', {'form': form})

def bayar_tagihan(request):
    if request.method == 'POST':
        form = BayarTagihanForm(request.POST)
        if form.is_valid():
            nomor_tagihan = form.cleaned_data['nomor_tagihan']
            no_rek_pembayar = form.cleaned_data['no_rekening_pembayar']

            try:
                tagihan = Tagihan.objects.get(nomor_tagihan=nomor_tagihan)
                if tagihan.status == 'LUNAS':
                    messages.warning(request, "Tagihan ini sudah lunas!")
                    return redirect('bayar_tagihan')

                with transaction.atomic():
                    pembayar = Rekening.objects.select_for_update().get(no_rekening=no_rek_pembayar)
                    pembuat = Rekening.objects.select_for_update().get(pk=tagihan.pembuat.pk) # Lock pembuat juga

                    if pembayar.saldo >= tagihan.jumlah:
                        # Transfer Logic
                        pembayar.saldo -= tagihan.jumlah
                        pembayar.save()

                        pembuat.saldo += tagihan.jumlah
                        pembuat.save()

                        # Update Tagihan
                        tagihan.status = 'LUNAS'
                        tagihan.pembayar = pembayar
                        tagihan.waktu_dibayar = timezone.now()
                        tagihan.save()

                        # Catat Transaksi
                        Transaksi.objects.create(
                            rekening=pembayar,
                            jenis='BAYAR',
                            nominal=tagihan.jumlah,
                            keterangan=f'Bayar Tagihan {tagihan.nomor_tagihan} ({tagihan.jenis_layanan})'
                        )
                        # Catat transaksi masuk buat bisnis
                        Transaksi.objects.create(
                            rekening=pembuat,
                            jenis='TRANSFER', # Using TRANSFER for income from bill
                            nominal=tagihan.jumlah,
                            keterangan=f'Terima Pembayaran {tagihan.nomor_tagihan}'
                        )

                        messages.success(request, f"Tagihan {tagihan.nomor_tagihan} LUNAS! Terimakasih.")
                        return redirect('dashboard')
                    else:
                        messages.error(request, "Saldo tidak mencukupi untuk membayar tagihan ini.")

            except Tagihan.DoesNotExist:
                messages.error(request, "Nomor Tagihan tidak ditemukan!")
            except Rekening.DoesNotExist:
                messages.error(request, "Nomor Rekening Pembayar tidak ditemukan!")
            except Exception as e:
                messages.error(request, f"Terjadi kesalahan: {str(e)}")

    else:
        form = BayarTagihanForm()
    return render(request, 'banking/bayar_tagihan.html', {'form': form})
