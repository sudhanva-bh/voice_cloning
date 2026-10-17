package com.indic.voice.presets

data class ExampleTranscript(
    val title: String,
    val advantageBadge: String,
    val text: String
)

enum class IdeaSection {
    SHORT,
    MEDIUM,
    LONG
}

enum class IdeaLanguage(val displayName: String) {
    ALL("All"),
    ENGLISH("English"),
    HINDI("हिंदी"),
    TELUGU("తెలుగు"),
    TAMIL("தமிழ்")
}

data class QuickIdea(
    val section: IdeaSection,
    val language: IdeaLanguage,
    val text: String
)

object PresetData {

    val exampleTranscripts = listOf(
        // SHORT REFERENCE SCRIPTS (Recommended 2–4s audio for optimal conditioning)
        ExampleTranscript(
            title = "Default Reference",
            advantageBadge = "Standard 2.2s",
            text = "Some call me nature."
        ),
        ExampleTranscript(
            title = "Voice Test",
            advantageBadge = "Quick 2.5s",
            text = "Hello, this is a voice cloning test."
        ),
        ExampleTranscript(
            title = "Compact Pangram",
            advantageBadge = "Full phonetics (3s)",
            text = "The quick brown fox jumps over the lazy dog."
        ),
        ExampleTranscript(
            title = "Conversational Question",
            advantageBadge = "Natural inflection (2.5s)",
            text = "How is the weather outside today?"
        ),
        ExampleTranscript(
            title = "Formal Intro",
            advantageBadge = "Clear articulation (2.5s)",
            text = "Welcome to the speech laboratory."
        ),
        ExampleTranscript(
            title = "Steady Cadence",
            advantageBadge = "Smooth rhythm (3s)",
            text = "Every journey begins with a single step."
        ),
        ExampleTranscript(
            title = "Vowel Resonance",
            advantageBadge = "Warm tones (3.5s)",
            text = "Bright blue skies and warm sunshine fill the morning."
        ),

        // SHORT INDIC REFERENCE SCRIPTS
        ExampleTranscript(
            title = "Hindi Reference (हिंदी)",
            advantageBadge = "Short Indic (2.5s)",
            text = "नमस्ते, यह मेरी आवाज का परीक्षण है।"
        ),
        ExampleTranscript(
            title = "Telugu Reference (తెలుగు)",
            advantageBadge = "Short Indic (2.5s)",
            text = "నమస్కారం, ఇది నా గొంతు పరీక్ష."
        ),
        ExampleTranscript(
            title = "Tamil Reference (தமிழ்)",
            advantageBadge = "Short Indic (2.5s)",
            text = "வணக்கம், இது என் குரலின் சோதனை."
        ),

        // MEDIUM / LONGER REFERENCE SCRIPTS
        ExampleTranscript(
            title = "Casual & Conversational",
            advantageBadge = "Extended flow (~6s)",
            text = "Honestly, I am just hanging out at home today, relaxing and catching up on a few things before going out."
        ),
        ExampleTranscript(
            title = "Professional Narration",
            advantageBadge = "Formal narration (~7s)",
            text = "Welcome to the voice cloning demonstration. Accurate pronunciation and consistent pacing ensure the highest quality voice synthesis."
        )
    )

    val quickIdeas = listOf(
        // ==========================================
        // ENGLISH SHORT PHRASES (~2.0s to 3.0s)
        // ==========================================
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.ENGLISH,
            text = "Google LiteRT is fast and clear."
        ),
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.ENGLISH,
            text = "Hello! This is a quick test of the voice cloning system."
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.ENGLISH,
            text = "The weather is exceptionally pleasant outside this afternoon."
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.ENGLISH,
            text = "Artificial intelligence is running directly on your phone."
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.ENGLISH,
            text = "How are you doing today? Hope everything is going well."
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.ENGLISH,
            text = "Thank you for listening to this voice cloning demonstration."
        ),

        // ==========================================
        // HINDI SHORT PHRASES (हिंदी ~2.0s to 3.0s)
        // ==========================================
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.HINDI,
            text = "यह एक वॉइस क्लोनिंग का परीक्षण है।"
        ),
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.HINDI,
            text = "नमस्ते! आपका दिन शुभ और सुखद हो।"
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.HINDI,
            text = "गूगल लाइट-आरटी फोन पर बहुत तेजी से चलता है।"
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.HINDI,
            text = "आज मौसम बहुत सुहावना और खूबसूरत है।"
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.HINDI,
            text = "कृत्रिम बुद्धिमत्ता हमारे जीवन को आसान बना रही है।"
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.HINDI,
            text = "क्या आप आज शाम को टहलने चलेंगे?"
        ),

        // ==========================================
        // TELUGU SHORT PHRASES (తెలుగు ~2.0s to 3.0s)
        // ==========================================
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.TELUGU,
            text = "ఇది గూగుల్ లైట్-ఆర్టీతో వాయిస్ క్లోనింగ్ పరీక్ష."
        ),
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.TELUGU,
            text = "నమస్కారం! మీ రోజు ఆహ్లాదకరంగా సాగాలని కోరుకుంటున్నాను."
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.TELUGU,
            text = "ఈ రోజు వాతావరణం చాలా ఆహ్లాదకరంగా మరియు చల్లగా ఉంది."
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.TELUGU,
            text = "కృత్రిమ మేధస్సు నేరుగా మీ మొబైల్ ఫోన్‌లో పనిచేస్తోంది."
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.TELUGU,
            text = "మీరు ఈ రోజు ఎలా ఉన్నారు? అంతా బాగుందా?"
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.TELUGU,
            text = "ఈ వాయిస్ క్లోనింగ్ డెమో విన్నందుకు ధన్యవాదాలు."
        ),

        // ==========================================
        // TAMIL SHORT PHRASES (தமிழ் ~2.0s to 3.0s)
        // ==========================================
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.TAMIL,
            text = "கூகிள் லைட்-ஆர்டி தொழில்நுட்பம் மூலம் குரல் உருவாக்கம்."
        ),
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.TAMIL,
            text = "வணக்கம்! உங்கள் நாள் மகிழ்ச்சியாக அமையட்டும்."
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.TAMIL,
            text = "இன்று வானிலை மிகவும் இனிமையாகவும் தென்றலாகவும் இருக்கிறது."
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.TAMIL,
            text = "செயற்கை நுண்ணறிவு நேரடியாக உங்கள் போனில் இயங்குகிறது."
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.TAMIL,
            text = "நீங்கள் இன்று எப்படி இருக்கிறீர்கள்? எல்லாம் நலமா?"
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.TAMIL,
            text = "இந்த குரல் சோதனையைக் கேட்டதற்கு மிக்க நன்றி."
        )
    )
}
