import subprocess

def install_flask():
    try:
        subprocess.check_call(['pip', 'install', 'flask'])
        print("Flask installed successfully.")
        subprocess.check_call(['pip', 'install', 'passlib'])
        print("Passlib installed successfully.")
        subprocess.check_call(['pip', 'install', 'Flask-Session'])
        print("Flask-Session installed successfully.")
    except subprocess.CalledProcessError as e:
        print("Failed to install Flask:", e)
        print("Failed to install Passlib:", e)

if __name__ == '__main__':
    install_flask()