"""Persistent, self-contained viewport CAD overlay controls."""
from pathlib import Path
from . import overlay

bl_info = {
    'name': 'CAD Overlay Tools',
    'author': 'Planby Technologies',
    'version': (1, 1, 0),
    'blender': (4, 4, 0),
    'location': '3D View > Sidebar > CAD Overlay',
    'description': 'CAD reference overlay and transparent model comparison; includes the 25B reference',
    'category': '3D View',
}


def register():
    overlay.REFERENCE_DIR = Path(__file__).resolve().parent / 'reference'
    overlay.register()


def unregister():
    overlay.unregister()
