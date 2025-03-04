import sys
import signal
import importlib

from src.ui.splash import show_splash_screen

def setup_signal_handlers():
    """Setup signal handlers for graceful exit"""
    def signal_handler(sig, frame):
        print("\nExiting t3rm1n4l music player. Goodbye!")
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def load_modules():
    """Dynamically load and initialize modules"""
    modules = [
        'src.player.player',
        'src.library.library_manager',
        'src.ui.components',
        'src.ui.app'
    ]
    
    loaded_modules = {}
    for module_name in modules:
        try:
            loaded_modules[module_name] = importlib.import_module(module_name)
        except ImportError as e:
            print(f"Error loading module {module_name}: {e}")
            return None
    
    return loaded_modules

def main():
    """Main entry point for the application"""
    setup_signal_handlers()
    
    try:
        # Show splash screen
        show_splash_screen(3) 
        
        # Dynamically load modules during splash screen
        modules = load_modules()
        if not modules:
            print("Failed to load required modules. Exiting...")
            return 1
        
        # Import the TerminalApp class after showing the splash screen
        from src.ui.app import TerminalApp
        
        # Run the application
        app = TerminalApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\nExiting t3rm1n4l music player. Goodbye!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
