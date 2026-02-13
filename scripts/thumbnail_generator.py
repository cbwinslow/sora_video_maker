"""
Thumbnail Generator Tool

This tool generates eye-catching thumbnails for videos.
"""

import os
import logging
from typing import Optional, Tuple, List

try:
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL/Pillow not available. Thumbnail generation will be limited.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThumbnailGenerator:
    """Generate professional thumbnails for videos"""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.default_size = (1280, 720)  # YouTube recommended size
        self.font_path = self.config.get('font_path', None)

        if not PIL_AVAILABLE:
            logger.warning("PIL not available. Thumbnail generation disabled.")

    def create_text_thumbnail(self, text: str, output_path: str,
                             bg_color: Tuple[int, int, int] = (41, 128, 185),
                             text_color: Tuple[int, int, int] = (255, 255, 255),
                             size: Optional[Tuple[int, int]] = None) -> bool:
        """
        Create a simple text-based thumbnail

        Args:
            text: Text to display on thumbnail
            output_path: Path to save thumbnail
            bg_color: Background color (R, G, B)
            text_color: Text color (R, G, B)
            size: Thumbnail size (width, height)

        Returns:
            True if successful, False otherwise
        """
        if not PIL_AVAILABLE:
            logger.error("PIL not available")
            return False

        try:
            size = size or self.default_size

            # Create image with background
            img = Image.new('RGB', size, bg_color)
            draw = ImageDraw.Draw(img)

            # Load font (try to use system font or default)
            try:
                font_size = 80
                if self.font_path and os.path.exists(self.font_path):
                    font = ImageFont.truetype(self.font_path, font_size)
                else:
                    # Try common font locations
                    common_fonts = [
                        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                        '/System/Library/Fonts/Helvetica.ttc',
                        'C:\\Windows\\Fonts\\arial.ttf'
                    ]
                    font = None
                    for font_path in common_fonts:
                        if os.path.exists(font_path):
                            font = ImageFont.truetype(font_path, font_size)
                            break

                    if font is None:
                        font = ImageFont.load_default()
                        logger.warning("Using default font")
            except Exception as e:
                font = ImageFont.load_default()
                logger.warning(f"Font loading failed: {e}")

            # Word wrap text
            words = text.split()
            lines = []
            current_line = []

            for word in words:
                test_line = ' '.join(current_line + [word])
                # Simple width estimation
                if len(test_line) > 20:  # Rough character limit per line
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                else:
                    current_line.append(word)

            if current_line:
                lines.append(' '.join(current_line))

            # Calculate text position (centered)
            line_height = font_size + 20
            total_height = len(lines) * line_height
            y = (size[1] - total_height) // 2

            # Draw each line
            for line in lines:
                # Get text bounding box
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (size[0] - text_width) // 2

                # Draw text shadow
                draw.text((x + 3, y + 3), line, fill=(0, 0, 0), font=font)
                # Draw main text
                draw.text((x, y), line, fill=text_color, font=font)

                y += line_height

            # Save thumbnail
            img.save(output_path, 'PNG', quality=95)
            logger.info(f"Thumbnail created: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            return False

    def create_gradient_thumbnail(self, text: str, output_path: str,
                                 color1: Tuple[int, int, int] = (41, 128, 185),
                                 color2: Tuple[int, int, int] = (109, 213, 250),
                                 size: Optional[Tuple[int, int]] = None) -> bool:
        """
        Create thumbnail with gradient background

        Args:
            text: Text to display
            output_path: Path to save thumbnail
            color1: Start gradient color
            color2: End gradient color
            size: Thumbnail size

        Returns:
            True if successful
        """
        if not PIL_AVAILABLE:
            return False

        try:
            size = size or self.default_size

            # Create gradient
            img = Image.new('RGB', size, color1)
            draw = ImageDraw.Draw(img)

            # Draw gradient
            for y in range(size[1]):
                ratio = y / size[1]
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.line([(0, y), (size[0], y)], fill=(r, g, b))

            # Add text overlay
            try:
                font = ImageFont.load_default()

                # Word wrap
                words = text.split()
                lines = []
                current_line = []

                for word in words:
                    test_line = ' '.join(current_line + [word])
                    if len(test_line) > 20:
                        if current_line:
                            lines.append(' '.join(current_line))
                            current_line = [word]
                    else:
                        current_line.append(word)

                if current_line:
                    lines.append(' '.join(current_line))

                # Draw text
                line_height = 60
                total_height = len(lines) * line_height
                y = (size[1] - total_height) // 2

                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                    x = (size[0] - text_width) // 2

                    # Shadow
                    draw.text((x + 5, y + 5), line, fill=(0, 0, 0, 180), font=font)
                    # Main text
                    draw.text((x, y), line, fill=(255, 255, 255), font=font)
                    y += line_height

            except Exception as e:
                logger.warning(f"Text overlay failed: {e}")

            img.save(output_path, 'PNG', quality=95)
            logger.info(f"Gradient thumbnail created: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating gradient thumbnail: {e}")
            return False

    def extract_frame_as_thumbnail(self, video_path: str, output_path: str,
                                   timestamp: float = 1.0,
                                   add_text: Optional[str] = None) -> bool:
        """
        Extract a frame from video and use as thumbnail

        Args:
            video_path: Path to video file
            output_path: Path to save thumbnail
            timestamp: Time in seconds to extract frame
            add_text: Optional text to overlay

        Returns:
            True if successful
        """
        import subprocess

        try:
            # Extract frame using ffmpeg
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-ss', str(timestamp),
                '-vframes', '1',
                '-q:v', '2',
                '-y',
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, check=True)

            # Add text overlay if requested
            if add_text and PIL_AVAILABLE:
                img = Image.open(output_path)

                # Enhance image
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.2)

                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(1.3)

                draw = ImageDraw.Draw(img)
                font = ImageFont.load_default()

                # Add text at bottom
                text_y = img.size[1] - 100
                bbox = draw.textbbox((0, 0), add_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_x = (img.size[0] - text_width) // 2

                # Background rectangle
                padding = 20
                rect_coords = [
                    (text_x - padding, text_y - padding),
                    (text_x + text_width + padding, text_y + 60 + padding)
                ]
                draw.rectangle(rect_coords, fill=(0, 0, 0, 180))

                # Text
                draw.text((text_x, text_y), add_text, fill=(255, 255, 255), font=font)

                img.save(output_path)

            logger.info(f"Frame extracted as thumbnail: {output_path}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"ffmpeg error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error extracting frame: {e}")
            return False

    def create_collage_thumbnail(self, images: List[str], output_path: str,
                                text: Optional[str] = None,
                                size: Optional[Tuple[int, int]] = None) -> bool:
        """
        Create a collage thumbnail from multiple images

        Args:
            images: List of image paths
            output_path: Path to save thumbnail
            text: Optional text overlay
            size: Thumbnail size

        Returns:
            True if successful
        """
        if not PIL_AVAILABLE:
            return False

        try:
            size = size or self.default_size

            # Create base image
            thumbnail = Image.new('RGB', size, (0, 0, 0))

            # Calculate grid
            num_images = min(len(images), 4)  # Max 4 images
            cols = 2 if num_images > 2 else num_images
            rows = (num_images + cols - 1) // cols

            cell_width = size[0] // cols
            cell_height = size[1] // rows

            # Place images
            for i, img_path in enumerate(images[:num_images]):
                if not os.path.exists(img_path):
                    continue

                try:
                    img = Image.open(img_path)
                    img = img.resize((cell_width, cell_height), Image.Resampling.LANCZOS)

                    col = i % cols
                    row = i // cols
                    x = col * cell_width
                    y = row * cell_height

                    thumbnail.paste(img, (x, y))
                except Exception as e:
                    logger.warning(f"Failed to process image {img_path}: {e}")

            # Add text overlay if provided
            if text:
                draw = ImageDraw.Draw(thumbnail)
                font = ImageFont.load_default()

                # Create semi-transparent overlay
                overlay = Image.new('RGBA', size, (0, 0, 0, 128))
                thumbnail = thumbnail.convert('RGBA')
                thumbnail = Image.alpha_composite(thumbnail, overlay)

                draw = ImageDraw.Draw(thumbnail)
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_x = (size[0] - text_width) // 2
                text_y = size[1] // 2 - 30

                draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)

                thumbnail = thumbnail.convert('RGB')

            thumbnail.save(output_path, 'PNG', quality=95)
            logger.info(f"Collage thumbnail created: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error creating collage: {e}")
            return False


def main():
    """Example usage"""
    generator = ThumbnailGenerator()

    if PIL_AVAILABLE:
        # Example 1: Simple text thumbnail
        generator.create_text_thumbnail(
            "AI Video Generation",
            "output/thumb1.png",
            bg_color=(231, 76, 60),
            text_color=(255, 255, 255)
        )

        # Example 2: Gradient thumbnail
        generator.create_gradient_thumbnail(
            "Amazing Tutorial",
            "output/thumb2.png",
            color1=(52, 152, 219),
            color2=(155, 89, 182)
        )

        print("Thumbnails created successfully!")
    else:
        print("PIL not available. Install Pillow to use thumbnail generation.")


if __name__ == '__main__':
    main()
