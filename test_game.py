# test_game.py
import yaml
import os
import sys

CONFIG_FILE = "test_game_character.yml"

def load_config(path=CONFIG_FILE):
    if not os.path.exists(path):
        print(f"Error: {path} not found. Please create it first.")
        sys.exit(1)
    with open(path, "r") as f:
        return yaml.safe_load(f)

def run_pipeline(config):
    char = config["pipeline"]
    body = config["body_dimensions"]
    settings = config["blender_settings"]

    print("=" * 50)
    print(" GAME CHARACTER PIPELINE - TEST RUN ")
    print("=" * 50)
    print(f"Character  : {char['character_name']}")
    print(f"Game       : {char['game']}")
    print(f"Dimensions : Height {body['height_cm']}cm | Waist {body['waist_cm']}cm | Hips {body['hips_cm']}cm")
    print("-" * 50)

    print(f"[1/3] Checking input assets...")
    print(f"      Body FBX : {char['input_fbx']}")
    print(f"      Clothing : {char['clothing_obj']}")
    if not os.path.exists(char['input_fbx']):
        print(f"      [!] Warning: {char['input_fbx']} not found. (Expected in a real setup)")
    if not os.path.exists(char['clothing_obj']):
        print(f"      [!] Warning: {char['clothing_obj']} not found. (Expected in a real setup)")

    print(f"\n[2/3] Simulating Blender processing...")
    print(f"      Applying Shrinkwrap Modifier (Offset: {settings['shrinkwrap_offset']}m)")
    print(f"      Transferring Skin Weights: {settings['transfer_weights']}")
    print(f"      Binding Clothing to Armature...")

    print(f"\n[3/3] Exporting final model...")
    os.makedirs(os.path.dirname(char['output_glb']), exist_ok=True)
    print(f"      Saving to: {char['output_glb']}")

    print("\n" + "=" * 50)
    print("Pipeline test completed successfully!")
    print("Next step: Install Blender & extraction tools to run the real mesh processing.")
    print("=" * 50)

if __name__ == "__main__":
    config = load_config()
    run_pipeline(config)
