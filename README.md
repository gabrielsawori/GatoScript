# GatoScript
A modern interpretive programming language based on Go.
# 🐱 GatoScript

**GatoScript** is a lightweight, interpreted programming language built in Go. It features a simple syntax, first-class functions, and a built-in HTTP server for backend development.

Created by **Gabriel Eduardi William Newton**.

## 🚀 Features

-   **Simple Syntax:** Easy to learn, inspired by Go and Python.
-   **Web Server Ready:** Built-in `listen()` function to handle HTTP requests.
-   **Concurrency:** Supports `spawn()` to run async tasks (using Goroutines).
-   **Data Structures:** Arrays, Hash Maps (JSON-like), and Strings.
-   **File System:** Read and write files easily.

## 📦 Installation

1.  Download the latest binary from [Releases](link-repo-nanti).
2.  Add to your path or run directly:
    ```bash
    ./gato script.gs
    ```

## 💻 Example Usage

### 1. Hello World
```gatoscript
print("Hello, GatoScript!");
