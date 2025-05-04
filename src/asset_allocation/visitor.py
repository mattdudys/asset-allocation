from abc import ABC, abstractmethod
from typing import Any


class Visitor(ABC):
    """Abstract base class for visitors that traverse the asset allocation structure.
    
    This visitor pattern allows for different operations to be performed on the
    hierarchical structure of AssetClassCategory, AssetClass, and Holding nodes
    without modifying their classes.
    """
    
    @abstractmethod
    def visit_asset_class_category(self, category: 'AssetClassCategory') -> Any:
        """Visit an AssetClassCategory node.
        
        Args:
            category: The AssetClassCategory node being visited
            
        Returns:
            Any result from visiting this node
        """
        pass
    
    @abstractmethod
    def visit_asset_class(self, asset_class: 'AssetClass') -> Any:
        """Visit an AssetClass node.
        
        Args:
            asset_class: The AssetClass node being visited
            
        Returns:
            Any result from visiting this node
        """
        pass
    
    @abstractmethod
    def visit_holding(self, holding: 'Holding') -> Any:
        """Visit a Holding node.
        
        Args:
            holding: The Holding node being visited
            
        Returns:
            Any result from visiting this node
        """
        pass 