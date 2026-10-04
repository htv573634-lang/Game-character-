# test_game.py
import yaml
import os
import sys
import trimesh
import pygltflib

CONFIG_FILE = "test_game_character.yml"

def load_config(path=CONFIG_FILE):
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        sys.exit(1)
    with open(path, "r") as f:
        return yaml.safe_load(f)

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
            
            if hasattr(geom.visual, 'material') and geom.visual.material is not None:
                mat = geom.visual.material
                print(f"    Material Type: {type(mat).__name__}")
                has_texture = False
                if hasattr(mat, 'baseColorTexture') and mat.baseColorTexture is not None:
                    print(f"    ✅ Base Color Texture: FOUND")
                    has_texture = True
                if not has_texture:
                    print(f"    ❌ Base Color Texture: MISSING (This causes black rendering!)")
            else:
                print(f"    ❌ Material: NONE (Defaulting to black)")
    except Exception as e:
        print(f"    Error inspecting model: {e}")
    print("-------------------------------------------\n")

def pack_gltf_to_glb(gltf_path, output_path):
    """Packs external textures and binary buffers into a single GLB file."""
    print(f"\n[3/3] Packing GLTF to GLB with textures...")
    try:
        gltf = pygltflib.GLTF2().load(gltf_path)
        
        # 1. Pack binary buffer (.bin)
        if gltf.buffers and gltf.buffers[0].uri:
            buffer_path = os.path.join(os.path.dirname(gltf_path), gltf.buffers[0].uri)
            if os.path.exists(buffer_path):
                with open(buffer_path, 'rb') as f:
                    gltf.buffers[0].data = f.read()
                gltf.buffers[0].uri = None
                print("      ✅ Embedded binary buffer (.bin)")
            else:
                print(f"      [!] Warning: Buffer file not found: {buffer_path}")

        # 2. Pack external images (.png)
        if gltf.images:
            for i, img in enumerate(gltf.images):
                if img.uri:
                    img_path = os.path.join(os.path.dirname(gltf_path), img.uri)
                    if os.path.exists(img_path):
                        with open(img_path, 'rb') as f:
                            img.data = f.read()
                        img.uri = None
                        print(f"      ✅ Embedded image {i+1}: {img.uri}")
                    else:
                        print(f"      [!] Warning: Image file not found: {img_path}")

        # 3. Save as GLB
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        gltf.save_binary(output_path)
        print(f"      ✅ Saved packed GLB to: {output_path}")
        
    except Exception as e:
        print(f"      ❌ Error packing GLTF: {e}")
        import traceback
        traceback.print_exc()

def run_pipeline(config):
    char = config["pipeline"]
    
    print("=" * 50)
    print(" GAME CHARACTER PIPELINE - TEST RUN ")
    print("=" * 50)
    print(f"Character  : {char['character_name']}")
    print(f"Game       : {char['game']}")
    print("-" * 50)

    # Step 1: Inspect downloaded files
    if not os.path.exists(char['input_obj']):
        print(f"❌ Error: The file '{char['input_obj']}' was NOT found.")
        sys.exit(1)

    # Step 2: Inspect the 3D model itself
    inspect_3d_model(char['input_obj'])

    # Step 3: Pack and Export
    pack_gltf_to_glb(char['input_obj'], char['output_glb'])

    print("\n" + "=" * 50)
    print("Pipeline test completed!")
    print("=" * 50)

if __name__ == "__main__":
    config = load_config()
    run_pipeline(config)
