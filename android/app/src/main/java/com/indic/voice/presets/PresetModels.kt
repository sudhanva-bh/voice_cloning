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
        // SHORT IDEAS (1 sentence)
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.ENGLISH,
            text = "Hello! This is a quick test of the voice cloning system."
        ),
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.ENGLISH,
            text = "How are you doing today? Hope everything is going well."
        ),
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.ENGLISH,
            text = "Your voice model has been synthesized successfully."
        ),
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.HINDI,
            text = "नमस्ते! यह वॉइस क्लोनिंग प्रणाली का एक त्वरित परीक्षण है।"
        ),
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.TELUGU,
            text = "హలో! ఇది వాయిస్ క్లోనింగ్ సిస్టమ్ యొక్క శీఘ్ర పరీక్ష."
        ),
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.TAMIL,
            text = "வணக்கம்! இது குரல் குளோனிங் அமைப்பின் விரைவான சோதனை."
        ),

        // MEDIUM IDEAS (2-3 sentences)
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.ENGLISH,
            text = "Artificial intelligence is rapidly transforming how we communicate across different languages and cultures. With on-device neural voice cloning, you can generate natural speech in real time without relying on cloud servers or internet access."
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.ENGLISH,
            text = "The weather is exceptionally pleasant outside this afternoon, with a gentle cool breeze and clear blue skies. It would be a great time to step out for a quick walk, catch some fresh air, and grab a cup of coffee."
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.HINDI,
            text = "आर्टिफिशियल इंटेलिजेंस हमारे संवाद करने के तरीके को तेजी से बदल रहा है। ऑन-डिवाइस न्यूरल वॉइस क्लोनिंग के साथ, आप क्लाउड सर्वर पर निर्भर हुए बिना वास्तविक समय में स्वाभाविक आवाज उत्पन्न कर सकते हैं।"
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.TELUGU,
            text = "కృత్రిమ మేధస్సు మనం వివిధ భాషలలో సంభాషించే విధానాన్ని వేగంగా మారుస్తోంది. ఆన్-డివైస్ న్యూరల్ వాయిస్ క్లోనింగ్ ద్వారా క్లౌడ్ సర్వర్‌లపై ఆధారపడకుండా రియల్ టైమ్‌లో సహజమైన ప్రసంగాన్ని రూపొందించవచ్చు."
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.TAMIL,
            text = "செயற்கை நுண்ணறிவு மொழிகளுக்கு இடையேயான தகவல் தொடர்பை வேகமாக மாற்றி வருகிறது. சாதனத்திலேயே இயங்கும் குரல் குளோனிங் மூலம் கிளவுட் சேவையகம் இல்லாமல் இயற்கையான குரலை உருவாக்க முடியும்."
        ),

        // LONG IDEAS (Paragraph)
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.ENGLISH,
            text = "The morning sun rose gently above the rolling green hills, casting a warm golden glow across the quiet valley below. A flock of wild geese soared gracefully against the amber dawn, while a cool morning mist slowly drifted through the pine forest. In the distance, the gentle rush of a mountain stream blended harmoniously with the awakening sounds of nature."
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.HINDI,
            text = "सुबह का सूरज धीरे-धीरे हरी पहाड़ियों के ऊपर उगा और नीचे शांत घाटी में एक सुनहरा प्रकाश बिखेर दिया। दूर पहाड़ों से बहने वाली नदी की कलकल ध्वनि प्रकृति के सुंदर वातावरण के साथ पूरी तरह घुलमिल गई, जिससे चारों ओर एक शांत और मनमोहक माहौल बन गया।"
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.TELUGU,
            text = "ఉదయపు సూర్యుడు పచ్చని కొండల మీదుగా నెమ్మదిగా ఉదయించి, లోయ అంతటా వెచ్చని బంగారు కాంతిని ప్రసరింపజేశాడు. చెట్ల గుండా వీచే చల్లని పిల్లగాలులు మరియు సుదూర వాగుల మధురమైన శబ్దం ప్రకృతి అందాన్ని మరింత ఇనుమడింపజేశాయి."
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.TAMIL,
            text = "காலை சூரியன் பசுமையான மலைகளுக்கு மேலே மெதுவாக எழுந்து, அமைதியான பள்ளத்தாக்கில் தங்கக் கதிர்களைப் பரப்பியது. பைன் மரக் காட்டின் வழியே குளிர்ந்த பனி மெல்ல நகர்ந்தது. தூரத்தில் உள்ள மலை ஓடையின் சலசலப்பு இயற்கையின் ஒலியோடு அழகாக இணைந்தது."
        )
    )
}
