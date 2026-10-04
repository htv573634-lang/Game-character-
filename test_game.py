# test_game.py
import yaml
import os
import sys
import trimesh

CONFIG_FILE = "test_game_character.yml"

def load_config(path=CONFIG_FILE):
    print("Current working directory:", os.getcwd())
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

    # Step 1: Check inputs
    print(f"[1/3] Checking input assets...")
    print(f"      Body FBX : {char['input_fbx']}")
    print(f"      Clothing : {char['clothing_obj']}")
    if not os.path.exists(char['input_fbx']):
        print(f"      [!] Warning: {char['input_fbx']} not found. (Expected in a real setup)")
    if not os.path.exists(char['clothing_obj']):
        print(f"      [!] Warning: {char['clothing_obj']} not found. (Expected in a real setup)")

    # Step 2: Generate Placeholder Mesh (Instead of Blender)
    print(f"\n[2/3] Generating placeholder mesh using Python (No Blender)...")
    print(f"      Applying Shrinkwrap Modifier (Offset: {settings['shrinkwrap_offset']}m)")
    print(f"      Transferring Skin Weights: {settings['transfer_weights']}")
    
    # Create a simple box scaled to the character's dimensions (height, shoulders, waist)
    # Convert cm to meters for 3D space
    height_m = body["height_cm"] / 100.0
    width_m = body["shoulders_cm"] / 100.0
    depth_m = body["waist_cm"] / 100.0
    
    # Create a placeholder humanoid shape (a simple capsule or box)
    # We use a box for simplicity, scaled to the character's proportions
    placeholder_mesh = trimesh.creation.box(extents=[width_m, depth_m, height_m])
    print(f"      Created placeholder mesh: {width_m}m x {depth_m}m x {height_m}m")

    # Step 3: Export as GLB
    print(f"\n[3/3] Exporting final model to GLB...")
    os.makedirs(os.path.dirname(char['output_glb']), exist_ok=True)
    
    # Export the mesh to GLB format
    placeholder_mesh.export(char['output_glb'], file_type='glb')
    print(f"      Saved GLB to: {char['output_glb']}")

    print("\n" + "=" * 50)
    print("Pipeline test completed successfully!")
    print("A placeholder .glb file has been generated without Blender.")
    print("=" * 50)

if __name__ == "__main__":
    config = load_config()
    run_pipeline(config)
