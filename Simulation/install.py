import subprocess

# Use subprocess to run the pip install command


def install_packages(packages):
    for i in packages:
        try:
            subprocess.check_call(["pip", "install", i])
            print(f"Successfully installed {i}")
        except subprocess.CalledProcessError:
            print(f"Failed to install {i}")

# Function to install matplotlib


def install_matplot_lib():
    try:
        subprocess.check_call(["pip", "install", "-U", "pip"])
        subprocess.check_call(["pip", "install", "-U", "matplotlib"])
        print(f"Successfully installed matplotlib")
    except subprocess.CalledProcessError:
        print(f"Failed to install matplotlib")
# main funtcion to test gui.py


def main():
    packages = ["openpyxl", "pandas", "numpy"]
    install_packages(packages)
    install_matplot_lib()


# Check if the script is being run as the main program
if __name__ == "__main__":
    main()
