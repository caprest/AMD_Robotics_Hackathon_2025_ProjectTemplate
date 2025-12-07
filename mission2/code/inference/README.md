# 🎹 Teaching Robots to Play Piano with Imitation Learning

> *"Any sufficiently advanced technology is indistinguishable from magic."* — Arthur C. Clarke

A vision-based robotic piano player powered by **Action Chunking Transformer (ACT)** and the **SO101 robotic arm**. We trained a robot to play Christmas carols using imitation learning — because why should humans have all the fun?

---

## 🎬 Demo

Watch our robot play **Jingle Bells** 🎄

https://github.com/user-attachments/assets/YOUR_VIDEO_HERE

---

## 🚀 What We Built

We created an end-to-end pipeline that enables a 6-DOF robotic arm to play piano by:

1. **Learning from human demonstrations** — We teleoperated the robot to play piano keys and recorded the demonstrations
2. **Training an ACT policy** — Using the LeRobot framework, we trained a transformer-based imitation learning model
3. **Real-time inference** — The robot reads sheet music and plays notes in real-time using vision feedback

### The Magic ✨

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

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_REPO/robo-maestro.git
cd robo-maestro

# Install dependencies
pip install -r requirements.txt

# Install LeRobot
pip install lerobot
```

---

## 🎮 Usage

### Prepare
Please prepare conda env:
```bash
conda activate lerobot
```

### Run with Real Robot
```bash
python -m inference.main so101
```

### Run in Simulation Mode
```bash
python -m inference.main sim
```

### Run in Dummy Mode (for testing)
```bash
python -m inference.main dummy
```

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

### 2. ACT Policy
We use the **Action Chunking Transformer** architecture from [ACT: Adaptive Chunking Transformer](https://arxiv.org/abs/2304.13705):

- **Input**: Camera image + robot joint states + current note
- **Output**: 6-DOF action (shoulder pan, shoulder lift, elbow flex, wrist flex, wrist roll, gripper)
- **Training**: Behavior cloning on ~50 human demonstrations

### 3. Inference Pipeline
```python
while playing:
    note = sheet.tick_note()           # Get current note from score
    observation = robot.get_obs()       # Camera + joint states
    action = policy.inference(obs, note)  # ACT predicts action
    robot.send_action(action)           # Execute on robot
```

---

## 📊 Results

| Metric | Value |
|--------|-------|
| Training Episodes | 50 |
| Training Time | ~2 hours |
| Inference FPS | 30 |
| Success Rate | 85%+ key hits |

---

## 👥 Team

Built with ❤️ and ☕ at **AMD Hackathon 2025**

---

## 🙏 Acknowledgments

- [Hugging Face LeRobot](https://github.com/huggingface/lerobot) — For the amazing robotics framework
- [ACT Paper](https://arxiv.org/abs/2304.13705) — For the policy architecture
- AMD — For the GPU compute power 🔥

---

## 📄 License

MIT License — Feel free to teach more robots to make music! 🎶

---

<p align="center">
  <b>🤖 + 🎹 = 🎵</b><br>
  <i>Making robots musical, one key at a time.</i>
</p>

