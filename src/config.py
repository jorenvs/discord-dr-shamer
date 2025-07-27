import pytz

class Config:
    def __init__(self):
        # Configuration - Wish time (24-hour format HH:MM)
        self.WISH_TIME = "11:11"
        
        # Configuration - Shame time (24-hour format HH:MM)
        self.SHAME_TIME = "22:22"
        
        # Configuration - Buffer time in seconds (added to 60s wish minute)
        self.WISH_BUFFER_TIME = 15
        
        # Configuration - Time to wait before sending wish summary (in seconds)
        self.WISH_SUMMARY_DELAY = 180  # 3 minutes

# Create a global config instance
config = Config()

# Create timezone object once to avoid repeated file system operations
LONDON_TZ = pytz.timezone('Europe/London')

# Configuration - Map server IDs to role IDs
SHAME_ROLE_CONFIG = {
    168316445569056768: 1390320164024881192,  # London server: dunce role
    1390289538613772400: 1390319545243402370, # JJ's test server
    1343509963812769832: 1390424931388362874, # The Post Office
    # Add more servers as needed
}

# Configuration - Map server IDs to dev channel names
DEV_CHANNEL_CONFIG = {
    168316445569056768: "pkl-dev",        # London server
    1390289538613772400: "dr-shamer-dev",  # JJ's test server
    1343509963812769832: "dr-shamer-dev",  # The Post Office
    # Add more servers as needed
}

# Configuration - Debug mode per server (True = show debug messages)
DEBUG_MODE_CONFIG = {
    168316445569056768: False,  # London server - no debug
    1390289538613772400: True,  # JJ's test server - debug on
    1343509963812769832: True,  # The Post Office - debug on
    # Add more servers as needed - default to True for new servers
}

# Configuration - Shame summary enable/disable per server
SHAME_SUMMARY_CONFIG = {
    168316445569056768: False,  # London server - disabled by default
    1390289538613772400: True,  # JJ's test server - enabled
    1343509963812769832: True,  # The Post Office - enabled
    # Add more servers as needed - default to True for new servers
} 