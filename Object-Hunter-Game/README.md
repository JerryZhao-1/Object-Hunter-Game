# Object Hunter Game

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![Status](https://img.shields.io/badge/status-active-green)

A camera-based object detection game where players must find specified objects using their camera. Powered by YOLO object detection technology.

Developed by Jerry Zhao

![Game Demo](assets/screenshots/demo.png)

## 🎮 Features

- Powered by YOLO v11x / v8 object detection technology
- Real-time object recognition
- Multiple difficulty levels (Easy, Normal, Hard)
- Engaging gameplay with performance feedback
- Supports 14+ common household objects for detection
- Clean, intuitive user interface

## 🔧 System Requirements

- Python 3.6+
- Webcam
- Windows, MacOS, or Linux

## 📥 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/object-hunter-game.git
   cd object-hunter-game
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running the Game

### Method 1: Using the Standard Launcher (Recommended)

```bash
python start_with_pygame.py
```

This will check dependencies and start the game when everything is ready.

### Method 2: Direct Launch

```bash
python main.py
```

Directly launches the game without checking dependencies.

## 🎯 Game Rules

1. After starting the game, the bottom of the screen will display the name of an object to find
2. Point your camera at this object for the system to recognize it
3. Successfully identified objects earn you points and a new target is selected
4. Try to find as many objects as possible before time runs out!

## 🎲 Gameplay

- **Three Difficulty Levels**:
  - **Easy**: Lower recognition requirements, simpler objects
  - **Normal**: Balanced challenge with standard recognition requirements
  - **Hard**: Higher recognition requirements, more challenging objects

- **Controls**:
  - Use mouse to navigate menus
  - Press ESC to exit the game

## 📋 Supported Objects

The game can recognize the following 14 objects:

- Cup
- Bottle
- Book
- Cell phone
- Keyboard
- Mouse
- Chair
- Laptop
- Remote
- Backpack
- Person
- TV
- Scissors
- Clock

## 🧠 YOLO Models

The game supports two YOLO models:

- **yolo11x.pt** (Primary, larger, more accurate) 
- **yolov8n.pt** (Fallback, smaller, faster)

## 🔍 Troubleshooting

1. **Cannot open camera**
   
   Make sure your camera is properly connected and not in use by another application.

2. **Window creation fails**
   
   Try running the game with the Pygame window system using `python start_with_pygame.py`.

3. **Game fails to start**
   
   - Check if all necessary dependencies are installed
   - Verify that either yolo11x.pt or yolov8n.pt model file exists
   - Check console output for error messages

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 