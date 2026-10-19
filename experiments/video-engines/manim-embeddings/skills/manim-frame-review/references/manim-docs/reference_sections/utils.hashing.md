## utils.hashing
# hashing

Utilities for scene caching.

### Functions

### get_hash_from_play_call(scene_object, camera_object, animations_list, current_mobjects_list, , backend, encoder_fingerprint, renderer_state)

Return the visual-segment cache key for one compiled play call.

* **Parameters:**
  * **scene_object** ([*Scene*](manim.scene.scene.Scene.md#manim.scene.scene.Scene)) – The scene object.
  * **camera_object** ([*Camera*](manim.camera.camera.Camera.md#manim.camera.camera.Camera) *|* *OpenGLCamera*) – The camera object used in the scene.
  * **animations_list** (*Iterable* *[*[*Animation*](manim.animation.animation.Animation.md#manim.animation.animation.Animation) *]*) – The list of animations.
  * **current_mobjects_list** (*Iterable* *[*[*Mobject*](manim.mobject.mobject.Mobject.md#manim.mobject.mobject.Mobject) *]*) – The list of mobjects.
  * **backend** (*str*) – Stable identity of the renderer producing the segment.
  * **encoder_fingerprint** (*str*) – Stable identity of the resolved segment encoder settings.
  * **renderer_state** (*Any*) – Additional renderer-specific state which affects segment pixels.
* **Returns:**
  A filename-safe digest of all visual cache inputs.
* **Return type:**
  `str`

### get_json(obj, , include_pixel_array=False)

Recursively serialize object to JSON using the `CustomEncoder` class.

* **Parameters:**
  * **obj** (*Any*) – The dict to flatten
  * **include_pixel_array** (*bool*) – Whether to include pixel arrays encountered while flattening the object.
* **Returns:**
  The flattened object
* **Return type:**
  `str`

