// 1. Test Array
let numbers = [1, 2, 3, 4];
print("Array Awal:", numbers);

// 2. Test Built-in Functions (len, first, push)
print("Panjang Array:", len(numbers));
print("Elemen Pertama:", first(numbers));

let newNumbers = push(numbers, 5);
print("Array Baru:", newNumbers);

// 3. Test Indexing
print("Ambil index ke-2:", newNumbers[2]); // Harusnya 3

// 4. Test Hash Map (Dictionary)
let user = {
    "nama": "Gabriel",
    "umur": 25,
    "lokasi": "Manado"
};

print("Nama User:", user["nama"]);
print("Lokasi:", user["lokasi"]);