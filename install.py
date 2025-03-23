import platform
import subprocess
import sys
import os
import shutil

def main():
    # Check if Windows
    if platform.system() == "Windows":
        print("Installing with Windows CUDA dependencies...")
        config_file = "pyproject-windows.toml"
        
        # For Windows, we need to temporarily rename config files to use the Windows version
        if os.path.exists("pyproject.toml.backup"):
            os.remove("pyproject.toml.backup")
            
        # Backup the original pyproject.toml
        shutil.copy("pyproject.toml", "pyproject.toml.backup")
        
        # Replace with Windows version
        shutil.copy(config_file, "pyproject.toml")
        
        try:
            # Create the virtual environment and install
            subprocess.run(["poetry", "env", "use", "python"], check=True)
            subprocess.run(["poetry", "install"], check=True)
            
            # Restore original config
            shutil.move("pyproject.toml.backup", "pyproject.toml")
        except Exception as e:
            # Make sure we restore the original config even if there's an error
            if os.path.exists("pyproject.toml.backup"):
                shutil.move("pyproject.toml.backup", "pyproject.toml")
            raise e
    else:
        print("Installing with standard PyTorch...")
        
        # For Mac/others, make sure we use only the standard config
        # Remove any existing lock file to prevent cached CUDA dependencies
        if os.path.exists("poetry.lock"):
            os.remove("poetry.lock")
        
        # Install using pip directly for Mac to bypass Poetry's source resolution
        # Use the latest available version that's compatible
        subprocess.run(["pip", "install", "torch==2.2.2"], check=True)
        subprocess.run(["poetry", "install", "--no-root"], check=True)
    
    print("Installation complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
