# ComfyUI Workflow Documentation

This directory contains pre-configured ComfyUI workflows for various video generation tasks.

## Available Workflows

### 1. text_to_image.json
Basic text-to-image generation workflow using Stable Diffusion XL.

**Usage:**
- Load in ComfyUI
- Edit the positive prompt in node 2
- Edit the negative prompt in node 3
- Click "Queue Prompt" to generate

**Requirements:**
- Stable Diffusion XL model (sd_xl_base_1.0.safetensors)

---

### 2. text_to_video_animatediff.json
Text-to-video generation using AnimateDiff for smooth animations.

**Usage:**
- Load in ComfyUI
- Provide text prompt in node 2
- Configure video parameters (frames, fps) in node 7
- Generate video with node 9

**Requirements:**
- Stable Diffusion XL model
- AnimateDiff motion module (mm_sd_v15_v2.ckpt)
- ComfyUI-AnimateDiff-Evolved extension
- ComfyUI-VideoHelperSuite extension

**Key Features:**
- Character consistency across frames
- Smooth motion generation
- Customizable frame count and FPS
- Direct video export

---

### 3. consistent_character_workflow.json
Generate consistent characters across multiple frames using IP-Adapter and ControlNet.

**Usage:**
- Load reference face image in node 4
- Load pose reference in node 8
- Adjust prompts for character description
- Generate consistent character

**Requirements:**
- Stable Diffusion XL model
- IP-Adapter (for face consistency)
- ControlNet OpenPose model
- Reference face image
- Pose reference image

**Key Features:**
- Face consistency using IP-Adapter
- Pose control using ControlNet
- Character customization via prompts
- High-quality output

**Workflow Nodes:**
1. Checkpoint Loader - Load base model
2. Positive Prompt - Character description
3. Negative Prompt - Things to avoid
4. Reference Face - Load face image
5. IP-Adapter Loader - Face consistency
6. IP-Adapter Apply - Apply face to generation
7. ControlNet Loader - Load pose model
8. Pose Reference - Load pose image
9. ControlNet Apply - Apply pose guidance
10. Sampler - Generate image
11-13. Decode and save

---

## How to Use Workflows

### Method 1: ComfyUI Interface

1. Start ComfyUI:
   ```bash
   cd ComfyUI
   python main.py
   ```

2. Open http://127.0.0.1:8188 in your browser

3. Load workflow:
   - Click "Load" button
   - Navigate to workflows directory
   - Select desired workflow JSON file

4. Configure parameters and generate

---

### Method 2: API (Programmatic)

```python
from scripts.api_integrations import ComfyUIAPI
import json

# Load workflow
with open('workflows/text_to_video_animatediff.json') as f:
    workflow = json.load(f)

# Queue workflow
api = ComfyUIAPI()
prompt_id = await api.queue_prompt(workflow)

# Get results
history = await api.get_history(prompt_id)
```

---

## Creating Custom Workflows

### Step 1: Design in ComfyUI
1. Open ComfyUI interface
2. Add and connect nodes
3. Test the workflow
4. Adjust parameters

### Step 2: Export Workflow
1. Click "Save" button
2. Choose "Save API Format"
3. Save to workflows directory

### Step 3: Document
1. Add to this README
2. List requirements
3. Provide usage instructions
4. Include example prompts

---

## Workflow Components

### Essential Nodes

**CheckpointLoaderSimple**
- Loads the base Stable Diffusion model
- Required for all workflows

**CLIPTextEncode**
- Converts text prompts to embeddings
- Used for positive and negative prompts

**KSampler / KSamplerAdvanced**
- Core generation node
- Controls sampling steps, CFG scale, etc.

**VAEDecode**
- Converts latents to images
- Final step before output

### Animation Nodes

**AnimateDiffLoader**
- Loads AnimateDiff motion module
- Required for video generation

**EmptyLatentVideo**
- Creates video latent space
- Set frame count and dimensions

**VHS_VideoCombine**
- Combines frames into video file
- Set FPS and output format

### Character Consistency Nodes

**IPAdapterUnifiedLoader**
- Loads IP-Adapter model
- For face/style consistency

**IPAdapterApply**
- Applies reference image
- Maintains character features

**ControlNetLoader**
- Loads ControlNet models
- For pose/composition control

**ControlNetApply**
- Applies ControlNet guidance
- Controls specific aspects

---

## Model Requirements

### Base Models
- **Stable Diffusion XL**: sd_xl_base_1.0.safetensors
- **Stable Diffusion 1.5**: (alternative)

### Motion Models
- **AnimateDiff v2**: mm_sd_v15_v2.ckpt
- **AnimateDiff v3**: mm_sd_v15_v3.ckpt (newer)

### ControlNet Models
- **OpenPose**: control_openpose.pth
- **Depth**: control_depth.pth
- **Canny**: control_canny.pth

### IP-Adapter Models
- **IP-Adapter Plus**: ip-adapter-plus_sd15.bin
- **IP-Adapter Face**: ip-adapter-face_sd15.bin

---

## Downloading Models

### Via ComfyUI Manager
1. Install ComfyUI Manager
2. Click "Manager" button
3. Search for required models
4. Click "Install"

### Manual Download
1. Download from HuggingFace or official sources
2. Place in appropriate directory:
   - Base models: `ComfyUI/models/checkpoints/`
   - ControlNet: `ComfyUI/models/controlnet/`
   - AnimateDiff: `ComfyUI/custom_nodes/ComfyUI-AnimateDiff-Evolved/models/`
   - IP-Adapter: `ComfyUI/models/ipadapter/`

---

## Tips for Best Results

### Text-to-Image
- Use detailed, specific prompts
- Include quality keywords: "masterpiece, best quality, 8k"
- Add style descriptors: "cinematic, dramatic lighting"
- Use negative prompts to avoid issues

### Text-to-Video
- Start with lower frame counts (16-32) for testing
- Use "(same person:1.3)" for character consistency
- Keep motion simple for better results
- Increase CFG scale for stronger adherence

### Consistent Characters
- Use high-quality reference images
- Match reference and target poses
- Adjust IP-Adapter strength (0.8-1.2)
- Use consistent lighting in prompts

---

## Troubleshooting

### Out of Memory
- Reduce resolution
- Lower frame count
- Use fp16 precision
- Close other applications

### Inconsistent Results
- Increase sampling steps (20-30)
- Adjust CFG scale (7-9)
- Use fixed seed for reproducibility
- Refine prompts

### Workflow Won't Load
- Check node names match installed extensions
- Verify model files exist
- Update ComfyUI and extensions
- Check JSON syntax

### Slow Generation
- Use smaller models
- Reduce resolution
- Lower frame count
- Enable xformers
- Use GPU acceleration

---

## Advanced Techniques

### Batch Processing
Configure batch size in workflow to generate multiple variations simultaneously.

### LoRA Integration
Add LoRA loader nodes to inject specific styles or concepts.

### Multi-ControlNet
Combine multiple ControlNets (pose + depth) for precise control.

### Upscaling
Add upscale nodes after generation for higher resolution output.

### Style Transfer
Use IP-Adapter with style reference images.

---

## Community Resources

- [ComfyUI Official](https://github.com/comfyanonymous/ComfyUI)
- [AnimateDiff](https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved)
- [IP-Adapter](https://github.com/cubiq/ComfyUI_IPAdapter_plus)
- [ComfyUI Examples](https://comfyanonymous.github.io/ComfyUI_examples/)

---

**Last Updated**: 2024-01-27
**Version**: 2.0
