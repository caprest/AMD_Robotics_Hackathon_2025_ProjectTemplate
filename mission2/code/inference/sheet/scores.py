from ..policy.const import TransitionType

NOTE_TO_NUMBER = {
    None: -1,
    "z": 0,
    "A3": 1,
    "B3": 2,
    "C4": 3,
    "D4": 4,
    "E4": 5,
    "F4": 6,
    "G4": 7,
    "A4": 8,
    "B4": 9,
    "C5": 10,
    TransitionType.C_TO_C: 11,
    TransitionType.C_TO_E: 12,
    TransitionType.C_TO_G: 13,
}

TestSequence = [  # Note: 8th note (duration=1)
    ("C4", 2),
    ("E4", 2),
    ("G4", 2),
    ("E4", 2),
    ("C4", 2),
]

TrasitionSequence = [
    (TransitionType.C_TO_G, 4),
    (TransitionType.C_TO_E, 2),
    (TransitionType.C_TO_G, 2),
    (TransitionType.C_TO_C, 2),
    (TransitionType.C_TO_E, 2),
    (TransitionType.C_TO_G, 4),
    (TransitionType.C_TO_E, 4),
    (TransitionType.C_TO_G, 2),
    (TransitionType.C_TO_C, 6),
]

JingleBells = [  # Note: 8th note (duration=1)
    ("E4", 2),
    ("E4", 2),
    ("E4", 4),
    ("E4", 2),
    ("E4", 2),
    ("E4", 4),
    ("E4", 2),
    ("G4", 2),
    ("C4", 3),
    ("D4", 1),
    ("E4", 6),
    ("z", 2),
]

WhenTheSaintsGoMarchingIn = [  # Note: quarter note (duration=1)
    ("z", 1),
    ("C4", 1),
    ("E4", 1),
    ("F4", 1),
    ("G4", 5),
    ("C4", 1),
    ("E4", 1),
    ("F4", 1),
    ("G4", 5),
    ("C4", 1),
    ("E4", 1),
    ("F4", 1),
    ("G4", 2),
    ("E4", 2),
    ("C4", 2),
    ("E4", 2),
    ("D4", 5),
    ("E4", 1),
    ("E4", 1),
    ("D4", 1),
    ("C4", 3),
    ("C4", 1),
    ("E4", 2),
    ("G4", 2),
    ("G4", 1),
    ("F4", 4),
    ("F4", 1),
    ("E4", 1),
    ("F4", 1),
    ("G4", 2),
    ("E4", 2),
    ("C4", 2),
    ("D4", 2),
    ("C4", 6),
    ("z", 2),
]

JoyToTheWorld = [  # Note: based 16th note (duration=1)
    ("C5", 4),
    ("B4", 3),
    ("A4", 1),
    ("G4", 6),
    ("F4", 2),
    ("E4", 4),
    ("D4", 4),
    ("C4", 6),
    ("G4", 2),
    ("A4", 6),
    ("A4", 2),
    ("B4", 5),
    ("B4", 2),
    ("C5", 12),
    ("z", 2),
    ("C5", 2),
    ("C5", 2),
    ("B4", 2),
    ("A4", 2),
    ("G4", 2),
    ("G4", 3),
    ("F4", 1),
    ("E4", 2),
    ("C5", 2),
    ("C5", 2),
    ("B4", 2),
    ("A4", 2),
    ("G4", 2),
    ("G4", 3),
    ("F4", 1),
    ("E4", 2),
    ("E4", 2),
    ("E4", 2),
    ("E4", 2),
    ("E4", 2),
    ("F4", 1),
    ("G4", 6),
    ("F4", 1),
    ("E4", 1),
    ("D4", 2),
    ("D4", 2),
    ("D4", 2),
    ("D4", 1),
    ("E4", 1),
    ("F4", 6),
    ("E4", 1),
    ("D4", 1),
    ("C4", 2),
    ("C5", 4),
    ("A4", 2),
    ("G4", 3),
    ("F4", 1),
    ("E4", 2),
    ("F4", 2),
    ("E4", 4),
    ("D4", 4),
    ("C4", 8),
]


def convert_to_int(scores):
    """Convert human-readable tuple format to scores_gt.py numeric format"""
    gt_scores = []
    for score in scores:
        gt_scores.extend([NOTE_TO_NUMBER[score[0]]] * score[1])
    return gt_scores


# Generate scores_gt.py format
WhenTheSaintsGoMarchingIn_gt = convert_to_int(WhenTheSaintsGoMarchingIn)
JoyToTheWorld_gt = convert_to_int(JoyToTheWorld)

# Display for verification
if __name__ == "__main__":
    print("WhenTheSaintsGoMarchingIn (human-readable):")
    print(WhenTheSaintsGoMarchingIn)
    print()

    print("WhenTheSaintsGoMarchingIn (scores_gt.py format):")
    print(WhenTheSaintsGoMarchingIn_gt)
    print()

    print("JoyToTheWorld (human-readable):")
    print(JoyToTheWorld)
    print()

    print("JoyToTheWorld (scores_gt.py format):")
    print(JoyToTheWorld_gt)
