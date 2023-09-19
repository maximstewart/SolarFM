# Python imports
from dataclasses import dataclass, field

# Lib imports

# Application imports


@dataclass
class Filters:
    meshs: list = field(default_factory=lambda: [
        ".blend",
        ".dae",
        ".fbx",
        ".gltf",
        ".obj",
        ".stl"
    ])
    code: list = field(default_factory=lambda: [
        ".cpp",
        ".css",
        ".c",
        ".go",
        ".html",
        ".htm",
        ".java",
        ".js",
        ".json",
        ".lua",
        ".md",
        ".py",
        ".rs",
        ".toml",
        ".xml",
        ".pom"
    ])
    videos: list = field(default_factory=lambda:[
        ".mkv",
        ".mp4",
        ".webm",
        ".avi",
        ".mov",
        ".m4v",
        ".mpg",
        ".mpeg",
        ".wmv",
        ".flv"
    ])
    office: list = field(default_factory=lambda: [
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".xlt",
        ".xltx",
        ".xlm",
        ".ppt",
        ".pptx",
        ".pps",
        ".ppsx",
        ".odt",
        ".rtf"
    ])
    images: list = field(default_factory=lambda: [
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".ico",
        ".tga",
        ".webp"
    ])
    text: list = field(default_factory=lambda: [
        ".txt",
        ".text",
        ".sh",
        ".cfg",
        ".conf",
        ".log"
    ])
    music: list = field(default_factory=lambda: [
        ".psf",
        ".mp3",
        ".ogg",
        ".flac",
        ".m4a"
    ])
    pdf: list = field(default_factory=lambda: [
        ".pdf"
    ])
