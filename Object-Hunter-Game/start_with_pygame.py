"""
Start Object Finder Game with Pygame Window System
"""
import os
import sys
import importlib
import subprocess
import time
import urllib.request
import shutil

def check_imports():
    """Check required imports"""
    required_packages = {
        "cv2": "OpenCV",
        "numpy": "NumPy",
        "pygame": "PyGame",
        "ultralytics": "Ultralytics YOLO"
    }
    
    success = True
    print("Checking environment dependencies...\n")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Operating system: {sys.platform} {os.name}\n")
    
    for package, name in required_packages.items():
        try:
            module = importlib.import_module(package)
            version = getattr(module, "__version__", "unknown")
            print(f"√ {name} installed, version: {version}")
        except ImportError:
            print(f"× {name} not installed")
            success = False
    
    try:
        import cv2
        backends = []
        if cv2.getBuildInformation().find("GStreamer:                   YES") != -1:
            backends.append("GStreamer")
        if cv2.getBuildInformation().find("DirectShow:                  YES") != -1:
            backends.append("DirectShow")
        if cv2.getBuildInformation().find("Media Foundation:            YES") != -1:
            backends.append("MSMF")
        print(f"\nOpenCV supported video backends: {', '.join(backends)}")
    except:
        pass
        
    return success

def setup_environment():
    """Setup environment variables"""
    os.environ.update({
        "OPENCV_VIDEOIO_PRIORITY_MSMF": "1",    # MSMF as first choice
        "OPENCV_VIDEOIO_PRIORITY_DSHOW": "2",   # DirectShow as second choice
        "OPENCV_VIDEOIO_PRIORITY_QT": "0",      # Disable Qt backend
        "QT_QPA_PLATFORM": "offscreen"          # Disable Qt platform
    })
    print("\nApplied OpenCV window system fixes")

def check_files():
    """Check for required files"""
    # Check for YOLO model
    primary_model = "yolo11x.pt"
    fallback_model = "yolov8n.pt"
    
    model_found = False
    model_path = os.path.join(os.getcwd(), primary_model)
    
    if os.path.exists(model_path):
        print(f"√ Primary YOLO model found: {primary_model}")
        model_found = True
    else:
        print(f"× Primary YOLO model not found: {primary_model}")
        
        # Check for fallback model
        fallback_path = os.path.join(os.getcwd(), fallback_model)
        if os.path.exists(fallback_path):
            print(f"√ Fallback YOLO model found: {fallback_model}")
            model_found = True
        else:
            print(f"× Fallback YOLO model not found: {fallback_model}")
            
            # Ask to download fallback model
            print("\nWould you like to download the fallback model? (y/n)")
            choice = input().lower().strip()
            if choice in ['y', 'yes']:
                try:
                    print(f"Downloading {fallback_model}...")
                    download_url = f"https://github.com/ultralytics/assets/releases/download/v0.0.0/{fallback_model}"
                    with urllib.request.urlopen(download_url) as response, open(fallback_model, 'wb') as out_file:
                        shutil.copyfileobj(response, out_file)
                    print(f"√ Successfully downloaded {fallback_model}")
                    model_found = True
                except Exception as e:
                    print(f"× Failed to download model: {e}")
                    print("You can manually download it from the Ultralytics GitHub repository.")
                    model_found = False
    
    # Check for sounds directory
    sounds_dir = os.path.join(os.getcwd(), "sounds")
    if not os.path.exists(sounds_dir):
        try:
            os.mkdir(sounds_dir)
            print("√ Created sounds directory")
        except:
            print("× Unable to create sounds directory")
    else:
        print("√ Sounds directory exists")
        
        # Check if any sound files exist
        sound_files = [f for f in os.listdir(sounds_dir) if f.endswith('.wav')]
        if sound_files:
            print(f"√ Found {len(sound_files)} sound files")
        else:
            print("× No sound files found in sounds directory")
    
    # Check for assets directory
    assets_dir = os.path.join(os.getcwd(), "assets")
    if not os.path.exists(assets_dir):
        try:
            os.mkdir(assets_dir)
            print("√ Created assets directory")
        except:
            print("× Unable to create assets directory")
    else:
        print("√ Assets directory exists")
    
    return model_found

def start_game():
    """Start the game"""
    try:
        print("\nLaunching Object Hunter Game...")
        setup_environment()
        
        python_exe = sys.executable
        print(f"Using Python interpreter: {python_exe}")
        
        # Run with enhanced error capture
        try:
            print("Starting game process...")
            result = subprocess.run([python_exe, "main.py"], check=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"Game process exited with error code: {e.returncode}")
            return False
        except KeyboardInterrupt:
            print("Game was interrupted by user")
            return True
            
    except Exception as e:
        print(f"Error starting game: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Print fancy banner
    print("=" * 60)
    print("    Object Hunter Game - Enhanced Pygame Window Version    ")
    print("=" * 60)
    
    import_success = check_imports()
    if not import_success:
        print("\nSome dependencies are missing. Install them with:")
        print("pip install -r requirements.txt")
        install = input("\nInstall missing dependencies now? (y/n): ").strip().lower()
        if install in ['y', 'yes']:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
                print("\nDependencies installed successfully!")
            except Exception as e:
                print(f"\nFailed to install dependencies: {e}")
                input("Press Enter to exit...")
                sys.exit(1)
        else:
            print("\nDependencies are required to run the game.")
            input("Press Enter to continue anyway...")
    
    file_check_success = check_files()
    if not file_check_success:
        print("\nSome required files are missing!")
        print("Game may not run properly.")
        cont = input("\nContinue anyway? (y/n): ").strip().lower()
        if cont not in ['y', 'yes']:
            print("Exiting...")
            sys.exit(1)
    
    print("\nAll checks complete, ready to start game!")
    print("\nTips:")
    print("- Use the mouse to click buttons on screen")
    print("- Press ESC key to exit the game")
    print("- If camera doesn't show properly, check your camera connection and restart")
    print("- The game uses advanced object detection, please be patient during startup")
    
    input("\nPress Enter to start game...")
    
    try:
        if not start_game():
            print("\nGame exited with errors")
        else:
            print("\nGame completed successfully")
    except KeyboardInterrupt:
        print("\nGame was interrupted by user")
    
    input("Press Enter to exit...") 