import subprocess

def install_flask():
    try:
        subprocess.check_call(['pip', 'install', 'flask'])
        print("Flask installed successfully.")
    except subprocess.CalledProcessError as e:
        print("Failed to install Flask:", e)

if __name__ == '__main__':
    install_flask()