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

### 2. text_to_video.json (To be created)
Text-to-video generation using AnimateDiff.

**Usage:**
- Load in ComfyUI
- Provide text prompt
- Configure video parameters (frames, fps)
- Generate video

**Requirements:**
- AnimateDiff models
- ControlNet (optional)

### 3. image_to_video.json (To be created)
Convert static images to animated videos.

**Usage:**
- Load in ComfyUI
- Upload source image
- Configure animation parameters
- Generate video

**Requirements:**
- AnimateDiff models
- VideoHelperSuite

## How to Use Workflows

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

## Custom Workflows

You can create custom workflows by:
1. Building in ComfyUI interface
2. Saving as JSON
3. Placing in this directory
4. Documenting in this README

## Tips

- Use the ComfyUI Manager for easy node installation
- Check model requirements before running workflows
- Save outputs in organized directories
- Experiment with different parameters for best results
