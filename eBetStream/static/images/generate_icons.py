from PIL import Image
import os

def generate_icons():
    # Chemin du logo source
    logo_path = os.path.join('Logo.png')
    
    # Tailles requises pour les icônes
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    try:
        # Ouvrir l'image source
        with Image.open(logo_path) as img:
            # Créer un fond blanc carré
            for size in sizes:
                # Créer une nouvelle image carrée blanche
                new_img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
                
                # Redimensionner le logo pour tenir dans le carré
                img.thumbnail((size, size))
                
                # Centrer le logo sur le fond
                x = (size - img.size[0]) // 2
                y = (size - img.size[1]) // 2
                new_img.paste(img, (x, y), img.convert('RGBA'))
                
                # Sauvegarder l'icône
                output_path = f'icon-{size}x{size}.png'
                new_img.save(output_path, 'PNG')
                print(f'Créé : {output_path}')
                
    except Exception as e:
        print(f'Erreur lors de la génération des icônes : {e}')

if __name__ == '__main__':
    generate_icons()
