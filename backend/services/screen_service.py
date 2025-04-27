try:
    from desktop_use import DesktopUseClient, Locator, ApiError, sleep, ElementResponse
    DESKTOP_USE_AVAILABLE = True
except ImportError:
    DESKTOP_USE_AVAILABLE = False
    print("Warning: desktop_use package not fully available. Some screen sharing features will be limited.")

from PIL import ImageGrab
import base64
from io import BytesIO
import time
from typing import Dict, Any, Optional

class ScreenService:
    def __init__(self, base_url: str = '127.0.0.1:3000'):
        """Initialize the screen monitoring service using Terminator"""
        self._connected = False
        if DESKTOP_USE_AVAILABLE:
            try:
                self.client = DesktopUseClient(base_url=base_url)
                self._connected = True
            except Exception as e:
                print(f"Could not connect to Terminator server: {e}")
        self.is_monitoring = False
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to Terminator server"""
        return self._connected and DESKTOP_USE_AVAILABLE
    
    def capture_screen_content(self) -> Dict[str, Any]:
        """Capture current screen content/state"""
        try:
            # Capture the screen
            screenshot = ImageGrab.grab()
            
            # Convert to base64 for transmission
            buffered = BytesIO()
            screenshot.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                "image": img_str,
                "timestamp": time.time(),
                "status": "success"
            }
        except Exception as e:
            return {"error": f"Screenshot failed: {str(e)}"}
    
    def analyze_screen(self, image_data: str = None) -> Dict[str, Any]:
        """Analyze screen content"""
        if not image_data:
            capture = self.capture_screen_content()
            if "error" in capture:
                return capture
            image_data = capture["image"]
            
        return {
            "status": "success",
            "timestamp": time.time(),
            "data": image_data
        }
    
    def _get_active_window(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently active window"""
        if not DESKTOP_USE_AVAILABLE:
            return {"error": "Desktop use functionality not available"}
            
        try:
            active_window = self.client.get_active_window_info()
            if active_window:
                return {
                    "title": active_window.title,
                    "id": active_window.id
                }
            return None
        except Exception as e:
            print(f"Error getting active window: {e}")
            return None
    
    def _extract_text_from_window(self, window_info: Dict[str, Any]) -> str:
        """Extract text content from the specified window"""
        if not DESKTOP_USE_AVAILABLE:
            return ""
            
        try:
            window_locator = Locator(selector_chain=f'window:{window_info["id"]}')
            text_elements = self.client.find_elements(window_locator)
            
            extracted_text = []
            for element in text_elements:
                if isinstance(element, ElementResponse) and element.label:
                    extracted_text.append(element.label)
            
            return "\n".join(extracted_text)
        except Exception as e:
            print(f"Error extracting text from window: {e}")
            return ""
    
    def monitor_math_application(self, app_name: str = "Calculator") -> Dict[str, Any]:
        """Specifically monitor math applications like calculator"""
        if not DESKTOP_USE_AVAILABLE:
            return {"error": "Desktop use functionality not available", "status": "failed"}
            
        if not self._connected:
            return {"error": "Not connected to Terminator server", "status": "failed"}
        
        try:
            # Open the application if it's not already open
            self.client.open_application(app_name)
            time.sleep(1)  # Give time for app to open
            
            # For calculator, we could get the display value
            if app_name.lower() == "calculator":
                calc_window = self.client.locator(f'window:{app_name}')
                display = calc_window.locator('name:CalculatorResults')
                result = display.get_text()
                
                return {
                    "application": app_name,
                    "current_value": result.text if hasattr(result, 'text') else "Unknown",
                    "timestamp": time.time(),
                    "status": "success"
                }
            
            return {"application": app_name, "status": "monitoring"}
            
        except Exception as e:
            return {"error": str(e), "status": "failed"}
    
    def start_monitoring(self):
        self.is_monitoring = True
        return {"status": "success", "message": "Screen monitoring started"}

    def stop_monitoring(self):
        self.is_monitoring = False
        return {"status": "success", "message": "Screen monitoring stopped"}