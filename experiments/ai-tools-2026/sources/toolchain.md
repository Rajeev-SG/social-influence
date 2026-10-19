# Toolchain Sources

- HyperFrames authoring and CLI:
  https://hyperframes.heygen.com/quickstart
- Diffusion Studio Core 4.0.3 installation and architecture:
  https://docs.diffusion.studio/docs
- Diffusion Studio rendering API:
  https://docs.diffusion.studio/docs/rendering
- Blender 5.2.2 installed from the Homebrew cask `blender`; production scenes are
  scripted through Blender's Python API and rendered with the actual installed binary.
- Local narration uses the already installed Kokoro 82M q8 ONNX runtime and British
  `bf_emma` voice from `/Users/rajeev/Code/content-machine`. No new TTS weights are
  downloaded.
