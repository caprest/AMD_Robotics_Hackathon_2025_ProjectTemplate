# AMD_Robotics_Hackathon_2025_Robot-Pianist

## Team Information

**Team:** 

* Team 29:  東京ベイエリアの会
* Team Members: Fumiya Shimada/ Michiya Abe/ Tomoyuki Hatakeyama/ Yukinori Manome

**Summary:**

* We developed a model to play the piano using the SO101 arm.
* Final demo movie: [TODO]
* [Reference demo](media/target_demo.mp4) we aimed to achieve. 


<video src="media/target_demo.mp4" controls loop autoplay ></video>


## Submission Details

### 1. Mission Description
- Play songs on a toy piano using the SO101 robot arms.
   - When provided with music sheet data, the robot is expected to play the song.

### 2. Creativity

🎹 **Why settle for a human pianist when you can have a robot that never gets tired and never complains?** Our SO101 robot pianist can play your favorite tunes—no sheet music reading lessons required!

**Novel approach:**
* **Conditional vector-based execution**: Our model uses learned intention vectors instead of hardcoded coordinates, allowing it to generalize across different piano positions without recalibration.
* **Multi-camera vision system**: Three-camera setup (fingertip, top-down, side-view) with visual markers enables precise localization despite occlusions.
* **Hierarchical strategy exploration**: We explored three methodologies—fully conditioned model, explicit state transition modeling, and simplified two-sound system—to balance generalization and reliability.

**Innovation:**
* **Musical score to robot pipeline**: Translates standard musical notation directly into robotic control signals, making the system accessible without robotics expertise.

**Entertainment value:** Perfect for demonstrations, educational events, or holiday parties! 

### 3. Technical Implementations
- We implemented three approaches.

### 3.1 Conditioned Model
This model accepts a conditional vector representing the "intention of pressing each note" and executes the corresponding action. By switching the conditional vector in sync with the sheet timing, we aim to play any song.  


- *Teleoperation / Dataset Capture*
    - We captured the action of pressing each key.
    - During capture, we also recorded the timing of key presses with a custom recording script.
    - During capture, we slightly adjusted the piano settings to generalize the policy to various configurations.
    - We added ornaments and markers to improve camera-based localization learning.
    - We used three cameras to better generalize to different situations:
        - Fingertip camera is attached to the arm to see the fingertip.
        - Top-down camera is used to see the entire setting.
        - Side webcam is used to complement the occluded areas of the arm.
- *Training*
    - We post-processed the "key pressing timing data" into a "key press intention vector".
    - The "key press intention vector" is represented as a one-hot vector and embedded via a linear projection.
    - We used the ACT model.
    - We used AMD Cloud for training.
- *Inference*
    - The inference script accepts musical score data and controls the robot by switching intention vectors accordingly.
    - Detailed documentation is provided under [here](mission2/code/inference/README.md).

### 3.2 Explicit State Transition Modeling
* Due to the limited state memory in the ACT model, we later adopted explicit state modeling to execute the task. We then trained models to handle each sub-policy.

* We decomposed piano playing into two actions:
  - From any position, move to the designated key and press it.
  - Release the key and return to the neutral position.

* Following are the details of the full pipeline:

- *Teleoperation / Dataset Capture*
    - We captured the action of each sub-policy.
    - We futher varied the piano position to achieve better generalization, especially for camera.
- *Training*
    - We trained an ACT model for each sub-policy.
    - We only used the fingertip camera to reduce training difficulty.
- *Inference*
    - The inference script accepts musical score data and controls the robot by switching intention vectors accordingly.

### 3.3 Simple Two-Sound Model (Our Final Submission)

Due to generalization difficulties, we further narrowed down the sub-policies to three models:
- **C-E policy**: Plays C, then E, and returns to the C position.
- **C-G policy**: Plays C, then G, and returns to the C position.
- **C-C policy**: Plays C and returns to the C position.

By combining these three models, we can play any song using C-E-G notes!

**Operating modes:**
- **Teleoperation mode**: You can manually switch between C-E, C-G, and C-C models at any time.
- **Sheet mode**: The system automatically switches between models based on the music sheet.  



### 4. Ease of Use

**Simplified setup**: Unlike traditional robotic systems requiring precise calibration and coordinate mapping, our learning-based approach only needs demonstration data collection via teleoperation. While retraining is required for new environments, this is far more accessible than programming explicit trajectories.

**Dual operation modes**: Teleoperation mode allows manual triggering of C-E, C-G, or C-C sequences with keyboard commands, while sheet mode automatically plays songs from text-based music score files.

**Quick start**: Collect demonstration data → Train three ACT models on AMD Cloud → Run inference and enjoy your robot pianist!


## Additional Links

## Code submission


**NOTES**

1. The `latest-run` is the soft link, please make sure to copy the real target directory it linked with all sub dirs and files.
2. Only provide (upload) the wandb of your last success pre-trained model for the Mission.