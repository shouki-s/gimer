"""Constants for the gimer package."""

class System:
    MACOS = "darwin"
    LINUX = "linux"
    WINDOWS = "windows"
    UNKNOWN = "unknown"

# Table styles
TABLE_TITLE = "Mergeable Branches"
COLUMN_NUMBER = "No."
COLUMN_BRANCH = "Branch Name"

# Messages
MSG_CURRENT_BRANCH = "Current branch:"
MSG_WARNING_UNCOMMITTED = "Warning: You have uncommitted changes in your working directory."
MSG_CONTINUE = "Do you want to continue?"
MSG_SELECT_BRANCH = "Select a branch number to merge"
MSG_STARTING_MERGE = "Starting merge:"
MSG_MERGE_SUCCESS = "Merge completed successfully!"
MSG_MERGE_ERROR = "An error occurred during merge:"
MSG_MERGE_CONFLICT = "Merge conflicts detected. Please resolve them manually."
