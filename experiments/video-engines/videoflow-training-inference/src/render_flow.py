from __future__ import annotations

import os
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
ROOT = SRC_DIR.parent
sys.path.insert(0, str(SRC_DIR))

from render_nodes import (  # noqa: E402
    FrameManifestConsumer,
    FrameProducer,
    FrameRendererProcessor,
    TimingProcessor,
)

from videoflow.core import Flow  # noqa: E402
from videoflow.core.constants import BATCH  # noqa: E402


def build_flow() -> Flow:
    timing_path = Path(
        os.environ.get("VF_TIMING_PATH", str(ROOT / "assets" / "audio" / "timing.json"))
    ).resolve()
    output_dir = Path(
        os.environ.get("VF_OUTPUT_DIR", str(ROOT / ".render" / "frames"))
    ).resolve()
    manifest_path = Path(
        os.environ.get("VF_MANIFEST_PATH", str(ROOT / ".render" / "frame-events.jsonl"))
    ).resolve()
    total_frames = int(os.environ.get("VF_TOTAL_FRAMES", "660"))

    frame_index = FrameProducer(total_frames, name="frame-index")
    timed = TimingProcessor(str(timing_path), name="scene-timing")(frame_index)
    rendered = FrameRendererProcessor(
        str(output_dir),
        str(ROOT / "src" / "project.json"),
        str(ROOT / "assets"),
        name="frame-renderer",
    )(timed)
    manifest = FrameManifestConsumer(str(manifest_path), name="frame-manifest")(rendered)
    return Flow([manifest], flow_type=BATCH, flow_id="training-vs-inference")


if __name__ == "__main__":
    from videoflow.engines.local import LocalProcessEngine

    flow = build_flow()
    flow.run(LocalProcessEngine())
    flow.join()
