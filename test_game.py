# test_game.py
import yaml
import os
import sys
import trimesh

CONFIG_FILE = "test_game_character.yml"

def load_config(path=CONFIG_FILE):
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        sys.exit(1)
    with open(path, "r") as f:
        return yaml.safe_load(f)

def inspect_downloaded_files(path):
    """Recursively lists all files in the input directory."""
    print(f"\n--- 📁 INSPECTING DIRECTORY: '{path}' ---")
    if not os.path.exists(path):
        print(f"      Directory '{path}' does not exist!")
        return
    for root, dirs, files in os.walk(path):
        for name in files:
            filepath = os.path.join(root, name)
            size_kb = os.path.getsize(filepath) / 1024
            print(f"      {filepath} ({size_kb:.2f} KB)")
    print("-------------------------------------------\n")

def inspect_3d_model(mesh_path):
    """Loads the model and prints detailed structural and material info."""
    print(f"--- 🔍 INSPECTING 3D MODEL: '{mesh_path}' ---")
    try:
        scene = trimesh.load(mesh_path, force='scene')
        
        print(f"Total Geometries (Meshes): {len(scene.geometry)}")
        print(f"Total Scene Nodes: {len(scene.graph.nodes)}")
        
        for i, (name, geom) in enumerate(scene.geometry.items()):
            print(f"\n  [Mesh {i+1}] Name: {name}")
            print(f"    Vertices: {len(geom.vertices)}")
            print(f"    Faces: {len(geom.faces)}")
            
            # Check Materials
            if hasattr(geom.visual, 'material') and geom.visual.material is not None:
                mat = geom.visual.material
                print(f"    Material Type: {type(mat).__name__}")
                
                # Check for textures
                has_texture = False
                if hasattr(mat, 'baseColorTexture') and mat.baseColorTexture is not None:
                    print(f"    ✅ Base Color Texture: FOUND")
                    has_texture = True
                if hasattr(mat, 'image') and mat.image is not None:
                    print(f"    ✅ Image Data: FOUND")
                    has_texture = True
                
                if not has_texture:
                    print(f"    ❌ Base Color Texture: MISSING (This causes black rendering!)")
                    print(f"    Material Base Color Factor: {getattr(mat, 'baseColorFactor', 'N/A')}")
            else:
                print(f"    ❌ Material: NONE (Defaulting to black)")
                
            # Check for rigging/skinning
            if hasattr(geom, 'vertex_definitions') and geom.vertex_definitions is not None:
                print(f"    ✅ Rigging/Skinning Data: FOUND")
            else:
                print(f"    ⚠️ Rigging/Skinning Data: NOT DETECTED by trimesh")
                
    except Exception as e:
        print(f"    Error inspecting model: {e}")
    print("-------------------------------------------\n")

def run_pipeline(config):
    char = config["pipeline"]
    body = config["body_dimensions"]

    print("=" * 50)
    print(" GAME CHARACTER PIPELINE - TEST RUN ")
    print("=" * 50)
    print(f"Character  : {char['character_name']}")
    print(f"Game       : {char['game']}")
    print("-" * 50)

    # Step 1: Inspect downloaded files
    inspect_downloaded_files("input/")
    if not os.path.exists(char['input_obj']):
        print(f"❌ Error: The file '{char['input_obj']}' was NOT found in the input folder.")
        print("Check the directory inspection above to see exactly what was downloaded.")
        sys.exit(1)

    # Step 2: Inspect the 3D model itself
    inspect_3d_model(char['input_obj'])

    # Step 3: Process and Export
    print(f"[3/3] Exporting final model to GLB...")
    try:
        final_scene = trimesh.load(char['input_obj'], force='scene')
        os.makedirs(os.path.dirname(char['output_glb']), exist_ok=True)
        final_scene.export(char['output_glb'], file_type='glb')
        print(f"      Saved GLB to: {char['output_glb']}")
        print("\n💡 NOTE: If the log says 'Base Color Texture: MISSING', the black model is due to broken texture links.")
        print("   We will need to update the script to pack the textures manually.")
    except Exception as e:
        print(f"❌ Export failed: {e}")

    print("\n" + "=" * 50)
    print("Pipeline test completed!")
    print("=" * 50)

if __name__ == "__main__":
    config = load_config()
    run_pipeline(config)
