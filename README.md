# Scuba-Cat-CV[cite: 1]

Made a CV code that runs the scuba cat meme when you hit the emote on your camera[cite: 1].

This project uses your webcam to track your body movements in real-time. Simply raise your hand above your shoulder to trigger the scuba cat meme. Lower your hand, and the meme instantly aborts, returning you to the normal webcam feed. 

## Features
* **Real-time Pose Detection:** Uses MediaPipe to track skeletal landmarks.
* **Instant Meme Deployment:** Triggers video and audio synchronization using OpenCV and Pygame.
* **Background Monitoring:** Runs pose detection in a separate thread to ensure the meme stops exactly when you lower your hand.
* **Cooldown Timer:** Prevents the meme from rapidly re-triggering and causing chaos.

## Repository Structure
Make sure your directory matches this exact structure[cite: 1]:
* `README.md`[cite: 1]
* `cat_audio.mp3`[cite: 1]
* `cat_video.mp4`[cite: 1]
* `scuba.py`[cite: 1]

*(Note: You will need to provide your own `cat_video.mp4` and `cat_audio.mp3` files in the root directory for the script to function properly.)*

## Requirements
Install the required dependencies before running the script:
```bash
pip install opencv-python mediapipe pygame
