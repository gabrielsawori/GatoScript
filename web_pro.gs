print("Menyalakan Server Pro...");

let handler = fn(req) {
    print("Request:", req["path"]);

    if (req["path"] == "/") {
        // BACA FILE HTML DARI DISK!
        let html = readFile("index.html");

        if (html == null) {
            return "<h1>Error: Gagal baca file index.html</h1>";
        }
        return html;
    } else {
        // Simple Log System (Menulis log ke file)
        writeFile("server.log", "404 hit at " + req["path"]);
        return "<h1>404 Not Found</h1>";
    }
};

listen("4000", handler);