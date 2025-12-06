from __future__ import annotations

from pathlib import Path
from typing import Any, MutableMapping

from lerobot.datasets.lerobot_dataset import LeRobotDataset


class Dataset:
    """Thin wrapper around LeRobotDataset to hide HF/local handling details."""

    def __init__(
        self,
        repo_id: str,
        local_dir: str | Path | None = None,
        **dataset_kwargs: Any,
    ):
        """
        Args:
            repo_id: Hugging Face repo id containing a LeRobot dataset.
            local_dir: Optional local cache/override directory.
            streaming: Whether to stream data instead of downloading it eagerly.
            dataset_kwargs: Extra keyword arguments forwarded to LeRobotDataset.
        """

        resolved_local_dir = (
            Path(local_dir).expanduser().resolve() if local_dir else None
        )

        lerobot_kwargs: MutableMapping[str, Any] = {
            "repo_id": repo_id,
        }
        if resolved_local_dir:
            lerobot_kwargs["local_dir"] = str(resolved_local_dir)
        lerobot_kwargs.update(dataset_kwargs)

        self.dataset = LeRobotDataset(**lerobot_kwargs)

        # show the dataset info
        print("===========================")
        print("📝 Dataset Info")
        print("===========================")
        print("fps: ", self.dataset.fps)
        print("num_episodes: ", self.dataset.num_episodes)
        print("num_frames: ", self.dataset.num_frames)
        print("features: ", self.dataset.features)

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, idx: int) -> Any:
        return self.dataset[idx]

    def __iter__(self):
        return iter(self.dataset)


if __name__ == "__main__":
    dataset = Dataset("abemii/test-20251206_172803")
    print(dataset[0])
