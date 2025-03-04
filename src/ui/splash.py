"""
Splash screen and loading animation
"""
import time
from rich.console import Console
from rich.panel import Panel
from rich.align import Align

# ASCII art for t3rm1n4l logo
T3RM1N4L_ASCII = r"""
                             .-') _    .-') _                                  
                            ( OO ) )  (  OO) )                                 
  ,----.    .-'),-----. ,--./ ,--,' ,(_)----..-'),-----.                       
 '  .-./-')( OO'  .-.  '|   \ |  |\ |       ( OO'  .-.  '                      
 |  |_( O- )   |  | |  ||    \|  | )'--.   //   |  | |  |                      
 |  | .--, \_) |  |\|  ||  .     |/ (_/   / \_) |  |\|  |                      
(|  | '. (_/ \ |  | |  ||  |\    |   /   /___ \ |  | |  |                      
 |  '--'  |   `'  '-'  '|  | \   |  |        | `'  '-'  '                      
  `------'      `-----' `--'  `--'  `--------'   `-----'                       
 _   .-')                  .-')                                                
( '.( OO )_               ( OO ).                                              
 ,--.   ,--.),--. ,--.   (_)---\_) ,-.-')   .-----.                            
 |   `.'   | |  | |  |   /    _ |  |  |OO) '  .--./                            
 |         | |  | | .-') \  :` `.  |  |  \ |  |('-.                            
 |  |'.'|  | |  |_|( OO ) '..`''.) |  |(_//_) |OO  )                           
 |  |   |  | |  | | `-' /.-._)   \,|  |_.'||  |`-'|                            
 |  |   |  |('  '-'(_.-' \       (_|  |  (_'  '--'\                            
 `--'   `--'  `-----'     `-----'  `--'     `-----'                            
 .-') _     ('-.  _  .-')  _   .-')                .-') _    ('-.              
(  OO) )  _(  OO)( \( -O )( '.( OO )_             ( OO ) )  ( OO ).-.          
/     '._(,------.,------. ,--.   ,--.),-.-') ,--./ ,--,'   / . --. /,--.      
|'--...__)|  .---'|   /`. '|   `.'   | |  |OO)|   \ |  |\   | \-.  \ |  |.-')  
'--.  .--'|  |    |  /  | ||         | |  |  \|    \|  | ).-'-'  |  ||  | OO ) 
   |  |  (|  '--. |  |_.' ||  |'.'|  | |  |(_/|  .     |/  \| |_.'  ||  |`-' | 
   |  |   |  .--' |  .  '.'|  |   |  |,|  |_.'|  |\    |    |  .-.  (|  '---.' 
   |  |   |  `---.|  |\  \ |  |   |  (_|  |   |  | \   |    |  | |  ||      |  
   `--'   `------'`--' '--'`--'   `--' `--'   `--'  `--'    `--' `--'`------'  
"""


def loading_animation(console, duration=5):
    """Display a loading animation with the t3rm1n4l logo"""
    start_time = time.time()
    
    # Animation frames for loading
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    frame_index = 0
    
    console.clear()
    
    while time.time() - start_time < duration:
        console.clear()
        
        # Create the loading panel with ASCII art and animation frame
        loading_text = f"{frames[frame_index]} Loading modules..."
        
        panel_content = Align.center(
            T3RM1N4L_ASCII + "\n" + loading_text,
            vertical="middle"
        )
        
        panel = Panel(
            panel_content,
            border_style="green",
            title="t3rm1n4l Music Player",
            subtitle="v0.1.0"
        )
        
        console.print(panel)
        
        # Update animation frame
        frame_index = (frame_index + 1) % len(frames)
        time.sleep(0.1)
    
    console.clear()
    return

def show_splash_screen(duration=5):
    """Show the splash screen for the specified duration"""
    console = Console()
    try:
        # Get terminal size and use it to center the splash screen
        loading_animation(console, duration)
    except Exception as e:
        # Fall back to simple loading message if there's an error
        console.print(f"Loading t3rm1n4l music player...", style="bold green")
        time.sleep(duration)
    
if __name__ == "__main__":
    # Test the splash screen
    show_splash_screen(2)
