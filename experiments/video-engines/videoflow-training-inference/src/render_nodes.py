from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from render_visuals import render_frame

from videoflow.core.node import ConsumerNode, ProcessorNode, ProducerNode


class FrameProducer(ProducerNode):
    def __init__(self, total_frames: int, **kwargs: Any) -> None:
        self._total_frames = int(total_frames)
        self._current = 0
        super().__init__(**kwargs)

    def next(self) -> int:
        if self._current >= self._total_frames:
            raise StopIteration()
        value = self._current
        self._current += 1
        return value


class TimingProcessor(ProcessorNode):
    def __init__(self, timing_path: str, **kwargs: Any) -> None:
        self._timing_path = str(timing_path)
        self._timing: dict[str, Any] | None = None
        super().__init__(**kwargs)

    def open(self) -> None:
        self._timing = json.loads(Path(self._timing_path).read_text(encoding="utf-8"))

    def process(self, frame_index: int) -> dict[str, Any]:
        timing = self._timing
        if timing is None:
            raise RuntimeError("TimingProcessor opened without timing data")
        fps = float(timing["fps"])
        timestamp = frame_index / fps
        scene = timing["scenes"][-1]
        for candidate in timing["scenes"]:
            if timestamp < float(candidate["end"]):
                scene = candidate
                break
        scene_start = float(scene["start"])
        scene_end = float(scene["end"])
        scene_progress = (timestamp - scene_start) / max(scene_end - scene_start, 0.001)
        caption = ""
        caption_progress = 0.0
        for line in timing["lines"]:
            if float(line["start"]) <= timestamp <= float(line["end"]):
                caption = line["text"]
                caption_progress = (timestamp - float(line["start"])) / max(
                    float(line["duration"]), 0.001
                )
                break
        return {
            "frame": int(frame_index),
            "timestamp": timestamp,
            "scene": scene["id"],
            "scene_progress": max(0.0, min(1.0, scene_progress)),
            "caption": caption,
            "caption_progress": max(0.0, min(1.0, caption_progress)),
            "timing": timing,
        }


class FrameRendererProcessor(ProcessorNode):
    def __init__(
        self,
        output_dir: str,
        project_path: str,
        assets_dir: str,
        **kwargs: Any,
    ) -> None:
        self._output_dir = str(output_dir)
        self._project_path = str(project_path)
        self._assets_dir = str(assets_dir)
        super().__init__(**kwargs)

    def open(self) -> None:
        Path(self._output_dir).mkdir(parents=True, exist_ok=True)

    def process(self, state: dict[str, Any]) -> dict[str, Any]:
        path = Path(self._output_dir) / f"frame_{int(state['frame']):05d}.jpg"
        render_frame(
            state,
            self._project_path,
            self._assets_dir,
            path,
        )
        return {
            "frame": int(state["frame"]),
            "timestamp": float(state["timestamp"]),
            "scene": state["scene"],
            "path": str(path),
        }


class FrameManifestConsumer(ConsumerNode):
    def __init__(self, manifest_path: str, **kwargs: Any) -> None:
        self._manifest_path = str(manifest_path)
        self._events_path: Path | None = None
        self._events_file = None
        super().__init__(**kwargs)

    def open(self) -> None:
        self._events_path = Path(self._manifest_path).with_suffix(".jsonl")
        self._events_path.parent.mkdir(parents=True, exist_ok=True)
        self._events_file = self._events_path.open("w", encoding="utf-8")

    def consume(self, item: dict[str, Any]) -> None:
        if self._events_file is None:
            raise RuntimeError("Manifest consumer opened without an output file")
        self._events_file.write(json.dumps(item, sort_keys=True) + "\n")

    def close(self) -> None:
        if self._events_file is not None:
            self._events_file.close()
        if self._events_path is None:
            return
        events = [
            json.loads(line)
            for line in self._events_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        events.sort(key=lambda item: int(item["frame"]))
        Path(self._manifest_path).write_text(
            json.dumps(
                {
                    "frame_count": len(events),
                    "frames": events,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
