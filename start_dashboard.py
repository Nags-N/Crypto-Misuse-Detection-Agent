import subprocess
import sys
import os
import time

def check_dependencies():
    # Check if frontend node_modules exists
    if not os.path.exists(os.path.join("frontend", "node_modules")):
        print("[-] npm dependencies not found. Installing...")
        subprocess.run(["npm", "install"], cwd="frontend", shell=(os.name == "nt"))

def main():
    print("==============================================")
    print("  Starting CryptoGuard AI Dashboard")
    print("==============================================\n")
    
    check_dependencies()

    # Determine correct python executable
    venv_python = os.path.join("venv", "Scripts", "python") if os.name == "nt" else os.path.join("venv", "bin", "python")
    if not os.path.exists(venv_python) and not os.path.exists(venv_python + ".exe"):
        print("[!] Virtual environment not found. Using system python.")
        venv_python = sys.executable

    # Start backend process
    print("[INFO] Starting FastAPI Backend on port 8000...")
    backend_cmd = [venv_python, "-m", "uvicorn", "api.server:app", "--reload", "--port", "8000"]
    backend_process = subprocess.Popen(backend_cmd)
    
    time.sleep(2) # Give backend a moment to initialize
    
    # Start frontend process
    print("[INFO] Starting React Frontend on port 5173...")
    frontend_cmd = ["npm", "run", "dev"]
    frontend_process = subprocess.Popen(frontend_cmd, cwd="frontend", shell=(os.name == "nt"))
    
    print("\n[SUCCESS] Dashboard is running!")
    print("-> Access the UI at: http://localhost:5173")
    print("-> Press Ctrl+C to stop both services.\n")

    try:
        # Keep process alive and wait for them
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down services...")
        backend_process.terminate()
        frontend_process.terminate()
        
        # Wait for graceful shutdown
        backend_process.wait()
        frontend_process.wait()
        print("[INFO] Shutdown complete.")

if __name__ == "__main__":
    main()
