import os
import datetime
import logging
from pathlib import Path
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)
import llm_chess
from run_multiple_games import run_games
from dotenv import load_dotenv
from utils import get_llms_autogen
current_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")

## CONFIGS

NUM_REPETITIONS = 10
LOG_FOLDER = f"_logs/new/claude_37_2025-30/{current_date}"
END_DATE = datetime.datetime(2025, 4, 25, 00, 00) # Set end date for experiment
llm_chess.throttle_delay = 1
llm_chess.dialog_turn_delay = 1
llm_chess.white_player_type = llm_chess.PlayerType.RANDOM_PLAYER
llm_chess.black_player_type = llm_chess.PlayerType.LLM_BLACK
llm_chess.board_representation_mode = llm_chess.BoardRepresentation.UNICODE_ONLY
llm_chess.temp_override = None
llm_chess.reasoning_effort = None 
llm_chess.remove_text = None

def main():
    global NUM_REPETITIONS
    current_file = os.path.basename(__file__)
    file_name = current_file.replace('.py', '')
    env_file = current_file.replace('.py', '.env')

    os.makedirs(LOG_FOLDER, exist_ok=True)

    # Configure a module-specific logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # Add file handler specifically for this module
    file_handler = logging.FileHandler(os.path.join(LOG_FOLDER, 'execution.log'))
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    # Prevent propagation to root logger to avoid capturing other modules' logs
    logger.propagate = False
    
    logger.info(f"Starting chess experiment with {file_name}")
    logger.info(f"Running {NUM_REPETITIONS} games")

    # Get absolute path to the env file in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, env_file)
    
    # Check if the env file exists
    if not os.path.exists(env_path):
        logger.error(f"Environment file not found: {env_path}")
        logger.error("Cannot continue without environment file. Exiting.")
        return
    
    logger.info(f"Using environment file: {env_path}")

    load_dotenv(dotenv_path=env_path, override=True)
    
    _, black_config = get_llms_autogen()
    logger.info(f"Black player model: {black_config["config_list"][0]["model"]}")
    logger.info(f"Logs will be saved to: {LOG_FOLDER}")

    # Check if experiment end date has passed
    current_date = datetime.datetime.now()
    if current_date > END_DATE:
        logger.info(f"Experiment end date ({END_DATE.strftime('%Y-%m-%d')}) has passed. Stopping execution.")
        return

    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run chess games with Claude 3.7')
    parser.add_argument('-n', '--num-games', type=int, help='Number of games to run')
    args = parser.parse_args()
    
    # Override NUM_REPETITIONS if -n argument is provided
    if args.num_games is not None:
        NUM_REPETITIONS = args.num_games
        logger.info(f"Number of games set to {NUM_REPETITIONS} from command line argument")
    
    # Run the games with our configuration
    run_games(NUM_REPETITIONS, LOG_FOLDER)
    
    logger.info(f"Experiment completed. Results saved to {LOG_FOLDER}")

if __name__ == "__main__":
    main() 