"""
Core data models for CurioShelf
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json


@dataclass
class ObjectSlice:
    """Represents a named rectangular selection inside a source file"""
    name: str
    source_id: str
    x: int
    y: int
    width: int
    height: int
    layer: str = "concept"  # concept, working, production
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "source_id": self.source_id,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "layer": self.layer
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ObjectSlice':
        return cls(**data)


@dataclass
class AssetSource:
    """Represents a source file with associated slices"""
    id: str
    file_path: Path
    file_type: str  # svg, png, jpg, etc.
    width: int
    height: int
    slices: List[ObjectSlice] = field(default_factory=list)
    
    def add_slice(self, slice_obj: ObjectSlice) -> None:
        """Add a slice to this source"""
        self.slices.append(slice_obj)
    
    def remove_slice(self, slice_name: str) -> bool:
        """Remove a slice by name, returns True if found and removed"""
        for i, slice_obj in enumerate(self.slices):
            if slice_obj.name == slice_name:
                del self.slices[i]
                return True
        return False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "file_path": str(self.file_path),
            "file_type": self.file_type,
            "width": self.width,
            "height": self.height,
            "slices": [slice_obj.to_dict() for slice_obj in self.slices]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AssetSource':
        slices = [ObjectSlice.from_dict(slice_data) for slice_data in data.get("slices", [])]
        return cls(
            id=data["id"],
            file_path=Path(data["file_path"]),
            file_type=data["file_type"],
            width=data["width"],
            height=data["height"],
            slices=slices
        )


@dataclass
class Template:
    """Defines required slice names for a type of object"""
    name: str
    description: str
    required_views: List[str]  # e.g., ["front", "back", "walk1", "walk2"]
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "required_views": self.required_views
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Template':
        return cls(**data)


@dataclass
class CurioObject:
    """Tracks all slices for an object across layers"""
    id: str
    name: str
    template_name: Optional[str] = None
    sources: Dict[str, AssetSource] = field(default_factory=dict)  # layer -> source
    slices: List[ObjectSlice] = field(default_factory=list)
    
    def add_source(self, layer: str, source: AssetSource) -> None:
        """Add a source for a specific layer"""
        self.sources[layer] = source
    
    def get_slices_for_view(self, view_name: str) -> List[ObjectSlice]:
        """Get all slices for a specific view across all layers"""
        return [slice_obj for slice_obj in self.slices if slice_obj.name == view_name]
    
    def get_missing_views(self, template: Optional[Template] = None) -> List[str]:
        """Get list of missing required views based on template"""
        if not template:
            return []
        
        existing_views = set(slice_obj.name for slice_obj in self.slices)
        return [view for view in template.required_views if view not in existing_views]
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "template_name": self.template_name,
            "sources": {layer: source.to_dict() for layer, source in self.sources.items()},
            "slices": [slice_obj.to_dict() for slice_obj in self.slices]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CurioObject':
        sources = {
            layer: AssetSource.from_dict(source_data) 
            for layer, source_data in data.get("sources", {}).items()
        }
        slices = [ObjectSlice.from_dict(slice_data) for slice_data in data.get("slices", [])]
        return cls(
            id=data["id"],
            name=data["name"],
            template_name=data.get("template_name"),
            sources=sources,
            slices=slices
        )


class AssetManager:
    """Coordinates sources, objects, and templates"""
    
    def __init__(self) -> None:
        self.sources: Dict[str, AssetSource] = {}
        self.objects: Dict[str, CurioObject] = {}
        self.templates: Dict[str, Template] = {}
        self._next_id = 1
    
    def generate_id(self) -> str:
        """Generate a unique ID"""
        id_str = f"id_{self._next_id}"
        self._next_id += 1
        return id_str
    
    def add_source(self, file_path: Path, width: int, height: int) -> AssetSource:
        """Add a new source file"""
        source_id = self.generate_id()
        file_type = file_path.suffix.lower().lstrip('.')
        
        source = AssetSource(
            id=source_id,
            file_path=file_path,
            file_type=file_type,
            width=width,
            height=height
        )
        
        self.sources[source_id] = source
        return source
    
    def add_object(self, name: str, template_name: Optional[str] = None) -> CurioObject:
        """Add a new object"""
        object_id = self.generate_id()
        obj = CurioObject(
            id=object_id,
            name=name,
            template_name=template_name
        )
        
        self.objects[object_id] = obj
        return obj
    
    def add_template(self, name: str, description: str, required_views: List[str]) -> Template:
        """Add a new template"""
        template = Template(
            name=name,
            description=description,
            required_views=required_views
        )
        
        self.templates[name] = template
        return template
    
    def get_object_completeness(self, object_id: str) -> Dict[str, bool]:
        """Get completeness status for an object's required views"""
        obj = self.objects.get(object_id)
        if not obj or not obj.template_name:
            return {}
        
        template = self.templates.get(obj.template_name)
        if not template:
            return {}
        
        existing_views = set(slice_obj.name for slice_obj in obj.slices)
        return {view: view in existing_views for view in template.required_views}
    
    def save_metadata(self, file_path: Path) -> None:
        """Save all metadata to a JSON file"""
        data = {
            "sources": {sid: source.to_dict() for sid, source in self.sources.items()},
            "objects": {oid: obj.to_dict() for oid, obj in self.objects.items()},
            "templates": {tname: template.to_dict() for tname, template in self.templates.items()}
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_metadata(self, file_path: Path) -> None:
        """Load metadata from a JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Clear existing data
        self.sources.clear()
        self.objects.clear()
        self.templates.clear()
        
        # Load sources
        for sid, source_data in data.get("sources", {}).items():
            self.sources[sid] = AssetSource.from_dict(source_data)
        
        # Load objects
        for oid, obj_data in data.get("objects", {}).items():
            self.objects[oid] = CurioObject.from_dict(obj_data)
        
        # Load templates
        for tname, template_data in data.get("templates", {}).items():
            self.templates[tname] = Template.from_dict(template_data)
