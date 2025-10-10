def get_wait_time_scenario_name(scenario_key: str) -> str:
    """
    Maps a scenario key to the correct scenario name for the wait time calculator.

    Args:
        scenario_key: The scenario key (e.g., 'peak', 'normal', 'low', 'peak 🔥', 'normal ✅', 'low 📉').

    Returns:
        The corresponding wait time scenario name ('Peak Season', 'Normal Operations', 'Low Season').
    """
    # Normalize by removing emojis and stripping whitespace
    normalized_key = scenario_key.split(' ')[0].strip().lower()
    
    mapping = {
        'peak': 'Peak Season',
        'normal': 'Normal Operations',
        'low': 'Low Season',
    }
    return mapping.get(normalized_key, 'Normal Operations')  # Default to 'Normal Operations' if no match