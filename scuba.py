import cv2
import mediapipe as mp
import pygame
import time
import threading

# 1. Initialize the DJ (Pygame Audio)
pygame.mixer.init()

# 2. Initialize the Brain (MediaPipe Pose)
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils
pose = mp_pose.Pose()

# --- YOUR MEDIA FILES ---
VIDEO_PATH = "cat_video.mp4" 
AUDIO_PATH = "cat_audio.mp3" 

# Global flag to stop the meme instantly
stop_meme = False

# --- WINDOW SETTINGS FOR BETTER QUALITY ---
WINDOW_NAME = "Scuba Dance Tracker"
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720

def is_hand_raised(landmarks):
    """
    SUPER SIMPLE: Check if either wrist is above its shoulder.
    Returns True if left OR right hand is raised.
    """
    # Get the landmarks
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    
    # Remember: smaller Y = higher up!
    # So wrist.y < shoulder.y means hand is ABOVE shoulder
    
    left_hand_raised = left_wrist.y < left_shoulder.y
    right_hand_raised = right_wrist.y < right_shoulder.y
    
    # Return True if EITHER hand is raised
    return left_hand_raised or right_hand_raised


def check_pose_in_background(cap, pose):
    """Constantly checks if hand is still raised, running in parallel."""
    global stop_meme
    
    while not stop_meme:
        success, img = cap.read()
        if not success:
            break
            
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # If hand is NO LONGER raised, kill the meme!
            if not is_hand_raised(landmarks):
                stop_meme = True
                break
        
        time.sleep(0.05)  # Check every 50ms


def play_scuba_meme(webcam_cap, pose_detector):
    """This function hijacks the screen to play the meme, then returns to the webcam."""
    global stop_meme
    stop_meme = False
    
    print("🤿 HAND RAISED! Deploying Cat...")
    
    try:
        pygame.mixer.music.load(AUDIO_PATH)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Audio error (Did you add the mp3 file?): {e}")

    # Load the video
    meme_cap = cv2.VideoCapture(VIDEO_PATH)
    if not meme_cap.isOpened():
        print(f"Video error (Did you add the {VIDEO_PATH} file?)")
        return

    # Start background thread to monitor pose
    pose_thread = threading.Thread(target=check_pose_in_background, args=(webcam_cap, pose_detector))
    pose_thread.daemon = True
    pose_thread.start()

    # Figure out the video's framerate
    fps = meme_cap.get(cv2.CAP_PROP_FPS)
    delay = int(1000 / fps) if fps > 0 else 30

    while meme_cap.isOpened() and not stop_meme:
        ret, frame = meme_cap.read()
        if not ret:
            break

        # Resize video to match window size
        frame = cv2.resize(frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        cv2.imshow(WINDOW_NAME, frame)
        
        if cv2.waitKey(delay) & 0xFF == ord('q') or stop_meme:
            break
            
    # Clean up
    meme_cap.release()
    pygame.mixer.music.stop()
    stop_meme = True
    
    print("🛑 Meme stopped! Back to normal...")


# 3. Initialize the Eyes (Webcam) with BETTER SETTINGS
cap = cv2.VideoCapture(0)

# Set webcam to higher resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Create a named window with better properties
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, DISPLAY_WIDTH, DISPLAY_HEIGHT)

# Cooldown to prevent rapid re-triggering
last_trigger_time = 0
COOLDOWN = 2  # Reduced to 2 seconds

while True:
    success, img = cap.read()
    if not success:
        break

    # Resize the webcam feed to match display size
    img = cv2.resize(img, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

    # Convert color for MediaPipe
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)

    # If the AI sees your skeleton...
    if results.pose_landmarks:
        # Draw landmarks with thinner lines for cleaner look
        mp_draw.draw_landmarks(
            img, 
            results.pose_landmarks, 
            mp_pose.POSE_CONNECTIONS,
            mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2)
        )
        
        landmarks = results.pose_landmarks.landmark
        
        # --- SUPER SIMPLE LOGIC: HAND ABOVE SHOULDER ---
        current_time = time.time()
        if (is_hand_raised(landmarks) and 
            current_time - last_trigger_time > COOLDOWN):
            
            # Flash a green warning
            cv2.putText(img, "HAND RAISED! 🙌", (50, 80), 
                       cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 0), 3)
            cv2.imshow(WINDOW_NAME, img)
            cv2.waitKey(1) 
            
            # Trigger the meme!
            play_scuba_meme(cap, pose)
            
            last_trigger_time = time.time()

    # Show the normal webcam feed
    cv2.imshow(WINDOW_NAME, img)

    # Press 'q' to quit the whole program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()