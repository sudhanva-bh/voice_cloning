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
            text = "Good morning, everyone! Let's quickly revise what we learned yesterday."
        ),
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.ENGLISH,
            text = "Hey! How's it going? Hope you're doing well!"
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.ENGLISH,
            text = "Before we start today's topic, can someone tell me what we learned in the last class? Don't worry if you're not sure, just give it a try!"
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.ENGLISH,
            text = "Hey, are you free for lunch today? There's this really nice place nearby I've been wanting to try. We should go together!"
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.ENGLISH,
            text = "Today, we're going to learn about how plants make their own food. Plants use sunlight, water, and carbon dioxide to prepare food through a process called photosynthesis. The green pigment in leaves, called chlorophyll, helps absorb sunlight. During this process, plants also release oxygen into the air. Now, can anyone tell me why sunlight is so important for plants?"
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.ENGLISH,
            text = "Hey, I was thinking we could go somewhere this Saturday. Maybe leave in the morning, grab breakfast on the way, and drive down to the beach. We could spend some time there, get something nice to eat, and come back by evening. It's been a while since we went out together, so I thought it would be fun!"
        ),

        // ==========================================
        // HINDI PRESETS (हिंदी)
        // ==========================================
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.HINDI,
            text = "बच्चों, आज हम एक नया पाठ शुरू करेंगे।"
        ),
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.HINDI,
            text = "अरे सुनो, आज शाम को चाय पीने चलोगे?"
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.HINDI,
            text = "अच्छा बच्चों, बताओ अगर हम किसी संख्या को दो से गुणा करें, तो क्या होगा? चलो, एक उदाहरण से समझते हैं।"
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.HINDI,
            text = "अरे, आज शाम को थोड़ा बाहर घूमने चलें क्या? बहुत दिन हो गए आराम से बैठकर बातें किए हुए।"
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.HINDI,
            text = "बच्चों, आज हम जानेंगे कि बारिश कैसे होती है। जब सूरज की गर्मी से नदियों और समुद्र का पानी भाप बनकर ऊपर उठता है, तो वह ठंडा होकर छोटे-छोटे पानी की बूंदों में बदल जाता है। ये बूंदें मिलकर बादल बनाती हैं। जब बादल भारी हो जाते हैं, तो पानी बारिश के रूप में नीचे गिरता है। अब बताओ, बारिश हमारे लिए क्यों जरूरी है?"
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.HINDI,
            text = "यार, याद है पहले हम सब दोस्त कितनी मस्ती किया करते थे? हर छोटी सी बात पर हँसना, बिना किसी वजह के बाहर घूमने निकल जाना और घंटों बैठकर बातें करना। अब सब अपने-अपने काम में इतने बिजी हो गए हैं कि मिलने का टाइम ही नहीं मिलता। इस बार सबको बुलाकर कहीं मिलते हैं ना!"
        ),

        // ==========================================
        // TELUGU PRESETS (తెలుగు)
        // ==========================================
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.TELUGU,
            text = "పిల్లలూ, ఈ రోజు మనం కొత్త పాఠం నేర్చుకుందాం."
        ),
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.TELUGU,
            text = "హేయ్! సాయంత్రం కాఫీ తాగడానికి వెళ్దామా?"
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.TELUGU,
            text = "పిల్లలూ, ఒక సంఖ్యను రెండుతో గుణిస్తే ఏమవుతుందో చెప్పగలరా? సరే, ఒక చిన్న ఉదాహరణతో అర్థం చేసుకుందాం."
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.TELUGU,
            text = "నువ్వు చెప్పిన సినిమా నిన్న రాత్రి చూశాను. నిజంగా చాలా బాగుంది! ముఖ్యంగా చివర్లో జరిగినది అస్సలు ఊహించలేదు."
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.TELUGU,
            text = "పిల్లలూ, ఈ రోజు మనం వర్షం ఎలా పడుతుందో తెలుసుకుందాం. సూర్యుడి వేడికి సముద్రాలు, నదుల్లోని నీరు ఆవిరిగా మారి పైకి వెళ్తుంది. పైకి వెళ్లిన ఆవిరి చల్లబడి చిన్న చిన్న నీటి బిందువులుగా మారుతుంది. అవన్నీ కలిసి మేఘాలుగా ఏర్పడతాయి. మేఘాల్లో నీరు ఎక్కువైనప్పుడు వర్షం పడుతుంది. ఇప్పుడు చెప్పండి, వర్షం మనకు ఎందుకు అవసరం?"
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.TELUGU,
            text = "ఒరేయ్, మనం అందరం కలిసి బయటకు వెళ్లి ఎన్ని రోజులైందో కదా! ఒకప్పుడు ప్రతి వారాంతం ఏదో ఒక ప్లాన్ వేసుకునేవాళ్లం. ఇప్పుడు ఎవరి పనుల్లో వాళ్లు బిజీ అయిపోయారు. ఈ శనివారం అందరికీ వీలైతే ఎక్కడికైనా వెళ్దాం. మంచి రెస్టారెంట్లో తిని, కాసేపు సరదాగా మాట్లాడుకుందాం. ఏమంటావు?"
        ),

        // ==========================================
        // TAMIL PRESETS (தமிழ்)
        // ==========================================
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.TAMIL,
            text = "மாணவர்களே, இன்னைக்கு ஒரு புது பாடம் படிக்கலாம்."
        ),
        QuickIdea(
            section = IdeaSection.SHORT,
            language = IdeaLanguage.TAMIL,
            text = "ஹேய்! சாயங்காலம் டீ குடிக்க போலாமா?"
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.TAMIL,
            text = "சரி மாணவர்களே, ஒரு எண்ணை ரெண்டால பெருக்கினா என்ன கிடைக்கும்? யாராவது சொல்ல முடியுமா? வாங்க, ஒரு சின்ன உதாரணத்தோட புரிஞ்சுக்கலாம்."
        ),
        QuickIdea(
            section = IdeaSection.MEDIUM,
            language = IdeaLanguage.TAMIL,
            text = "நீங்க சொன்ன அந்த படத்தை நேத்து பார்த்தேன். செமையா இருந்துச்சு! முக்கியமா அந்த கடைசி சீன், சுத்தமா எதிர்பார்க்கவே இல்ல!"
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.TAMIL,
            text = "மாணவர்களே, இன்னைக்கு மழை எப்படி பெய்யுதுன்னு பார்க்கலாம். சூரியனோட வெப்பத்தால கடல், ஆறுகள்ல இருக்குற தண்ணீர் ஆவியாகி மேல போகுது. அந்த ஆவி மேல போய் குளிர்ந்ததும் சின்ன சின்ன நீர்த்துளிகளா மாறுது. அந்த நீர்த்துளிகள் எல்லாம் சேர்ந்து மேகங்களா உருவாகுது. மேகத்துல தண்ணீர் அதிகமானதும் மழையா கீழ விழுது. இப்ப சொல்லுங்க, மழை நமக்கு ஏன் முக்கியம்?"
        ),
        QuickIdea(
            section = IdeaSection.LONG,
            language = IdeaLanguage.TAMIL,
            text = "டேய், நாம எல்லாரும் சேர்ந்து வெளிய போய் எவ்வளவு நாள் ஆச்சு தெரியுமா? முன்னாடி எல்லா வாரமும் ஏதாவது பிளான் போட்டுட்டே இருப்போம். இப்ப எல்லாரும் அவங்க அவங்க வேலையில பிசியா இருக்காங்க. இந்த சனிக்கிழமை எல்லாருக்கும் ஃப்ரீயா இருந்தா எங்கேயாவது போலாம். நல்லா சாப்பிட்டு, கொஞ்ச நேரம் ஜாலியா பேசிட்டு வரலாம். என்ன சொல்ற?"
        )
    )
}
