import logging
from pypdf import PdfReader

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str | None:
    """
    Ouvre un fichier PDF, extrait le texte de toutes les pages, 
    le nettoie basiquement et le retourne.
    Retourne None si l'extraction échoue ou si le fichier est illisible.
    """
    try:
        reader = PdfReader(file_path)
        extracted_text = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text.append(text)
                
        if not extracted_text:
            return ""  # PDF lu mais aucune page ne contient du texte
            
        # Nettoyage basique : joindre les pages, nettoyer les espaces superflus
        full_text = "\n".join(extracted_text)
        cleaned_text = " ".join(full_text.split())
        
        return cleaned_text

    except Exception as e:
        logger.error(f"Failed to extract text from {file_path}: {str(e)}")
        return None
