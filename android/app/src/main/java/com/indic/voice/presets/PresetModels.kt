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
            title = "Friendly Greeting",
            advantageBadge = "Quick 2.5s",
            text = "Hello there! It is wonderful to meet you."
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
            title = "Coffee Break",
            advantageBadge = "Casual chat (2.5s)",
            text = "Let's take a quick coffee break and relax."
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
            title = "Hindi Greeting (हिंदी)",
            advantageBadge = "Short Indic (2.5s)",
            text = "नमस्ते, आप कैसे हैं? सब कुछ कैसा चल रहा है?"
        ),
        ExampleTranscript(
            title = "Telugu Greeting (తెలుగు)",
            advantageBadge = "Short Indic (2.5s)",
            text = "నమస్కారం, ఎలా ఉన్నారు? మీ పనులు ఎలా సాగుతున్నాయి?"
        ),
        ExampleTranscript(
            title = "Tamil Greeting (தமிழ்)",
            advantageBadge = "Short Indic (2.5s)",
            text = "வணக்கம், எப்படி இருக்கீங்க? இன்னைக்கு நாள் எப்படி போகுது?"
        ),

        // MEDIUM / LONGER REFERENCE SCRIPTS
        ExampleTranscript(
            title = "Casual & Conversational",
            advantageBadge = "Extended flow (~6s)",
            text = "Honestly, I am just hanging out at home today, relaxing and catching up on a few things before going out."
        ),
        ExampleTranscript(
            title = "Weekend Road Trip",
            advantageBadge = "Natural storytelling (~6s)",
            text = "We packed our bags early in the morning and drove out to the lake to spend the whole day outdoors."
        )
    )

    val quickIdeas = listOf(
        // ==========================================
        // ENGLISH PRESETS
        // ==========================================
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.ENGLISH,
            text = "Hey! Just wanted to check in and see how you're doing."
        ),
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.ENGLISH,
            text = "I'll be there in about ten minutes, see you soon!"
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.ENGLISH,
            text = "Are you free to grab some lunch together this afternoon? There's a great little cafe nearby that makes amazing food."
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.ENGLISH,
            text = "I just finished reading that book you recommended last week. You were right, the ending was totally unexpected!"
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.ENGLISH,
            text = "The morning sun rose gently above the rolling green hills, casting a warm golden glow across the quiet valley below. A cool morning mist slowly drifted through the pine forest. In the distance, the gentle rush of a mountain stream blended harmoniously with the awakening sounds of nature."
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.ENGLISH,
            text = "I was thinking we could head out early on Saturday morning and make a road trip to the coast. We could stop by that scenic viewpoint for coffee, take a stroll along the beach in the afternoon, and catch the sunset before heading back. What do you think?"
        ),

        // ==========================================
        // HINDI PRESETS (हिंदी)
        // ==========================================
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.HINDI,
            text = "अरे सुनो, क्या तुम शाम को चाय पीने आ रहे हो?"
        ),
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.HINDI,
            text = "नमस्ते! उम्मीद है आपका आज का दिन बहुत अच्छा बीत रहा होगा।"
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.HINDI,
            text = "क्या हम आज शाम को थोड़ी देर के लिए पार्क में टहलने चलें? काफी दिन हो गए हमें सुकून से बैठकर बातें किए हुए।"
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
            text = "मुझे पुरानी यादें ताजा करना बहुत पसंद है। जब हम सब दोस्त एक साथ बैठकर पुरानी बातें याद करते हैं और हंसते हैं, तो दिन की सारी थकान पल भर में गायब हो जाती है। हमें जिंदगी में ऐसी छोटी-छोटी खुशियों के लिए हमेशा वक्त निकालना चाहिए।"
        ),

        // ==========================================
        // TELUGU PRESETS (తెలుగు)
        // ==========================================
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.TELUGU,
            text = "హలో! సాయంత్రం కాఫీ తాగడానికి బయటకు వెళ్దామా?"
        ),
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.TELUGU,
            text = "నమస్కారం! మీ రోజంతా చాలా సంతోషంగా సాగాలని కోరుకుంటున్నాను."
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.TELUGU,
            text = "నువ్వు చెప్పిన సినిమా నిన్న రాత్రి చూశాను. కథ మరియు పాటలు నిజంగా చాలా బాగున్నాయి, నాకు చాలా బాగా నచ్చింది."
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
            text = "జీవితంలో ఎంత బిజీగా ఉన్నా సరే, మనసుకు నచ్చిన పనుల కోసం మరియు కుటుంబంతో గడపడానికి కొద్దిగా సమయం కేటాయించాలి. అప్పుడే మనసుకి కొత్త ఉత్సాహం మరియు పని చేయడంలో ఆనందం లభిస్తుంది. నువ్వు ఏమంటావు?"
        ),

        // ==========================================
        // TAMIL PRESETS (தமிழ்)
        // ==========================================
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.TAMIL,
            text = "ஹலோ! சாயங்காலம் டீ குடிக்க வெளியில போலாமா?"
        ),
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.TAMIL,
            text = "வணக்கம்! உங்கள் நாள் மகிழ்ச்சியாக அமையட்டும்."
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.TAMIL,
            text = "நீங்க சொன்ன அந்த புத்தகத்தை படிச்சு முடிச்சுட்டேன். கதை ரொம்ப சுவாரசியமா இருந்தது, எனக்கு ரொம்ப பிடிச்சிருந்தது."
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
            text = "எவ்வளவு வேலைகள் இருந்தாலும், நமக்குப் பிடித்த விஷயங்களுக்காகவும் குடும்பத்துடனும் சிறிது நேரம் ஒதுக்குவது மனதிற்கு மிகுந்த நிம்மதியைத் தரும். அப்பொழுதுதான் அடுத்த வேலைகளை உற்சாகமாக செய்ய முடியும். இதைப்பற்றி நீங்க என்ன நினைக்கிறீங்க?"
        )
    )
}
