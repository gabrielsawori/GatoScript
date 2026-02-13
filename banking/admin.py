from django.contrib import admin
from .models import Nasabah, Rekening, Transaksi

# 1. Konfigurasi Tampilan Nasabah (Untuk CS)
class RekeningInline(admin.TabularInline):
    model = Rekening
    extra = 0
    readonly_fields = ('no_rekening', 'saldo')
    can_delete = False

@admin.register(Nasabah)
class NasabahAdmin(admin.ModelAdmin):
    list_display = ('nama_lengkap', 'nik', 'no_telepon', 'tanggal_gabung')
    search_fields = ('nama_lengkap', 'nik')
    inlines = [RekeningInline]

# 2. Konfigurasi Tampilan Rekening (Read Only untuk Saldo)
@admin.register(Rekening)
class RekeningAdmin(admin.ModelAdmin):
    list_display = ('no_rekening', 'nasabah', 'jenis', 'saldo', 'aktif')
    search_fields = ('no_rekening', 'nasabah__nama_lengkap')
    list_filter = ('jenis', 'aktif')
    readonly_fields = ('no_rekening', 'saldo')

# 3. Konfigurasi Transaksi (Read Only - Audit Trail)
@admin.register(Transaksi)
class TransaksiAdmin(admin.ModelAdmin):
    list_display = ('waktu', 'rekening', 'jenis', 'nominal', 'teller')
    list_filter = ('jenis', 'waktu', 'teller')
    search_fields = ('rekening__no_rekening',)

    # Transaksi adalah log sejarah, tidak boleh diedit atau ditambah manual dari admin
    # Harus melalui sistem teller (frontend) agar logika saldo jalan.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
