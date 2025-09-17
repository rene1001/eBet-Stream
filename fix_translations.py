#!/usr/bin/env python3
"""
Script pour compléter automatiquement toutes les traductions manquantes
"""
import re

# Dictionnaire de traductions françaises vers anglaises
FR_TO_EN = {
    # Navigation et base
    "Jeux": "Games",
    "Paris": "Betting", 
    "Mon Compte": "My Account",
    "Déconnexion": "Logout",
    "Connexion": "Login",
    "Inscription": "Sign Up",
    "Retour à l'accueil": "Back to Home",
    "Retour au blog": "Back to Blog",
    "Retour à la liste des paris": "Back to Bet List",
    "Parier": "Bet",
    "Close": "Close",
    
    # Footer
    "Votre plateforme de paris sportifs en ligne": "Your online esports betting platform",
    "Tous droits réservés.": "All rights reserved.",
    "Confidentialité": "Privacy",
    "Conditions": "Terms",
    "eBetStream Logo": "eBetStream Logo",
    
    # Betting
    "\"Double\" Betting System: Bet on a result and double your bet if you win!": "\"Double\" Betting System: Bet on a result and double your bet if you win!",
    "Odds": "Odds",
    "Potential Winnings": "Potential Winnings",
    "Your Choice": "Your Choice",
    "Match Information": "Match Information",
    "Tournament": "Tournament",
    "Game": "Game",
    "Match Date": "Match Date",
    "Match Status": "Match Status",
    "Final Score": "Final Score",
    "Congratulations! You won": "Congratulations! You won",
    "with this bet.": "with this bet.",
    "Too bad! You lost your bet of": "Too bad! You lost your bet of",
    "Your bet is pending the match result.": "Your bet is pending the match result.",
    "Live Bet Information": "Live Bet Information",
    "Timestamp:": "Timestamp:",
    "Game Time:": "Game Time:",
    "Score at bet time:": "Score at bet time:",
    "Back to my bets": "Back to my bets",
    "Place another live bet": "Place another live bet",
    
    # Bet List
    "Total Bets": "Total Bets",
    "Won Bets": "Won Bets", 
    "Lost Bets": "Lost Bets",
    "Pending Bets": "Pending Bets",
    "Total Bet Amount": "Total Bet Amount",
    "Total Winnings": "Total Winnings",
    "Net Profit": "Net Profit",
    "Date": "Date",
    "Match": "Match",
    "Choice": "Choice",
    "Amount": "Amount",
    "Potential Win": "Potential Win",
    "Status": "Status",
    "You haven't placed any bets yet.": "You haven't placed any bets yet.",
    "Page navigation": "Page navigation",
    "Previous": "Previous",
    "Next": "Next",
    
    # Match List
    "Watch Live": "Watch Live",
    "Aucun match disponible pour le moment.": "No matches available at the moment.",
    
    # P2P Challenges
    "Créer un Défi P2P": "Create P2P Challenge",
    "Créer un Nouveau Défi P2P": "Create New P2P Challenge",
    "Détails du défi": "Challenge Details",
    "Titre du défi": "Challenge Title",
    "Description du défi": "Challenge Description",
    "Type de jeu": "Game Type",
    "Nom du jeu": "Game Name", 
    "Adversaire": "Opponent",
    "Mises et règles": "Stakes and Rules",
    "Votre mise (Ktap)": "Your Stake (Ktap)",
    "Solde disponible:": "Available Balance:",
    "Mise de l'adversaire (Ktap)": "Opponent Stake (Ktap)",
    "Pot total du défi :": "Total Challenge Pot:",
    "Ce montant sera bloqué sur votre compte jusqu'à la fin du défi.": "This amount will be locked on your account until the end of the challenge.",
    "Règles spécifiques (optionnel)": "Specific Rules (optional)",
    "Format du match": "Match Format",
    "Date limite d'acceptation": "Acceptance Deadline",
    "Important :": "Important:",
    "En créant ce défi, vous acceptez que le montant de votre mise soit bloqué sur votre compte jusqu'à la fin du défi. En cas de non-respect des règles, l'équipe de modération se réserve le droit d'annuler le défi.": "By creating this challenge, you agree that your stake amount will be locked on your account until the end of the challenge. In case of rule violations, the moderation team reserves the right to cancel the challenge.",
    "Annuler": "Cancel",
    "Créer le défi": "Create Challenge",
    "La date d'expiration doit être dans le futur.": "The expiration date must be in the future.",
    "Le montant du pari doit être supérieur à 0.": "The bet amount must be greater than 0.",
    
    # Place Bet
    "Place Bet": "Place Bet",
    "Current Match": "Current Match",
    "Date and Time": "Date and Time",
    "Place Your Bet": "Place Your Bet",
    "Bet Amount (K)": "Bet Amount (K)",
    "Available Balance:": "Available Balance:",
    "Betting Rules": "Betting Rules",
    "Minimum Amount": "Minimum Amount",
    "1 K per bet": "1 K per bet",
    "Maximum Amount": "Maximum Amount",
    "available balance": "available balance",
    "Betting Deadline": "Betting Deadline",
    "Until match start": "Until match start",
    "Calculated based on amount": "Calculated based on amount",
    "Winnings are calculated based on bet amount and current odds": "Winnings are calculated based on bet amount and current odds",
    
    # Blog
    "Écrire un article": "Write an Article",
    "Publier l'article": "Publish Article",
    "Par": "By",
    "le": "on",
    "dans": "in",
    "vues": "views",
    "Modifier": "Edit",
    "Supprimer": "Delete",
    "Commentaires": "Comments",
    "Laisser un commentaire": "Leave a Comment",
    "Publier": "Publish",
    "Connectez-vous": "Log in",
    "pour laisser un commentaire.": "to leave a comment.",
    "Membre": "Member",
    "Posté le": "Posted on",
    "Modifié le": "Modified on",
    "Aucun commentaire pour le moment. Soyez le premier à commenter !": "No comments yet. Be the first to comment!",
    
    # Clans
    "Créer un nouveau clan": "Create New Clan",
    "Créer le clan": "Create Clan",
    "Jeu": "Game",
    "Victoires": "Wins",
    "Défaites": "Defeats",
    "Ratio": "Ratio",
    "Description": "Description",
    "Défier le clan": "Challenge the Clan",
    "Membres du clan": "Clan Members",
    "Pseudo": "Username",
    "Rôle": "Role",
    "Date d'entrée": "Join Date",
    "Aucun membre": "No members",
    "Historique des matchs": "Match History",
    "Score": "Score",
    "Résultat": "Result",
    "Victoire": "Victory",
    "Défaite": "Defeat",
    "En cours": "In Progress",
    "Aucun match joué": "No matches played",
    "Meilleurs Clans": "Top Clans",
    "Créer un clan": "Create Clan",
    "Voir le clan": "View Clan",
    "Aucun clan n'est encore créé.": "No clan has been created yet.",
    
    # Game List
    "Liste des Jeux": "Game List",
    "Tournois": "Tournaments", 
    "Voir les Tournois": "View Tournaments",
    "Aucun jeu disponible pour le moment.": "No games available at the moment.",
    
    # Home Page
    "Plateforme de Paris Sportifs Cyber": "Cyber Sports Betting Platform",
    "NOUVEAU TOURNOI VALORANT - 50K€ DE PRIZES": "NEW VALORANT TOURNAMENT - 50K€ PRIZES",
    "CHAMPIONNAT CS2 COMMENCE DEMAIN": "CS2 CHAMPIONSHIP STARTS TOMORROW",
    "RECORD BATTU: +2M€ DE PARIS CETTE SEMAINE": "RECORD BROKEN: +2M€ BETS THIS WEEK",
    "NOUVEAUX DÉFIS P2P DISPONIBLES": "NEW P2P CHALLENGES AVAILABLE",
    "LIVE: 15K SPECTATEURS SUR NOS STREAMS": "LIVE: 15K VIEWERS ON OUR STREAMS",
    "COMMUNAUTÉ: +50K NOUVEAUX MEMBRES": "COMMUNITY: +50K NEW MEMBERS",
    "Gagnez de l'": "Earn",
    "Gagnez de l'Argent en Jouant sur eBetStream": "Earn Money Playing on eBetStream",
    "Commencer à Gagner": "Start Earning",
    "Devenez la Star d'": "Become the Star of",
    "Devenez la Star d'eBetStream": "Become the Star of eBetStream", 
    "Devenir Légende": "Become a Legend",
    "Relevez des Défis Épiques": "Take on Epic Challenges",
    "Relevez des Défis Épiques sur eBetStream": "Take on Epic Challenges on eBetStream",
    "Lancer un Défi": "Launch a Challenge",
    "Placez des Paris Gagnants": "Place Winning Bets",
    "Placez des Paris Gagnants sur eBetStream": "Place Winning Bets on eBetStream",
    "Parier Maintenant": "Bet Now",
}

# Dictionnaire de traductions françaises vers espagnoles  
FR_TO_ES = {
    # Navigation et base
    "Jeux": "Juegos",
    "Paris": "Apuestas",
    "Mon Compte": "Mi Cuenta", 
    "Déconnexion": "Cerrar Sesión",
    "Connexion": "Iniciar Sesión",
    "Inscription": "Registrarse",
    "Retour à l'accueil": "Volver al Inicio",
    "Retour au blog": "Volver al Blog",
    "Retour à la liste des paris": "Volver a la Lista de Apuestas",
    "Parier": "Apostar",
    "Close": "Cerrar",
    
    # Footer
    "Votre plateforme de paris sportifs en ligne": "Tu plataforma de apuestas deportivas en línea",
    "Tous droits réservés.": "Todos los derechos reservados.",
    "Confidentialité": "Privacidad",
    "Conditions": "Términos",
    "eBetStream Logo": "Logo de eBetStream",
    
    # Betting
    "\"Double\" Betting System: Bet on a result and double your bet if you win!": "Sistema de Apuestas \"Doble\": ¡Apuesta por un resultado y duplica tu apuesta si ganas!",
    "Odds": "Cuotas",
    "Potential Winnings": "Ganancias Potenciales",
    "Your Choice": "Tu Elección",
    "Match Information": "Información del Partido",
    "Tournament": "Torneo",
    "Game": "Juego",
    "Match Date": "Fecha del Partido",
    "Match Status": "Estado del Partido",
    "Final Score": "Puntuación Final",
    "Congratulations! You won": "¡Felicidades! Ganaste",
    "with this bet.": "con esta apuesta.",
    "Too bad! You lost your bet of": "¡Qué mal! Perdiste tu apuesta de",
    "Your bet is pending the match result.": "Tu apuesta está pendiente del resultado del partido.",
    "Live Bet Information": "Información de Apuesta en Vivo",
    "Timestamp:": "Marca de tiempo:",
    "Game Time:": "Tiempo de Juego:",
    "Score at bet time:": "Puntuación al momento de la apuesta:",
    "Back to my bets": "Volver a mis apuestas",
    "Place another live bet": "Hacer otra apuesta en vivo",
    
    # Bet List
    "Total Bets": "Total de Apuestas",
    "Won Bets": "Apuestas Ganadas",
    "Lost Bets": "Apuestas Perdidas", 
    "Pending Bets": "Apuestas Pendientes",
    "Total Bet Amount": "Monto Total de Apuestas",
    "Total Winnings": "Ganancias Totales",
    "Net Profit": "Ganancia Neta",
    "Date": "Fecha",
    "Match": "Partido",
    "Choice": "Elección",
    "Amount": "Monto",
    "Potential Win": "Ganancia Potencial",
    "Status": "Estado",
    "You haven't placed any bets yet.": "Aún no has hecho ninguna apuesta.",
    "Page navigation": "Navegación de página",
    "Previous": "Anterior",
    "Next": "Siguiente",
    
    # Match List
    "Watch Live": "Ver en Vivo",
    "Aucun match disponible pour le moment.": "No hay partidos disponibles en este momento.",
    
    # P2P Challenges
    "Créer un Défi P2P": "Crear Desafío P2P",
    "Créer un Nouveau Défi P2P": "Crear Nuevo Desafío P2P",
    "Détails du défi": "Detalles del Desafío",
    "Titre du défi": "Título del Desafío",
    "Description du défi": "Descripción del Desafío",
    "Type de jeu": "Tipo de Juego",
    "Nom du jeu": "Nombre del Juego",
    "Adversaire": "Oponente",
    "Mises et règles": "Apuestas y Reglas",
    "Votre mise (Ktap)": "Tu Apuesta (Ktap)",
    "Solde disponible:": "Saldo disponible:",
    "Mise de l'adversaire (Ktap)": "Apuesta del Oponente (Ktap)",
    "Pot total du défi :": "Bote Total del Desafío:",
    "Ce montant sera bloqué sur votre compte jusqu'à la fin du défi.": "Este monto será bloqueado en tu cuenta hasta el final del desafío.",
    "Règles spécifiques (optionnel)": "Reglas Específicas (opcional)",
    "Format du match": "Formato del Partido",
    "Date limite d'acceptation": "Fecha Límite de Aceptación",
    "Important :": "Importante:",
    "En créant ce défi, vous acceptez que le montant de votre mise soit bloqué sur votre compte jusqu'à la fin du défi. En cas de non-respect des règles, l'équipe de modération se réserve le droit d'annuler le défi.": "Al crear este desafío, aceptas que el monto de tu apuesta sea bloqueado en tu cuenta hasta el final del desafío. En caso de incumplimiento de las reglas, el equipo de moderación se reserva el derecho de cancelar el desafío.",
    "Annuler": "Cancelar",
    "Créer le défi": "Crear Desafío",
    "La date d'expiration doit être dans le futur.": "La fecha de expiración debe estar en el futuro.",
    "Le montant du pari doit être supérieur à 0.": "El monto de la apuesta debe ser mayor a 0.",
    
    # Place Bet
    "Place Bet": "Hacer Apuesta",
    "Current Match": "Partido Actual",
    "Date and Time": "Fecha y Hora",
    "Place Your Bet": "Haz tu Apuesta",
    "Bet Amount (K)": "Monto de Apuesta (K)",
    "Available Balance:": "Saldo Disponible:",
    "Betting Rules": "Reglas de Apuestas",
    "Minimum Amount": "Monto Mínimo",
    "1 K per bet": "1 K por apuesta",
    "Maximum Amount": "Monto Máximo",
    "available balance": "saldo disponible",
    "Betting Deadline": "Fecha Límite de Apuestas",
    "Until match start": "Hasta el inicio del partido",
    "Calculated based on amount": "Calculado basado en el monto",
    "Winnings are calculated based on bet amount and current odds": "Las ganancias se calculan basadas en el monto de la apuesta y las cuotas actuales",
    
    # Blog
    "Écrire un article": "Escribir un Artículo",
    "Publier l'article": "Publicar Artículo",
    "Par": "Por",
    "le": "el",
    "dans": "en",
    "vues": "vistas",
    "Modifier": "Editar",
    "Supprimer": "Eliminar",
    "Commentaires": "Comentarios",
    "Laisser un commentaire": "Dejar un Comentario",
    "Publier": "Publicar",
    "Connectez-vous": "Iniciar sesión",
    "pour laisser un commentaire.": "para dejar un comentario.",
    "Membre": "Miembro",
    "Posté le": "Publicado el",
    "Modifié le": "Modificado el",
    "Aucun commentaire pour le moment. Soyez le premier à commenter !": "No hay comentarios por el momento. ¡Sé el primero en comentar!",
    
    # Clans
    "Créer un nouveau clan": "Crear Nuevo Clan",
    "Créer le clan": "Crear Clan",
    "Jeu": "Juego",
    "Victoires": "Victorias",
    "Défaites": "Derrotas",
    "Ratio": "Ratio",
    "Description": "Descripción",
    "Défier le clan": "Desafiar al Clan",
    "Membres du clan": "Miembros del Clan",
    "Pseudo": "Usuario",
    "Rôle": "Rol",
    "Date d'entrée": "Fecha de Ingreso",
    "Aucun membre": "Sin miembros",
    "Historique des matchs": "Historial de Partidos",
    "Score": "Puntuación",
    "Résultat": "Resultado",
    "Victoire": "Victoria",
    "Défaite": "Derrota",
    "En cours": "En Progreso",
    "Aucun match joué": "No se han jugado partidos",
    "Meilleurs Clans": "Mejores Clanes",
    "Créer un clan": "Crear Clan",
    "Voir le clan": "Ver Clan",
    "Aucun clan n'est encore créé.": "Aún no se ha creado ningún clan.",
    
    # Game List
    "Liste des Jeux": "Lista de Juegos",
    "Tournois": "Torneos",
    "Voir les Tournois": "Ver Torneos",
    "Aucun jeu disponible pour le moment.": "No hay juegos disponibles en este momento.",
    
    # Home Page
    "Plateforme de Paris Sportifs Cyber": "Plataforma de Apuestas Deportivas Cibernéticas",
    "NOUVEAU TOURNOI VALORANT - 50K€ DE PRIZES": "NUEVO TORNEO VALORANT - 50K€ EN PREMIOS",
    "CHAMPIONNAT CS2 COMMENCE DEMAIN": "CAMPEONATO CS2 COMIENZA MAÑANA",
    "RECORD BATTU: +2M€ DE PARIS CETTE SEMAINE": "RÉCORD ROTO: +2M€ EN APUESTAS ESTA SEMANA",
    "NOUVEAUX DÉFIS P2P DISPONIBLES": "NUEVOS DESAFÍOS P2P DISPONIBLES",
    "LIVE: 15K SPECTATEURS SUR NOS STREAMS": "EN VIVO: 15K ESPECTADORES EN NUESTROS STREAMS",
    "COMMUNAUTÉ: +50K NOUVEAUX MEMBRES": "COMUNIDAD: +50K NUEVOS MIEMBROS",
    "Gagnez de l'": "Gana",
    "Gagnez de l'Argent en Jouant sur eBetStream": "Gana Dinero Jugando en eBetStream",
    "Commencer à Gagner": "Empezar a Ganar",
    "Devenez la Star d'": "Conviértete en la Estrella de",
    "Devenez la Star d'eBetStream": "Conviértete en la Estrella de eBetStream",
    "Devenir Légende": "Convertirse en Leyenda",
    "Relevez des Défis Épiques": "Acepta Desafíos Épicos",
    "Relevez des Défis Épiques sur eBetStream": "Acepta Desafíos Épicos en eBetStream",
    "Lancer un Défi": "Lanzar un Desafío",
    "Placez des Paris Gagnants": "Haz Apuestas Ganadoras",
    "Placez des Paris Gagnants sur eBetStream": "Haz Apuestas Ganadoras en eBetStream",
    "Parier Maintenant": "Apostar Ahora",
}

def fix_po_file(file_path, translations_dict):
    """Fix a .po file by completing missing translations and removing fuzzy markers"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Skip fuzzy markers
        if line.strip() == "#, fuzzy" or line.strip().startswith("#,") and "fuzzy" in line:
            i += 1
            continue
            
        # Process msgid/msgstr pairs
        if line.startswith('msgid '):
            msgid_line = line
            new_lines.append(msgid_line)
            i += 1
            
            # Handle multiline msgid
            while i < len(lines) and lines[i].startswith('"') and not lines[i].startswith('msgstr'):
                new_lines.append(lines[i])
                i += 1
            
            # Process msgstr
            if i < len(lines) and lines[i].startswith('msgstr '):
                msgstr_line = lines[i]
                
                # Extract the msgid text
                msgid_match = re.search(r'msgid\s+"([^"]*)"', msgid_line)
                msgstr_match = re.search(r'msgstr\s+"([^"]*)"', msgstr_line)
                
                if msgid_match and msgstr_match:
                    msgid_text = msgid_match.group(1)
                    msgstr_text = msgstr_match.group(1)
                    
                    # If translation is empty and we have a translation for it
                    if not msgstr_text and msgid_text in translations_dict:
                        translation = translations_dict[msgid_text]
                        new_msgstr = f'msgstr "{translation}"'
                        new_lines.append(new_msgstr)
                    else:
                        new_lines.append(msgstr_line)
                else:
                    new_lines.append(msgstr_line)
                
                i += 1
                
                # Handle multiline msgstr
                while i < len(lines) and lines[i].startswith('"'):
                    new_lines.append(lines[i])
                    i += 1
            else:
                i += 1
        else:
            new_lines.append(line)
            i += 1
    
    # Write the fixed content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

if __name__ == "__main__":
    print("Fixing English translations...")
    fix_po_file('eBetStream/locale/en/LC_MESSAGES/django.po', FR_TO_EN)
    print("English translations fixed!")
    
    print("Fixing Spanish translations...")
    fix_po_file('eBetStream/locale/es/LC_MESSAGES/django.po', FR_TO_ES)
    print("Spanish translations fixed!")