import torch

from lerobot.policies.act.modeling_act import ACTPolicy
from lerobot.processor import PolicyProcessorPipeline

from .const import TransitionType


class ActPolicy:
    def __init__(self, note_to_repo_id: dict[str | TransitionType | None, str]):
        self.note_to_policy: dict[str | TransitionType | None, ACTPolicy] = {}
        self.note_to_preprocessor = {}
        self.note_to_postprocessor = {}
        for note, repo_id in note_to_repo_id.items():
            self.note_to_policy[note] = ACTPolicy.from_pretrained(repo_id).cuda()
            self.note_to_preprocessor[note] = PolicyProcessorPipeline.from_pretrained(
                repo_id, config_filename="policy_preprocessor.json"
            )
            self.note_to_postprocessor[note] = PolicyProcessorPipeline.from_pretrained(
                repo_id, config_filename="policy_postprocessor.json"
            )
        self.prev_note = None

    def inference(
        self, observation: dict, note: str | TransitionType | None
    ) -> torch.Tensor | None:
        # assert note is not None
        if note not in self.note_to_policy:
            print(f"⚠️ No policy for note: {note}")
            return None

        if self.prev_note != note:
            self.note_to_policy[note].reset()

        self.prev_note = note

        preprocessor = self.note_to_preprocessor[note]
        postprocessor = self.note_to_postprocessor[note]
        policy = self.note_to_policy[note]

        batched_observation = preprocessor(observation)
        action = policy.select_action(batched_observation)
        post_processed = postprocessor({"action": action})
        return post_processed["action"].squeeze(0).to(dtype=torch.float32)

    def reset(self):
        for policy in self.note_to_policy.values():
            policy.reset()
