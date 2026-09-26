from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseCartridge(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this cartridge (e.g. 'bedtime_story')."""
        pass

    @property
    def command(self) -> str:
        """
        The slash command triggering this cartridge in Telegram/channels.
        Defaults to the cartridge name if not overridden.
        """
        return self.name

    @property
    @abstractmethod
    def description(self) -> str:
        """Short human-readable description of what this cartridge does."""
        pass

    @abstractmethod
    async def generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the cartridge logic.
        
        Args:
            payload: Input dictionary containing parameters (e.g., name, age, theme).
            
        Returns:
            Dict containing:
                - status: 'success' or 'error'
                - output_file: path to generated file (or 'output_files' list)
                - title: human-readable title
                - script: text content if applicable
                - metadata: extra metadata dictionary
        """
        pass
