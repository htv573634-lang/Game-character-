# test_game.py
import yaml
import os
import sys
import trimesh
import struct
import json

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
    """Manually packs external textures and binary buffers into a single GLB file."""
    print(f"\n[3/3] Packing GLTF to GLB with textures...")
    try:
        with open(gltf_path, 'r') as f:
            gltf = json.load(f)
        
        # 1. Read the .bin file
        bin_data = b''
        if 'buffers' in gltf and len(gltf['buffers']) > 0:
            buffer = gltf['buffers'][0]
            if 'uri' in buffer:
                bin_path = os.path.join(os.path.dirname(gltf_path), buffer['uri'])
                if os.path.exists(bin_path):
                    with open(bin_path, 'rb') as f:
                        bin_data = f.read()
                    del buffer['uri']
                    print(f"      ✅ Embedded binary buffer")
        
        # 2. Read and embed the .png textures
        if 'images' in gltf:
            for i, img in enumerate(gltf['images']):
                if 'uri' in img:
                    img_path = os.path.join(os.path.dirname(gltf_path), img['uri'])
                    if os.path.exists(img_path):
                        with open(img_path, 'rb') as f:
                            img_data = f.read()
                        
                        # Add image data to the binary buffer
                        img['bufferView'] = len(gltf.get('bufferViews', []))
                        if 'bufferViews' not in gltf:
                            gltf['bufferViews'] = []
                        gltf['bufferViews'].append({
                            'buffer': 0,
                            'byteOffset': len(bin_data),
                            'byteLength': len(img_data)
                        })
                        bin_data += img_data
                        
                        # Set the mimeType
                        if 'mimeType' not in img:
                            if img_path.endswith('.png'):
                                img['mimeType'] = 'image/png'
                            elif img_path.endswith('.jpg') or img_path.endswith('.jpeg'):
                                img['mimeType'] = 'image/jpeg'
                        
                        del img['uri']
                        print(f"      ✅ Embedded image {i+1}: {os.path.basename(img_path)}")
        
        # 3. Update the total buffer length
        if 'buffers' in gltf and len(gltf['buffers']) > 0:
            gltf['buffers'][0]['byteLength'] = len(bin_data)
        
        # 4. Create the JSON chunk
        json_str = json.dumps(gltf, separators=(',', ':'))
        json_chunk = json_str.encode('utf-8')
        while len(json_chunk) % 4 != 0:
            json_chunk += b' '
        
        # 5. Create the BIN chunk
        bin_chunk = bin_data
        while len(bin_chunk) % 4 != 0:
            bin_chunk += b'\x00'
        
        # 6. Write the final GLB file
        total_length = 12 + 8 + len(json_chunk) + 8 + len(bin_chunk)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            # Header
            f.write(struct.pack('<III', 0x46546C67, 2, total_length))
            # JSON Chunk
            f.write(struct.pack('<II', len(json_chunk), 0x4E4F534A))
            f.write(json_chunk)
            # BIN Chunk
            f.write(struct.pack('<II', len(bin_chunk), 0x004E4942))
            f.write(bin_chunk)
        
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

    # Step 2: Inspect the 3D model
    inspect_3d_model(char['input_obj'])

    # Step 3: Pack and Export
    pack_gltf_to_glb(char['input_obj'], char['output_glb'])

    print("\n" + "=" * 50)
    print("Pipeline test completed!")
    print("=" * 50)

if __name__ == "__main__":
    config = load_config()
    run_pipeline(config)
