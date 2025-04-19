from desktop_use import DesktopUseClient, Locator, ApiError, sleep, ElementResponse
import time
from typing import Dict, Any, Optional

class ScreenService:
    def __init__(self, base_url: str = '127.0.0.1:3000'):
        """Initialize the screen monitoring service using Terminator"""
        try:
            self.client = DesktopUseClient(base_url=base_url)
            self._connected = True
        except Exception as e:
            print(f"Could not connect to Terminator server: {e}")
            self._connected = False
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to Terminator server"""
        return self._connected
    
    def capture_screen_content(self) -> Dict[str, Any]:
        """Capture current screen content/state"""
        if not self._connected:
            return {"error": "Not connected to Terminator server"}
        
        try:
            # Get the active window
            active_window = self._get_active_window()
            if not active_window:
                return {"error": "No active window detected"}
            
            # Extract text from the active window
            window_content = self._extract_text_from_window(active_window)
            
            return {
                "window_title": active_window.get("title", "Unknown"),
                "content": window_content,
                "timestamp": time.time()
            }
        except ApiError as e:
            return {"error": f"Terminator API error: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}
    
    def _get_active_window(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently active window"""
        try:
            active_window = self.client.get_active_window()
            if active_window:
                return {
                    "title": active_window.title,
                    "id": active_window.id
                }
            return None
        except ApiError as e:
            print(f"Error getting active window: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error getting active window: {e}")
            return None
    
    def _extract_text_from_window(self, window_info: Dict[str, Any]) -> str:
        """Extract text content from the specified window"""
        try:
            # Use the window ID to locate text elements
            window_locator = Locator(f'window:{window_info["id"]}')
            text_elements = self.client.locate_all(window_locator)
            
            # Extract text from all located elements
            extracted_text = []
            for element in text_elements:
                if isinstance(element, ElementResponse) and element.label:
                    extracted_text.append(element.label)
            
            return "\n".join(extracted_text)
        except ApiError as e:
            print(f"Error extracting text from window: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected error extracting text: {e}")
            return ""
    
    def monitor_math_application(self, app_name: str = "Calculator") -> Dict[str, Any]:
        """Specifically monitor math applications like calculator"""
        if not self._connected:
            return {"error": "Not connected to Terminator server"}
        
        try:
            # Open the application if it's not already open
            self.client.open_application(app_name)
            sleep(1000)  # Give time for app to open
            
            # For calculator, we could get the display value
            if app_name.lower() == "calculator":
                calc_window = self.client.locator(f'window:{app_name}')
                display = calc_window.locator('name:CalculatorResults')
                result = display.get_text()
                
                return {
                    "application": app_name,
                    "current_value": result.text if hasattr(result, 'text') else "Unknown",
                    "timestamp": time.time()
                }
            
            return {"application": app_name, "status": "monitoring"}
            
        except ApiError as e:
            return {"error": f"Terminator API error: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}