import platform
import subprocess
import sys
import os
import shutil

def main():
    # Remove existing pyproject.toml if it exists
    if os.path.exists("pyproject.toml"):
        os.remove("pyproject.toml")
    
    print("Setting up the environment... system:", platform.system())

    # Check if Windows
    if platform.system() == "Windows":
        print("Installing with Windows CUDA dependencies...")
        
        # Copy the Windows config file
        shutil.copy("pyproject-windows.toml", "pyproject.toml")
        
        # Create the virtual environment and install
        subprocess.run(["poetry", "env", "use", "python"], check=True)

    # Check if Linux
    elif platform.system() == "Linux":
        print("Installing with Linux CUDA dependencies...")
        
        # Copy the Linux config file
        shutil.copy("pyproject-linux.toml", "pyproject.toml")
        
        # Create the virtual environment and install
        subprocess.run(["poetry", "env", "use", "python"], check=True)

    else:
        print("Installing with Mac/standard PyTorch...")
        
        # Copy the Mac config file
        shutil.copy("pyproject-mac.toml", "pyproject.toml")
        
        # Remove any existing lock file to prevent cached CUDA dependencies
        if os.path.exists("poetry.lock"):
            os.remove("poetry.lock")
        
        # Install torch directly with pip to bypass Poetry's source resolution
        subprocess.run(["pip", "install", "torch==2.2.2"], check=True)

    subprocess.run(["poetry", "lock"], check=True)
    subprocess.run(["poetry", "install"], check=True)
    
    print("Installation complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())