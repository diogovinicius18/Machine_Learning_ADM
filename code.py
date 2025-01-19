import bpy
import os

'''
bl_info = {
    "name": "Aplicar_MT",
    "blender": (3, 0, 0),
    "category": "Object",
}


class OBJECT_OT_ExecutarScript(bpy.types.Operator):
    bl_idname = "object.executar_script"
    bl_label = "Executar Script"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # Coloque o código que deseja executar aqui
        #aplicar_MT()
        pegando_dir()


        return {'FINISHED'}

class VIEW3D_PT_ExecutarScriptPanel(bpy.types.Panel):
    bl_label = "Aplicar_MT"
    bl_idname = "VIEW3D_PT_Aplicar_MT"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Aplicar_MT"  # Defina a categoria desejada

    def draw(self, context):
        layout = self.layout
        layout.operator("object.executar_script")

def register():
    bpy.utils.register_class(OBJECT_OT_ExecutarScript)
    bpy.utils.register_class(VIEW3D_PT_ExecutarScriptPanel)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_ExecutarScript)
    bpy.utils.unregister_class(VIEW3D_PT_ExecutarScriptPanel)

if __name__ == "__main__":
    register()

'''

def pegando_dir():
    
    blend_file_path = bpy.data.filepath
    script_dir = os.path.dirname(blend_file_path)
    print(f"Diretório do script: {script_dir}")

    # Caminho completo para o arquivo .blend
    file_path = os.path.join(script_dir, "library", "DECALS_PRO.blend")
    print(f"Caminho do arquivo .blend: {file_path}")

    # Verifique se o arquivo existe
    if not os.path.exists(file_path):
        print(f"Erro: O arquivo '{file_path}' não existe.")
        return
    

    # Nome do nó que deseja importar
    nome_node = "NODE_PUDDLES"

    # Carregando o arquivo de origem
    with bpy.data.libraries.load(file_path) as (data_from, data_to):
        data_to.materials = [nome_node] 
        
        
    # Verificando se o nó foi carregado com sucesso
    if nome_node in bpy.data.materials:
        # Acessando o nó importado
        no_importado = bpy.data.materials[nome_node]

        print(f"Nó '{no_importado}' importado com sucesso.")
        aplicar_MT()
    else:
        print(f"Nó '{nome_node}' não foi encontrado no arquivo de origem.")

def aplicar_MT():


    albedo_palavras = {"albedo", "color", "diff"}
    roughness_palavras = {"rough", "gloss", "roughness"}
    normal_palavras = {"normal", "nrm"}
    ao_palavras = {"ao", "ambient", "occlusion", "ambient", "occlusion"}
    disp_palavras = {"disp", "heigth"}
    opacity_palavras = {"opacity", "alpha"}
     
    objetos = bpy.context.selected_objects

    for objeto in objetos:
        if objeto:
            if objeto.active_material:
                material = objeto.active_material
            else:
                material = bpy.data.materials.new(name="New_Material")
                objeto.active_material = material

            material.use_nodes = True

            tex_images = []

            # Identifique as texturas no material e adicione à lista
            for node in material.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    tex_images.append(node)

            # Limpe todos os nós do material, exceto as texturas
            for node in material.node_tree.nodes:
               # if node.type != "TEX_IMAGE":
                material.node_tree.nodes.remove(node)
                

            # Obtenha o nó "Material Output" do material
            material_output = material.node_tree.nodes.new(type="ShaderNodeOutputMaterial")
            material_output.location = (0, 0)

            # Crie uma nova instância do grupo de nós personalizados
            node_puddels = material.node_tree.nodes.new(type="ShaderNodeGroup")
            node_puddels.location = (-200, 0)

            # Defina o nome do grupo (deve corresponder ao nome real do grupo)
            node_puddels.node_tree = bpy.data.node_groups["NODE_PUDDELS"]       
                
            node_textures = material.node_tree.nodes.new(type="ShaderNodeGroup")
            node_textures.location = (-400, 0)

            # Defina o nome do grupo (deve corresponder ao nome real do grupo)
            node_textures.node_tree = bpy.data.node_groups["TEXTURES"]
            
            
            for node in node_textures.node_tree.nodes:
                if node.type == "TEX_IMAGE":
                    node_textures.node_tree.nodes.remove(node)
            
            
            if len(tex_images) > 0:
                for textura in tex_images:
                    new_node = node_textures.node_tree.nodes.new(type='ShaderNodeTexImage')
                    new_node.image = textura.image
                
                
            dn_albedo = 0
            t_ao = 0

            node_output = None
            node_math = None

            for no in node_textures.node_tree.nodes:
                if no.type == "GROUP_OUTPUT":
                    node_output = no
                elif no.type == "GROUP_INPUT":
                    print("q")
                elif no.type == "TEX_IMAGE":
                    print("a")
                else:
                    node_math = no

                
            print(node_math)
            print(node_output)

            for node in node_textures.node_tree.nodes:
                if node.type == "TEX_IMAGE":                    
                    if any(palavra in node.image.filepath.lower() for palavra in albedo_palavras):
                        node_textures.node_tree.links.new(node.outputs["Color"], node_output.inputs["ALBEDO"])
                        node_textures.node_tree.links.new(node_math.outputs["Vector"], node.inputs["Vector"])
                        node.location = (-300, dn_albedo + 300)

                    if any(palavra in node.image.filepath.lower() for palavra in ao_palavras):
                        node_textures.node_tree.links.new(node.outputs["Color"], node_output.inputs["AO"])
                        node_textures.node_tree.links.new(node_math.outputs["Vector"], node.inputs["Vector"])
                        node.location = (-300, dn_albedo)

                    if any(palavra in node.image.filepath.lower() for palavra in roughness_palavras):
                        if "rough" in node.image.filepath.lower():
                            node_textures.node_tree.links.new(node.outputs["Color"], node_output.inputs["ROUGHNESS"])
                            node_textures.node_tree.links.new(node_math.outputs["Vector"], node.inputs["Vector"])
                            node.location = (-300, dn_albedo - 300)

                        elif "gloss" in node.image.filepath.lower():
                            invert_node = material.node_tree.nodes.new(type="ShaderNodeInvert")
                            invert_node.location = (-150, dn_albedo - 300)
                            node_textures.node_tree.links.new(node.outputs["Color"], invert_node.inputs["Color"])
                            node_textures.node_tree.links.new(invert_node.outputs["Color"], node_output.inputs["ROUGHNESS"])
                            node_textures.node_tree.links.new(node_math.outputs["Vector"], node.inputs["Vector"])
                            node.location = (-300, dn_albedo - 300)

                    if any(palavra in node.image.filepath.lower() for palavra in normal_palavras):
                        node_textures.node_tree.links.new(node.outputs["Color"], node_output.inputs["NORMAL"])
                        node_textures.node_tree.links.new(node_math.outputs["Vector"], node.inputs["Vector"])
                        node.location = (-300, dn_albedo - 600)

                    if any(palavra in node.image.filepath.lower() for palavra in disp_palavras):
                        node_textures.node_tree.links.new(node.outputs["Color"], node_output.inputs["DISPLACEMENT"])
                        node_textures.node_tree.links.new(node_math.outputs["Vector"], node.inputs["Vector"])
                        node.location = (-300, dn_albedo - 900)

                    if any(palavra in node.image.filepath.lower() for palavra in opacity_palavras):
                        node_textures.node_tree.links.new(node.outputs["Color"], node_output.inputs["OPACITY"])
                        node_textures.node_tree.links.new(node_math.outputs["Vector"], node.inputs["Vector"])
                        node.location = (-300, dn_albedo - 1200)


                    material.node_tree.links.new(node_puddels.outputs["ALBEDO"], material_output.inputs["Surface"])
                    material.node_tree.links.new(node_puddels.outputs["DISPLACEMENT"], material_output.inputs["Displacement"])

                    material.node_tree.links.new(node_textures.outputs["ALBEDO"], node_puddels.inputs["ALBEDO"])
                    material.node_tree.links.new(node_textures.outputs["AO"], node_puddels.inputs["AO"])
                    material.node_tree.links.new(node_textures.outputs["ROUGHNESS"], node_puddels.inputs["ROUGHNESS"])
                    material.node_tree.links.new(node_textures.outputs["NORMAL"], node_puddels.inputs["NORMAL"])
                    material.node_tree.links.new(node_textures.outputs["DISPLACEMENT"], node_puddels.inputs["DISPLACEMENT"])
                    material.node_tree.links.new(node_textures.outputs["OPACITY"], node_puddels.inputs["OPACITY"])
                    
                    



            if objeto.type == "MESH":
                if len(objeto.data.materials) == 0:
                    objeto.data.materials.append(material)
                else:
                    objeto.data.materials[0] = material

pegando_dir()
