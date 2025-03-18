#!/usr/bin/env python
"""
Basic example of using the DaVinci Resolve MCP Server.

This script demonstrates how to manually connect to the MCP server
and execute some basic operations with DaVinci Resolve.
"""

import sys
import os
import time
import json
from typing import Dict, Any

# Add the parent directory to the path so we can import the resolve_mcp package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.resolve_mcp.resolve_api import ResolveAPI

def main():
    """Main function to demonstrate basic usage of the DaVinci Resolve API."""
    print("Connecting to DaVinci Resolve...")
    resolve_api = ResolveAPI()
    
    if not resolve_api.is_connected():
        print("Failed to connect to DaVinci Resolve. Make sure DaVinci Resolve is running.")
        return
    
    print("Successfully connected to DaVinci Resolve.")
    
    # Get the current project
    project = resolve_api.get_current_project()
    if project:
        print(f"Current project: {project.GetName()}")
    else:
        print("No project is currently open.")
        
        # Create a new project
        project_name = f"Example Project {int(time.time())}"
        print(f"Creating a new project: {project_name}")
        if resolve_api.create_project(project_name):
            print(f"Successfully created project: {project_name}")
            project = resolve_api.get_current_project()
        else:
            print(f"Failed to create project: {project_name}")
            return
    
    # Create a new timeline
    timeline_name = f"Example Timeline {int(time.time())}"
    print(f"Creating a new timeline: {timeline_name}")
    if resolve_api.create_timeline(timeline_name):
        print(f"Successfully created timeline: {timeline_name}")
    else:
        print(f"Failed to create timeline: {timeline_name}")
    
    # Get the current timeline
    timeline = resolve_api.get_current_timeline()
    if timeline:
        print(f"Current timeline: {timeline.GetName()}")
        print(f"Timeline duration: {timeline.GetEndFrame() - timeline.GetStartFrame() + 1} frames")
        print(f"Video tracks: {timeline.GetTrackCount('video')}")
        print(f"Audio tracks: {timeline.GetTrackCount('audio')}")
    else:
        print("No timeline is currently open.")
    
    # Get media storage information
    print("\nMedia Storage Information:")
    volumes = resolve_api.get_mounted_volumes()
    if volumes:
        print("Mounted volumes:")
        for i, volume in enumerate(volumes, 1):
            print(f"  {i}. {volume}")
    else:
        print("No mounted volumes available.")
    
    # Get media pool information
    print("\nMedia Pool Information:")
    media_pool = resolve_api.get_media_pool()
    if media_pool:
        root_folder = media_pool.GetRootFolder()
        if root_folder:
            print(f"Root folder: {root_folder.GetName()}")
            
            # Print folder structure
            def print_folder_structure(folder, indent=""):
                name = folder.GetName()
                print(f"{indent}- {name}")
                
                subfolders = folder.GetSubFolders()
                for subfolder in subfolders:
                    print_folder_structure(subfolder, indent + "  ")
            
            print("Folder structure:")
            print_folder_structure(root_folder)
        else:
            print("No root folder available.")
    else:
        print("No media pool available.")
    
    # Save the project
    if resolve_api.save_project():
        print(f"Successfully saved project: {project.GetName()}")
    else:
        print(f"Failed to save project: {project.GetName()}")

if __name__ == "__main__":
    main()
