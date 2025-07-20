"""
Slate Detection Module for DaVinci Resolve MCP Server

This module provides functionality to detect slate information from video clips
and automatically rename them based on the detected information.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass

# Try to import required dependencies
try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    # Create placeholder for type hints
    class np:
        ndarray = Any

try:
    import pytesseract
    from PIL import Image
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

logger = logging.getLogger("slate_detection")

@dataclass
class SlateInfo:
    """Container for slate information extracted from video frames."""
    production: Optional[str] = None
    slate_number: Optional[str] = None
    scene: Optional[str] = None
    take: Optional[str] = None
    roll: Optional[str] = None
    camera: Optional[str] = None
    director: Optional[str] = None
    date: Optional[str] = None
    confidence: float = 0.0
    frame_number: int = 0


class SlateDetector:
    """Detects slate information from video frames using OCR."""
    
    def __init__(self):
        self.confidence_threshold = 0.3
        
    def analyze_frame(self, frame: np.ndarray) -> SlateInfo:
        """
        Analyze a video frame for slate information.
        
        Args:
            frame: OpenCV frame (numpy array)
            
        Returns:
            SlateInfo object with detected information
        """
        if not HAS_TESSERACT or not HAS_OPENCV:
            return SlateInfo(confidence=0.0)
            
        try:
            # Convert frame to PIL Image for tesseract
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(pil_image, config='--psm 6')
            
            # Parse the text for slate information
            slate_info = self._parse_slate_text(text)
            
            # Calculate confidence based on detected information
            slate_info.confidence = self._calculate_confidence(slate_info, text)
            
            return slate_info
            
        except Exception as e:
            logger.error(f"Error analyzing frame: {e}")
            return SlateInfo(confidence=0.0)
    
    def _parse_slate_text(self, text: str) -> SlateInfo:
        """Parse OCR text to extract slate information."""
        slate_info = SlateInfo()
        
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip().upper()
            
            # Look for common slate patterns
            if 'SLATE' in line or 'SCENE' in line:
                # Extract scene/slate number
                words = line.split()
                for i, word in enumerate(words):
                    if word in ['SLATE', 'SCENE'] and i + 1 < len(words):
                        potential_number = words[i + 1].strip(':')
                        if potential_number.replace('/', '').replace('-', '').isalnum():
                            if 'SLATE' in word:
                                slate_info.slate_number = potential_number
                            else:
                                slate_info.scene = potential_number
            
            if 'TAKE' in line:
                words = line.split()
                for i, word in enumerate(words):
                    if 'TAKE' in word and i + 1 < len(words):
                        potential_take = words[i + 1].strip(':')
                        if potential_take.isdigit():
                            slate_info.take = potential_take
            
            if 'ROLL' in line:
                words = line.split()
                for i, word in enumerate(words):
                    if 'ROLL' in word and i + 1 < len(words):
                        potential_roll = words[i + 1].strip(':')
                        if potential_roll.replace('/', '').replace('-', '').isalnum():
                            slate_info.roll = potential_roll
            
            if 'CAMERA' in line or 'CAM' in line:
                words = line.split()
                for i, word in enumerate(words):
                    if 'CAMERA' in word or 'CAM' in word:
                        if i + 1 < len(words):
                            potential_camera = words[i + 1].strip(':')
                            if potential_camera.replace('/', '').replace('-', '').isalnum():
                                slate_info.camera = potential_camera
            
            # Look for production name (usually appears early in the slate)
            if len(line) > 5 and not any(keyword in line for keyword in ['SLATE', 'SCENE', 'TAKE', 'ROLL', 'CAMERA']):
                if not slate_info.production and line.replace(' ', '').isalnum():
                    slate_info.production = line
        
        return slate_info
    
    def _calculate_confidence(self, slate_info: SlateInfo, raw_text: str) -> float:
        """Calculate confidence score based on detected information."""
        confidence = 0.0
        
        # Base confidence from text quality
        if len(raw_text.strip()) > 10:
            confidence += 0.1
        
        # Add confidence for each detected field
        if slate_info.slate_number:
            confidence += 0.3
        if slate_info.scene:
            confidence += 0.2
        if slate_info.take:
            confidence += 0.2
        if slate_info.roll:
            confidence += 0.1
        if slate_info.camera:
            confidence += 0.1
        if slate_info.production:
            confidence += 0.1
        
        return min(confidence, 1.0)


class ClipRenamer:
    """Handles renaming of clips based on slate information."""
    
    def __init__(self, resolve_api):
        self.resolve_api = resolve_api
        
    def generate_clip_name(self, slate_info: SlateInfo, original_name: str) -> str:
        """
        Generate a new clip name based on slate information.
        
        Args:
            slate_info: Detected slate information
            original_name: Original clip name
            
        Returns:
            Generated clip name
        """
        name_parts = []
        
        # Add production name if available
        if slate_info.production:
            name_parts.append(slate_info.production)
        
        # Add scene information
        if slate_info.scene:
            name_parts.append(f"Scene_{slate_info.scene}")
        elif slate_info.slate_number:
            name_parts.append(f"Slate_{slate_info.slate_number}")
        
        # Add take information
        if slate_info.take:
            name_parts.append(f"Take_{slate_info.take}")
        
        # Add camera information if available
        if slate_info.camera:
            name_parts.append(f"Cam_{slate_info.camera}")
        
        # If no useful information was found, return original name
        if not name_parts:
            return original_name
        
        # Join parts with underscores
        new_name = "_".join(name_parts)
        
        # Preserve file extension if present in original name
        if '.' in original_name:
            extension = original_name.split('.')[-1]
            if not new_name.endswith(f'.{extension}'):
                new_name = f"{new_name}.{extension}"
        
        return new_name
    
    def rename_clip(self, clip, new_name: str) -> bool:
        """
        Rename a clip in DaVinci Resolve.
        
        Args:
            clip: DaVinci Resolve clip object
            new_name: New name for the clip
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return clip.SetClipProperty("Clip Name", new_name)
        except Exception as e:
            logger.error(f"Error renaming clip: {e}")
            return False


def analyze_video_for_slate(video_path: str, max_frames: int = 30) -> SlateInfo:
    """
    Analyze a video file for slate information.
    
    Args:
        video_path: Path to the video file
        max_frames: Maximum number of frames to analyze
        
    Returns:
        SlateInfo object with detected information
    """
    if not HAS_OPENCV:
        raise ImportError("OpenCV is required for video analysis")
    
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    detector = SlateDetector()
    best_slate_info = SlateInfo()
    
    try:
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Analyze every 5th frame to save processing time
            if frame_count % 5 == 0:
                slate_info = detector.analyze_frame(frame)
                slate_info.frame_number = frame_count
                
                # Keep the slate info with highest confidence
                if slate_info.confidence > best_slate_info.confidence:
                    best_slate_info = slate_info
                
                # If we found high-confidence slate info, we can stop early
                if slate_info.confidence > 0.8:
                    break
            
            frame_count += 1
        
        cap.release()
        
    except Exception as e:
        logger.error(f"Error analyzing video {video_path}: {e}")
        raise
    
    return best_slate_info


def analyze_clips_and_rename(resolve_api, folder, dry_run: bool = True) -> Dict[str, Any]:
    """
    Analyze all clips in a folder and rename them based on slate information.
    
    Args:
        resolve_api: DaVinci Resolve API instance
        folder: Media pool folder to analyze
        dry_run: If True, only simulate renaming
        
    Returns:
        Dictionary with analysis results
    """
    if not HAS_OPENCV or not HAS_TESSERACT:
        return {"error": "Required dependencies not available. Install opencv-python and pytesseract."}
    
    try:
        clips = folder.GetClips()
        if not clips:
            return {"error": "No clips found in the specified folder."}
        
        results = {
            "analyzed_clips": 0,
            "successful_renames": 0,
            "failed_renames": 0,
            "clip_results": []
        }
        
        renamer = ClipRenamer(resolve_api)
        
        for clip in clips:
            clip_name = clip.GetName()
            clip_path = clip.GetClipProperty("File Path")
            
            clip_result = {
                "original_name": clip_name,
                "status": "error"
            }
            
            results["analyzed_clips"] += 1
            
            if not clip_path or not os.path.exists(clip_path):
                clip_result["reason"] = "File path not found or file does not exist"
                clip_result["status"] = "skipped"
                results["clip_results"].append(clip_result)
                continue
            
            try:
                # Analyze the video for slate information
                slate_info = analyze_video_for_slate(clip_path)
                
                if slate_info.confidence < 0.3:
                    clip_result["reason"] = f"Low confidence slate detection ({slate_info.confidence:.2f})"
                    clip_result["status"] = "skipped"
                    results["clip_results"].append(clip_result)
                    continue
                
                # Generate new name
                new_name = renamer.generate_clip_name(slate_info, clip_name)
                
                if new_name == clip_name:
                    clip_result["reason"] = "Generated name same as original"
                    clip_result["status"] = "skipped"
                    results["clip_results"].append(clip_result)
                    continue
                
                clip_result["new_name"] = new_name
                clip_result["slate_info"] = {
                    "production": slate_info.production,
                    "slate_number": slate_info.slate_number,
                    "scene": slate_info.scene,
                    "take": slate_info.take,
                    "roll": slate_info.roll,
                    "camera": slate_info.camera
                }
                clip_result["confidence"] = slate_info.confidence
                
                # Perform rename if not dry run
                if not dry_run:
                    success = renamer.rename_clip(clip, new_name)
                    if success:
                        clip_result["status"] = "renamed"
                        results["successful_renames"] += 1
                    else:
                        clip_result["status"] = "error"
                        clip_result["reason"] = "Failed to rename clip"
                        results["failed_renames"] += 1
                else:
                    clip_result["status"] = "renamed"  # Simulated rename
                    results["successful_renames"] += 1
                
            except Exception as e:
                clip_result["reason"] = f"Analysis error: {str(e)}"
                clip_result["status"] = "error"
                results["failed_renames"] += 1
            
            results["clip_results"].append(clip_result)
        
        return results
        
    except Exception as e:
        return {"error": f"Failed to analyze clips: {str(e)}"}