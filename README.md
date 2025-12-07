# AMD_Robotics_Hackathon_2025_Robot-Pianist

## Team Information

**Team:** 

* Team 29:  東京ベイエリアの会
* Team Members: Fumiya Shimada/ Michiya Abe/ Tomoyuki Hatakeyama/ Yukinori Manome

**Summary:**

* We developed a model to play the piano using the SO101 arm
* Final demo movie. [TODO]
* Reference demo we aimed to achieve: <video src="media/target_demo.mp4" controls loop autoplay muted></video>


## Submission Details

### 1. Mission Description
- Play songs on a toy piano using the SO101 robot arms.
   - When provided with music sheet data, the robot is expected to play the song.

### 2. Creativity

🎹 **Why settle for a human pianist when you can have a robot that never gets tired, never complains, and always hits the right keys (most of the time)?** Whether it's Jingle Bells for Christmas or your favorite tune, our SO101 robot pianist is ready to perform—no sheet music reading lessons required!

**What is novel or unique in our approach:**

* **Conditional Vector-Based Music Execution**: Unlike traditional robotic piano systems that require explicit pre-programming of each note's physical coordinates, our conditioned model uses learned intention vectors. This allows the robot to generalize across different piano positions and adapt to variations in the environment without manual recalibration.

* **Hierarchical Approach with Multiple Strategies**: We explored three different methodologies—from a fully conditioned end-to-end model to explicit state transition modeling to a simplified two-sound system. This iterative refinement demonstrates our systematic problem-solving approach and allows us to understand the trade-offs between generalization and reliability.

* **Multi-Camera Vision System with Strategic Augmentation**: We implemented a three-camera setup (fingertip, top-down, and side-view) combined with visual markers and ornaments to enhance spatial understanding. This innovation addresses the challenge of precise localization in a dynamic manipulation task where occlusion and varying perspectives are critical.

**Innovation in design, methodology, or application:**

* **Dataset Capture with Variability**: During teleoperation, we intentionally introduced variations in piano positioning to build robustness into the policy from the ground up, rather than relying solely on data augmentation during training.

* **Musical Score to Robot Actions Pipeline**: We developed an end-to-end system that translates standard musical notation directly into robotic control signals, making the solution accessible to users without robotics expertise. This bridges the gap between musical expression and robotic execution.

* **Adaptive Sub-Policy Decomposition**: Recognizing the limitations of monolithic models for complex sequential tasks, we decomposed the piano-playing action into atomic sub-policies (approach-and-press, release-and-return), enabling more reliable execution and easier debugging of specific movement phases.

**Entertainment value:** Transform any space into a concert hall! Our robot pianist brings joy, sparks curiosity, and makes robotics accessible and fun for audiences of all ages. Perfect for demonstrations, educational events, or just impressing your friends at holiday parties. 

### 3. Technical Implementations
- We implemented three approaches.

### 3.1 Conditioned Model
This model accepts a conditional vector representing "intention of pushing each note" and executes the corresponding action. By switching the conditional vector in sync with the sheet timing, we aim to play any song.  


- *Teleoperation / Dataset Capture*
    - We captured the action of pressing each key.
    - During capture, we also recorded the timing of key presses.
    - During capture, we slightly adjusted the piano settings to generalize the policy to various configurations.
    - We added ornaments and markers to improve camera-based localization learning.
    - We used three cameras to better generalize to different situations.
        - Finger tip camera is attached to the arm to see the fingertip.
        - Top-down camera is used to see the entire setting
        - Side web camera is used to complement the occluded area of arm
- *Training*
    - We post-processed the "key pressing timing data" into a "key press intention vector".
    - The "key press intention vector" is represented as a one-hot vector and embedded via a linear projection.
    - We used the ACT model.
    - We used AMD Cloud for training.
- *Inference*
    - The inference script accepts musical score data and controls the robot by switching intention vectors accordingly.
    - Detailed documentation is provided under [mission2/code/inference]().

### 3.2 Explicit State Transition Modeling
* Because of the limited state memory in the ACT model, we later take explicit state modeling to execute the task. We then train models to handle each sub-policy.

* We decomposed piano playing into two actions:
  - From any position, move to the designated key and press it.
  - Release the key and return to the neutral position.

* Following are the details of the full pipeline:

- *Teleoperation / Dataset Capture*
    - We captured the action of each sub-policy.
- *Training*
    - We trained an ACT model for each sub-policy.
    - We limited the use of camera to ease the difficulty in training.
    -
- *Inference*
    - The inference script accepts musical score data and controls the robot by switching intention vectors accordingly.
    - Detailed documentation is provided under [mission2/code/inference]().

### 3.3 Simple Two-Sound Model
- Due to generalization difficulties, we narrowed down the sub-policy to playing C-E and C-G.

- We have two modes:
  - Teleoperation mode: you can switch between the C-E model and C-G model at any time.
  - Sheet mode: you can switch between the C-E and C-G models based on the music sheet.  



### 4. Ease of use
- *How generalizable is your implementation across tasks or environments?*
- *Flexibility and adaptability of the solution*
- *Types of commands or interfaces needed to control the robot*

## Additional Links

## Code submission


**NOTES**

1. The `latest-run` is the soft link, please make sure to copy the real target directory it linked with all sub dirs and files.
2. Only provide (upload) the wandb of your last success pre-trained model for the Mission.