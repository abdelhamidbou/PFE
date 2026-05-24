from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import database
import models
import schemas
import auth

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

SYMPTOM_KEYWORDS = {
    "acné": "L'acné peut être traitée avec des crèmes locales ou des traitements oraux selon sa sévérité. Nous recommandons un rendez-vous avec notre dermatologue pour un diagnostic précis.",
    "psoriasis": "Le psoriasis est une maladie auto-immune chronique. Nos dermatologues proposent des traitements adaptés incluant des crèmes, la photothérapie et des traitements biologiques.",
    "eczéma": "L'eczéma (dermatite atopique) peut être contrôlé avec des hydratants et des corticostéroïdes. Consultez nos spécialistes pour un plan de traitement personnalisé.",
    "grain de beauté": "Toute modification d'un grain de beauté nécessite une consultation rapide. Notre dérmascopie IA peut aider à évaluer le risque.",
    "démangeaison": "Les démangeaisons peuvent avoir de multiples causes : allergies, infections fongiques, peau sèche. Un examen dermatologique est recommandé.",
    "kératose": "La kératose actinique est une lésion pré-cancéreuse induite par le soleil. Une consultation est essentielle pour le traitement.",
    "cheveux": "Pour les problèmes de perte de cheveux, notre spécialiste en trichologie peut vous aider avec un diagnostic et un traitement avancés.",
    "ongles": "Les infections fongiques des ongles et autres affections peuvent être traitées efficacement après un examen microbiologique.",
    "boutons": "Les boutons peuvent être causés par l'acné, les allergies ou les infections. Consultez notre dermatologue pour un diagnostic précis.",
    "tache": "Les taches cutanées (taches de vieillesse, mélasma, etc.) peuvent être traitées avec le laser ou des peelings. Prenez un rendez-vous.\t",
}

DEFAULT_RESPONSE = "Merci pour votre message. Je peux vous aider avec les demandes générales sur la peau, la planification de rendez-vous et l'orientation vers le bon spécialiste. Pourriez-vous décrire vos symptômes ou ce avec quoi vous avez besoin d'aide ?"

GREETING_RESPONSES = [
    "Bonjour ! Je suis l'assistant IA de DermaFlow. Comment puis-je vous aider aujourd'hui ?",
    "Salut ! Je suis là pour vous aider avec vos questions dermatologiques et la planification de rendez-vous. Que ressentez-vous ?",
    "Bienvenue sur DermaFlow AI ! Je peux vous aider avec les questions sur la peau et la réservation de rendez-vous. Comment puis-je vous aider ?",
]


def generate_response(message: str) -> str:
    message_lower = message.lower().strip()

    greetings = ["bonjour", "salut", "hello", "bonsoir", "coucou"]
    if any(g in message_lower for g in greetings):
        import random
        return random.choice(GREETING_RESPONSES)

    for keyword, response in SYMPTOM_KEYWORDS.items():
        if keyword in message_lower:
            return response

    if "rendez-vous" in message_lower or "rdv" in message_lower or "book" in message_lower:
        return "Pour prendre un rendez-vous, veuillez vous connecter à votre portail patient et accéder à la section Rendez-vous. Vous pouvez aussi nous appeler au +212 5XX-XXXXXX."

    if "urgence" in message_lower or "urgent" in message_lower:
        return "Pour les urgences dermatologiques, veuillez nous appeler au +212 5XX-XXXXXX ou visitez directement notre clinique."

    if "spécialité" in message_lower or "spécialiste" in message_lower or "médecin" in message_lower:
        return "Nous avons les spécialités suivantes : Dermatologie Clinique, Dermato-Esthétique, Oncodermatologie, Trichologie, Allergologie Cutanée et Dermato-Pédiatrie. Quelle spécialité vous intéresse ?"

    if "heures" in message_lower or "ouvert" in message_lower or "horaires" in message_lower:
        return "DermaFlow AI est ouvert du Lundi au Vendredi de 8h à 20h et le Samedi de 9h à 14h. Les urgences sont disponibles 24/7."

    if "merci" in message_lower:
        return "Je vous en prie ! N'hésitez pas si vous avez d'autres questions."

    return DEFAULT_RESPONSE


@router.post("/message", response_model=schemas.ChatResponse)
def chat(chat_data: schemas.ChatRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == chat_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    response_text = generate_response(chat_data.message)

    chat_msg = models.ChatMessage(
        user_id=chat_data.user_id,
        message=chat_data.message,
        response=response_text,
    )
    db.add(chat_msg)
    db.commit()

    return schemas.ChatResponse(response=response_text, timestamp=datetime.utcnow())


@router.get("/history/{user_id}", response_model=list[schemas.ChatResponse])
def get_chat_history(user_id: int, limit: int = 50, db: Session = Depends(database.get_db)):
    messages = db.query(models.ChatMessage).filter(models.ChatMessage.user_id == user_id).order_by(models.ChatMessage.created_at.desc()).limit(limit).all()
    return [schemas.ChatResponse(response=m.response, timestamp=m.created_at) for m in reversed(messages)]
