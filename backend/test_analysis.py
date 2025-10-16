"""
Script de test pour l'endpoint /analyze
Usage: python test_analysis.py
"""
import requests
import json

# Données de test
test_data = {
    "form_data": {
        "q1": "Dupont",
        "q2": "Marie",
        "q3": "Comptable",
        "q4": "Comptabilité / Finance",
        "q5": "Actuellement, je reçois environ 50 factures fournisseurs par jour par e-mail. Je dois manuellement ouvrir chaque PDF, extraire les informations (montant, date, numéro fournisseur) et les saisir dans SAP. C'est très chronophage et source d'erreurs de saisie. Je voudrais que ces données soient automatiquement extraites des PDF et intégrées dans SAP avec une validation de ma part.",
        "q6": "1. Réception e-mail avec facture PDF en pièce jointe\n2. Téléchargement et ouverture du PDF\n3. Lecture manuelle des informations\n4. Saisie manuelle dans SAP (transaction FB60)\n5. Vérification de cohérence\n6. Archivage du PDF dans un dossier réseau\n7. Envoi e-mail de confirmation au fournisseur",
        "q7": "Quotidien",
        "q8": "51-200",
        "q9": "10-30 min",
        "q10": "2-5",
        "q11": "4",
        "q11a": "Tâche très répétitive sans valeur ajoutée intellectuelle, nombreuses erreurs de frappe qui génèrent des litiges fournisseurs",
        "q11b": "Les erreurs impactent directement la relation fournisseur et peuvent bloquer des livraisons critiques",
        "q12": "Factures PDF reçues par e-mail (formats variables selon fournisseurs), fichier Excel de suivi des saisies, données SAP",
        "q13": "Oui",
        "q13a": "Copier-coller manuel des données entre le PDF et SAP, vérification visuelle de cohérence entre montant HT/TTC, saisie des codes analytiques",
        "q14": "Oui",
        "q14a": "Certains fournisseurs envoient des factures dans des formats PDF différents (scannés vs natifs), nécessite validation manager si montant > 10 000€",
        "q15": "Moyenne",
        "q16": "Outlook (e-mails) + Adobe Reader (PDF) + SAP ERP + Excel (suivi)"
    }
}

def test_analyze():
    """Test de l'endpoint /analyze"""
    url = "http://localhost:5050/analyze"
    
    print("🧪 Test de l'analyse IA structurée")
    print("=" * 50)
    print("\n📤 Envoi des données...")
    
    try:
        response = requests.post(url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            print("✅ Succès !\n")
            result = response.json()
            
            print("📝 USER STORY:")
            print(result['user_story']['html'])
            print(f"   ({result['user_story']['word_count']} mots)\n")
            
            print("📊 SCHÉMA D'EXÉCUTION:")
            print(result['execution_schema']['ascii_diagram'])
            print("\nÉtapes:")
            for step in result['execution_schema']['steps']:
                print(f"   {step['step']}. {step['description']}")
            print()
            
            print("🔧 ÉLÉMENTS SOURCES:")
            for el in result['elements_sources']['types']:
                print(f"   • {el['category']}: {el['description']}")
            print(f"   Total: {result['elements_sources']['count']} type(s)")
            print(f"   Complexité: {result['elements_sources']['complexity_level']}\n")
            
            print("📈 ANALYSE:")
            print(f"   Pain points: {', '.join(result['analysis']['pain_points'])}")
            print(f"   Bénéfices: {', '.join(result['analysis']['benefits'])}")
            print(f"   Score faisabilité: {result['analysis']['feasibility_score']}/100")
            print(f"   Priorité: {result['analysis']['priority']}\n")
            
            print("=" * 50)
            print("✅ Structure JSON validée !")
            print("\n💾 JSON complet:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Backend non accessible")
        print("   Lancez: cd backend && uvicorn main:app --port 5050")
    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    test_analyze()

