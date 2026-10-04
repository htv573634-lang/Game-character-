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
    print(f"      Body Model : {char['input_obj']}")
    if 'clothing_obj' in char:
        print(f"      Clothing   : {char['clothing_obj']}")
    else:
        print(f"      Clothing   : (None provided)")

    # Step 2: Load or Generate Mesh
    print(f"\n[2/3] Processing 3D Model...")

    if os.path.exists(char['input_obj']):
        print(f"      Found real character model! Loading...")
        try:
            character_mesh = trimesh.load(char['input_obj'], force='scene')
            
            # Check for clothing
            if 'clothing_obj' in char and os.path.exists(char['clothing_obj']):
                print(f"      Found clothing model! Loading and combining...")
                clothing_mesh = trimesh.load(char['clothing_obj'], force='scene')
                final_scene = trimesh.Scene([character_mesh, clothing_mesh])
            else:
                print(f"      [!] No clothing model found. Exporting character only.")
                final_scene = character_mesh
                
        except Exception as e:
            print(f"      [!] Error loading model: {e}")
            print(f"      Falling back to placeholder box...")
            height_m = body["height_cm"] / 100.0
            width_m = body["shoulders_cm"] / 100.0
            depth_m = body["waist_cm"] / 100.0
            placeholder_mesh = trimesh.creation.box(extents=[width_m, depth_m, height_m])
            final_scene = trimesh.Scene([placeholder_mesh])
            
    else:
        print(f"      [!] Real character model not found at '{char['input_obj']}'.")
        print(f"      Creating placeholder box instead...")
        height_m = body["height_cm"] / 100.0
        width_m = body["shoulders_cm"] / 100.0
        depth_m = body["waist_cm"] / 100.0
        placeholder_mesh = trimesh.creation.box(extents=[width_m, depth_m, height_m])
        final_scene = trimesh.Scene([placeholder_mesh])
        print(f"      Created placeholder mesh: {width_m}m x {depth_m}m x {height_m}m")

    # Step 3: Export as GLB
    print(f"\n[3/3] Exporting final model to GLB...")
    os.makedirs(os.path.dirname(char['output_glb']), exist_ok=True)

    final_scene.export(char['output_glb'], file_type='glb')
    print(f"      Saved GLB to: {char['output_glb']}")

    print("\n" + "=" * 50)
    print("Pipeline test completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    config = load_config()
    run_pipeline(config)
