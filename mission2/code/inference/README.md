# 🎹 Teaching Robots to Play Piano with Imitation Learning

A vision-based robotic piano player powered by **Action Chunking Transformer (ACT)** and the **SO101 robotic arm**. We trained a robot to play Christmas carols using imitation learning — because why should humans have all the fun?


## 🚀 What We Built

- **Sheet Music Parser** — Converts musical scores (notes + durations) into time-synchronized commands
- **Vision-Guided Control** — Camera observations enable precise key targeting
- **Learned Motor Skills** — No hand-coded trajectories — the robot learned to play entirely from watching humans

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        INFERENCE PIPELINE                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────┐      ┌──────────────┐      ┌───────────────────┐    │
│   │  Sheet   │─────▶│   Current    │      │    Observation    │    │
│   │  Music   │      │    Note      │      │  (Camera + State) │    │
│   └──────────┘      └──────┬───────┘      └─────────┬─────────┘    │
│                            │                        │               │
│                            ▼                        ▼               │
│                     ┌─────────────────────────────────┐             │
│                     │     ACT Policy (Transformer)    │             │
│                     │   ┌─────────────────────────┐   │             │
│                     │   │  Encoder  │   Decoder   │   │             │
│                     │   └─────────────────────────┘   │             │
│                     └──────────────┬──────────────────┘             │
│                                    │                                │
│                                    ▼                                │
│                           ┌─────────────────┐                       │
│                           │  Action (6-DOF) │                       │
│                           │  Joint Commands │                       │
│                           └────────┬────────┘                       │
│                                    │                                │
│                                    ▼                                │
│                          ┌──────────────────┐                       │
│                          │   SO101 Robot    │                       │
│                          │   🤖 🎹           │                       │
│                          └──────────────────┘                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎵 Supported Songs

| Song | Notes | Duration |
|------|-------|----------|
| 🎄 Jingle Bells | C4-G4 | ~10 sec |
| ⛪ When The Saints Go Marching In | C4-G4 | ~30 sec |
| 🌍 Joy To The World | C4-C5 | ~45 sec |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Robot** | SO101 Follower Arm (6-DOF) |
| **Policy** | ACT (Action Chunking Transformer) |
| **Framework** | [LeRobot](https://github.com/huggingface/lerobot) by Hugging Face 🤗 |
| **Hardware** | AMD GPU (ROCm) |
| **Vision** | OpenCV + USB Cameras |
| **Dataset** | Custom teleoperation recordings on HuggingFace Hub |

---

## 🎮 Usage

### Prepare
Please prepare conda env:
```bash
conda activate lerobot
```

### Run Modes

Since we only had **one physical robot**, we created three execution modes to enable parallel development between the data collection team and the deployment team.

| Mode | Command | Description |
|------|---------|-------------|
| **so101** | `python -m inference.main so101` | Run inference on the real robot |
| **sim** | `python -m inference.main sim` | Load observations from dataset, execute actions on real robot |
| **dummy** | `python -m inference.main dummy` | Test inference pipeline without robot connection |

#### 🤖 `so101` — Real Robot Mode
```bash
python -m inference.main so101
```
Connects to the physical SO101 robot and runs inference with real-time camera observations.

#### 🎬 `sim` — Simulation Mode  
```bash
python -m inference.main sim
```
Loads observation data from a pre-collected dataset on HuggingFace Hub, but executes actions on the real robot.  
**Use case**: While one team was collecting training data, the deployment team could validate policy behavior using previously recorded observations.

#### 🧪 `dummy` — Dummy Mode
```bash
python -m inference.main dummy
```
Runs the entire inference pipeline without any physical robot connection. Observations come from the dataset, and actions are only logged (not executed).  
**Use case**: Enabled software debugging and feature development even when the robot was occupied for data collection.

---

## 🧠 How It Works

### 1. Sheet Music System
Musical scores are represented as sequences of `(note, duration)` tuples:

```python
JingleBells = [
    ("E4", 2),  # E4 for 2 eighth notes
    ("E4", 2),
    ("E4", 4),  # E4 for 4 eighth notes (quarter note)
    ...
]
```

The `Sheet` class converts these into frame-synchronized note commands at 30 FPS.

### 2. Inference Pipeline
```python
while playing:
    note = sheet.tick_note()           # Get current note from score
    observation = robot.get_obs()       # Camera + joint states
    action = policy.inference(obs, note)  # ACT predicts action
    robot.send_action(action)           # Execute on robot
```


## 🔮 Future Work

### Real-Time Chunking (RTC)

We originally planned to integrate **Real-Time Chunking (RTC)** to improve the responsiveness and smoothness of our robot's piano playing. RTC enables more reactive control by processing action chunks in real-time, reducing latency between observation and execution.

We had prepared to clone and adapt this as `lrbt043`, but due to time constraints during the hackathon, we were unable to implement it.

**Expected benefits:**
- Lower latency between note changes and robot response
- Smoother transitions between consecutive key presses
- Better temporal alignment with the sheet music tempo

---

## 👥 Team

Developed during **AMD Hackathon 2025**
