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
        // ENGLISH PRESETS
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
            text = "Artificial intelligence is running directly on your phone. On-device neural voice cloning enables natural speech synthesis without cloud latency."
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.ENGLISH,
            text = "The weather is exceptionally pleasant outside this afternoon. Cool morning breezes through the hills bring fresh energy to the day."
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.ENGLISH,
            text = "The morning sun rose gently above the rolling green hills, casting a warm golden glow across the quiet valley below. A cool morning mist slowly drifted through the pine forest. In the distance, the gentle rush of a mountain stream blended harmoniously with the awakening sounds of nature."
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.ENGLISH,
            text = "Zero-shot voice cloning with Google LiteRT brings powerful neural speech synthesis right to your fingertips. By leveraging continuous flow matching and efficient neural vocoding, natural speech is synthesized completely offline on edge mobile devices."
        ),

        // ==========================================
        // HINDI PRESETS (हिंदी)
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
            text = "गूगल लाइट-आरटी फोन पर बहुत तेजी से चलता है। कृत्रिम बुद्धिमत्ता हमारे दैनिक जीवन को आसान और बेहतर बना रही है।"
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.HINDI,
            text = "आज मौसम बहुत सुहावना और खूबसूरत है। चारों ओर ठंडी हवाएं और हरी-भरी प्रकृति मन को बहुत शांति देती हैं।"
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.HINDI,
            text = "सुबह का सूरज धीरे-धीरे हरी पहाड़ियों के ऊपर उगा और नीचे शांत घाटी में एक सुनहरा प्रकाश बिखेर दिया। दूर पहाड़ों से बहने वाली नदी की मधुर ध्वनि प्रकृति के शांत वातावरण के साथ पूरी तरह घुलमिल गई, जिससे चारों ओर एक शांत और मनमोहक माहौल बन गया।"
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.HINDI,
            text = "ऑन-डिवाइस वॉइस क्लोनिंग तकनीक बिना किसी इंटरनेट या क्लाउड सर्वर के आपके फोन पर काम करती है। यह भारतीय भाषाओं में स्वाभाविक और सजीव आवाज उत्पन्न करने की दिशा में एक बड़ा कदम है।"
        ),

        // ==========================================
        // TELUGU PRESETS (తెలుగు)
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
            text = "కృత్రిమ మేధస్సు నేరుగా మీ మొబైల్ ఫోన్‌లో పనిచేస్తోంది. ఆన్-డివైస్ వాయిస్ క్లోనింగ్ ద్వారా క్లౌడ్ సర్వర్‌లపై ఆధారపడకుండా సహజమైన ప్రసంగాన్ని రూపొందించవచ్చు."
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.TELUGU,
            text = "ఈ రోజు వాతావరణం చాలా ఆహ్లాదకరంగా మరియు చల్లగా ఉంది. సుదూర కొండల నుండి వీచే పిల్లగాలులు మనసుకు ప్రశాంతతను కలిగిస్తున్నాయి."
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.TELUGU,
            text = "ఉదయపు సూర్యుడు పచ్చని కొండల మీదుగా నెమ్మదిగా ఉదయించి, లోయ అంతటా వెచ్చని బంగారు కాంతిని ప్రసరింపజేశాడు. చెట్ల గుండా వీచే చల్లని పిల్లగాలులు మరియు సుదూర వాగుల మధురమైన శబ్దం ప్రకృతి అందాన్ని మరింత ఇనుమడింపజేశాయి."
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.TELUGU,
            text = "గూగుల్ లైట్-ఆర్టీ సాంకేతికతతో ఎలాంటి ఇంటర్నెట్ అవసరం లేకుండా నేరుగా మొబైల్‌లోనే సహజమైన తెలుగు స్వరాన్ని సృష్టించవచ్చు. ఇది భారతీయ భాషా సాంకేతికతలో విప్లవాత్మక మార్పుకు నాంది."
        ),

        // ==========================================
        // TAMIL PRESETS (தமிழ்)
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
            text = "செயற்கை நுண்ணறிவு நேரடியாக உங்கள் போனில் இயங்குகிறது. சாதனத்திலேயே இயங்கும் குரல் குளோனிங் மூலம் கிளவுட் இல்லாமல் இயற்கையான குரலை உருவாக்க முடியும்."
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.TAMIL,
            text = "இன்று வானிலை மிகவும் இனிமையாகவும் தென்றலாகவும் இருக்கிறது. பசுமையான சூழலில் மெல்லிய தென்றல் காற்று மனதிற்கு இதமளிக்கிறது."
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.TAMIL,
            text = "காலை சூரியன் பசுமையான மலைகளுக்கு மேலே மெதுவாக எழுந்து, அமைதியான பள்ளத்தாக்கில் தங்கக் கதிர்களைப் பரப்பியது. பைன் மரக் காட்டின் வழியே குளிர்ந்த பனி மெல்ல நகர்ந்தது. தூரத்தில் உள்ள மலை ஓடையின் சலசலப்பு இயற்கையின் ஒலியோடு அழகாக இணைந்தது."
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.TAMIL,
            text = "கூகிள் லைட்-ஆர்டி மூலம் இணைய இணைப்பு இன்றியே உங்கள் போனில் அதிவேகமாக குரல் குளோனிங் செய்ய முடிகிறது. தமிழ் மொழியில் மிகத் துல்லியமான உச்சரிப்புடன் இயற்கையான பேச்சை உருவாக்க இது உதவுகிறது."
        )
    )
}
