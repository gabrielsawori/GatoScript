print("MULAI PROGRAM");

// Fungsi yang kerjanya lama (pura-pura download file)
let download = fn(id) {
    print("⬇️  Mulai download file:", id);
    sleep(2000); // Tidur 2 detik
    print("✅ Selesai download file:", id);
};

// Jalankan 2 download secara bersamaan (Async)
spawn(download, "File_A.mp4");
spawn(download, "File_B.zip");

print("⚠️  Kode ini jalan duluan karena tidak menunggu download selesai!");

// Tahan sebentar agar program tidak langsung mati sebelum download beres
sleep(3000);
print("SELESAI SEMUA");