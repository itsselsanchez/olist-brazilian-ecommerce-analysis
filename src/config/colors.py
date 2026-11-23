
# -----------------------------------------------------------
# Raw hex & rgb color definitions
# -----------------------------------------------------------

# Olist brand colors
NAVY   = "#1A1F5E"
TEAL   = "#2EC4A0"
SKY    = "#4BBFE0"

# Other colors
CYAN    = "#51c9fe"
MAGENTA = "#CB5BFF"
PURPLE  = "#9A4EAA"
CORAL   = "#F4845F"
YELLOW  = "#FFD166"
MAROON  = "#7F1B21"

# Neutrals
NEAR_BLACK       = "#010101"
MIDNIGHT_BLUE    = "#010D15"
ULTRA_DARK_BLUE  = "#040D16"
DARK_BLUE        = "#162129"
DEEP_SLATE       = "#3A4A5C"
MEDIUM_SLATE     = "#49525B"
BLUE_GRAY        = "#56657A"
SLATE            = "#8B9BAE"
NOBEL            = "#A1A0A0"
LIGHT_GRAY       = "#D2D7DE"
OFF_WHITE        = "#F7F8FA"
WHITE            = "#FFFFFF"

TRANSPARENT = "rgba(0, 0, 0, 0)"

# -----------------------------------------------------------
# Semantic roles 
# -----------------------------------------------------------

# Surfaces
BACKGROUND  = MIDNIGHT_BLUE     # paper, plot, map bg, ocean
LAND        = DEEP_SLATE        # Brazil fill
LAND_MUTED  = ULTRA_DARK_BLUE   # surrounding countries fill

# Lines & borders
BORDER      = MEDIUM_SLATE    # country outlines
GRIDLINE    = SLATE           # chart gridlines + internal state/muni borders
OUTLINE     = NOBEL           # bright Brazil edge
FLOW_LINE   = SKY             # connection-map arcs

# Text
LABEL       = SLATE           # axis text, map labels
TITLE       = WHITE           # chart / map titles

# Single series color
SINGLE_SERIES   = SKY                          

# Sequential palette
SEQ_TEAL = [
    [0.0, BACKGROUND], 
    [1.0, TEAL]
]
# Diverging palette
DIV_CORAL_TEAL = [
    [0.0, CORAL], 
    [0.5, BACKGROUND], 
    [1.0, TEAL]
]
# General categorical palette
CATEGORY_PALETTE = [
    SKY, 
    TEAL, 
    CORAL, 
    YELLOW, 
    NAVY, 
    MAROON
]

# Keyed categorical palettes
# on-time vs late deliveries
PALETTE_ON_TIME = {
    True: TEAL, 
    False: CORAL
}
# seller type
PALETTE_SELLER_TYPE = {
    "specialist": SKY, 
    "generalist": TEAL
}
# review ratings (1-5 stars)
PALETTE_REVIEW = {
    1: CORAL, 
    2: YELLOW, 
    3: TEAL, 
    4: SKY, 
    5: NAVY
}

# Plotly geographic density scales
CUSTOMER_DENSITY_SCALE = "Tealgrn"
SELLER_DENSITY_SCALE   = "Redor"

# Bivariate anchors
BIVARIATE_LOW    = DARK_BLUE  
BIVARIATE_X_HIGH = PURPLE   
BIVARIATE_Y_HIGH = NEAR_BLACK   

# Table Styling
# Background fills
TABLE_BACKGROUND        = TRANSPARENT
TABLE_HEADER_BACKGROUND = BLUE_GRAY
TABLE_TITLE_BACKGROUND  = DEEP_SLATE

# Alternating row fills 
ROW_LIGHT               = WHITE
ROW_DARK                = OFF_WHITE

TABLE_BORDER_COLOR      = LIGHT_GRAY

# Table font colors
TABLE_TITLE_FONT_COLOR  = WHITE
TABLE_CODE_FONT_COLOR   = MEDIUM_SLATE
TABLE_HEADER_FONT_COLOR = WHITE
TABLE_LABEL_FONT_COLOR  = DARK_BLUE
TABLE_VALUE_FONT_COLOR  = MEDIUM_SLATE