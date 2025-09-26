"""
CurioShelf Sprite Generator

A plugin-based system for generating sprite sheets with various animations and styles.
"""

from .core import SpriteGenerator, SpritePlugin, SpriteMetadata, PluginSpriteData
from .plugins.stick_figure import StickFigurePlugin

__all__ = ['SpriteGenerator', 'SpritePlugin', 'SpriteMetadata', 'PluginSpriteData', 'StickFigurePlugin']
