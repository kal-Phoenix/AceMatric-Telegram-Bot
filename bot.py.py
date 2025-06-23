import os
import telebot
from telebot import types
import random
import time
import requests
from telebot import apihelper

# --- CONFIGURATION ---
# Retrieve the Telegram Bot API Token from environment variables for security.
# This token MUST be set in your deployment environment (e.g., Replit Secrets)
# or in your local PyCharm Run Configurations for testing.
API_TOKEN = os.environ.get('7604445147:AAFdvu2w2g1TLoY8w7dnIpIX6bsaYnn0Bug')

# Check if the API token is set. If not, print a warning.
# The bot will not function without a valid token.
if not API_TOKEN:
    print("WARNING: TELEGRAM_API_TOKEN environment variable not set. The bot will NOT start.")
    print("Please ensure your Telegram Bot API Token is configured in Replit Secrets or PyCharm Run Configurations.")
    # Exit or raise an error if the token is critical for startup
    # For a production bot, you might want to sys.exit(1) here
else:
    print("API Token found. Initializing bot...")
    bot = telebot.TeleBot(API_TOKEN)

# --- PREMIUM USER MANAGEMENT (SIMULATED FOR MVP) ---
# This set simulates premium users. In a real-world application,
# this would typically be managed by a persistent database (e.g., Firestore)
# and integrated with a payment gateway (like Chapa or Telebirr).
PREMIUM_USERS = set()  # Stores chat_ids of users who are 'premium' for the current session.

# Define the base path where all educational resources (PDFs) are stored.
# This path is relative to the bot's root directory.
RESOURCES_BASE_PATH = 'resources/'

# List of official EUEE (Ethiopian University Entrance Examination) grade levels.
GRADES = ["9", "10", "11", "12"]

# Define the subject categories and their sub-categories.
# This structure helps organize the educational materials.
CATEGORIES = {
    "English": ["textbooks", "workbooks", "past_papers"],
    "Mathematics": ["textbooks", "workbooks", "past_papers"],
    "Natural Science": ["textbooks", "workbooks", "past_papers"],
    "Social Science": ["textbooks", "workbooks", "past_papers"]
}


# --- HELPER FUNCTIONS FOR RESOURCE MANAGEMENT ---

def ensure_resource_paths_and_dummy_files():
    """
    Ensures that the necessary directory structure for resources exists
    and creates dummy PDF files for demonstration purposes.
    This function helps in local testing and initial deployment setup.
    """
    print("Ensuring resource paths and creating dummy files...")

    # Create the base 'resources/' directory if it doesn't already exist.
    if not os.path.exists(RESOURCES_BASE_PATH):
        os.makedirs(RESOURCES_BASE_PATH)

    # Iterate through defined grades, subjects, and categories to create directories
    # and a placeholder PDF file in each leaf directory.
    for grade in GRADES:
        grade_path = os.path.join(RESOURCES_BASE_PATH, f"grade_{grade}")
        if not os.path.exists(grade_path):
            os.makedirs(grade_path)  # Create grade-specific directory

        for subject, categories_list in CATEGORIES.items():
            # Standardize subject name for file paths (e.g., "Natural Science" -> "natural_science")
            subject_path = os.path.join(grade_path, subject.replace(" ", "_").lower())
            if not os.path.exists(subject_path):
                os.makedirs(subject_path)  # Create subject-specific directory

            for category in categories_list:
                category_path = os.path.join(subject_path, category)
                if not os.path.exists(category_path):
                    os.makedirs(category_path)  # Create category-specific directory

                # Define dummy PDF file name based on conventions
                dummy_file_name = f"G{grade}_{subject.replace(' ', '_').lower()}_{category}_sample.pdf"
                dummy_file_path = os.path.join(category_path, dummy_file_name)

                # Create the dummy file if it doesn't exist
                if not os.path.exists(dummy_file_path):
                    with open(dummy_file_path, 'w') as f:
                        f.write(
                            f"This is a dummy PDF for {subject.replace(' ', ' ').title()} - {category.replace('_', ' ').title()} - Grade {grade}. Replace with actual content!\n")
    print("Resource paths ensured and dummy files created.")


# Ensure resources are set up only if bot initialization is successful
if API_TOKEN:
    ensure_resource_paths_and_dummy_files()

# --- BOT MESSAGES & CONTENT ---
WELCOME_MESSAGE_EN = """
Hello! I'm AceMatric Bot, your AI-powered EUEE prep assistant! 🤖
I'm here to help you ace your exams, brought to you by Top Scorer AAU Students!
Tap a command or button below to get started.
"""
WELCOME_MESSAGE_AM = """
ሰላም! እኔ ኤሴማትሪክ ቦት ነኝ፣ የአንተ/ሷ የኢዩኢኢ (EUEE) ዝግጅት ረዳት! 🤖
በAAU ከፍተኛ ውጤት ባስመዘገቡ ተማሪዎች የተዘጋጀን ነን። ፈተናዎችዎን በቀላሉ እንዲያልፉ ለመርዳት እዚህ ነኝ።
ለመጀመር ከታች ያሉትን ትዕዛዞች ወይም ቁልፎች ይጫኑ።
"""

MAIN_MENU_MESSAGE_EN = "What would you like to explore today?"
MAIN_MENU_MESSAGE_AM = "ዛሬ ምን ማሰስ ይፈልጋሉ?"

PREMIUM_TEASE_MESSAGE_EN = """
🌟 *AceMatric Premium Access:* 🌟
Unlock detailed, explained answers for all past EUEE papers, one-to-one mentorship with AAU Top Scorers, personalized progress tracking, advanced practice content, and cutting-edge AI-aided study tools!

*To get Premium Access, please make your payment using one of the following methods, then contact our support with your Telegram username and transaction details.*

* **CBE Account:** `YOUR_CBE_ACCOUNT_NUMBER_HERE`
    * **Account Name:** `AceMatric Solutions` (Example)
* **Telebirr Account:** `YOUR_TELEBIRR_PHONE_NUMBER_HERE`
    * **Account Name:** `AceMatric Payments` (Example)

Visit our upcoming website for more details: [Your Website Link Here - e.g., acematric.com]

You can simulate premium access for testing by using the /simulate_premium command.
"""
PREMIUM_TEASE_MESSAGE_AM = """
🌟 *ኤሴማትሪክ ፕሪሚየም አገልግሎት:* 🌟
ሁሉንም ያለፉትን የEUEE ፈተናዎች የተብራሩ መልሶች፣ ከAAU ከፍተኛ ውጤት ካስመዘገቡ ተማሪዎች ጋር አንድ-ለአአ ትምህርት፣ የሂደት ክትትል፣ የተሻሻሉ የልምምድ ይዘቶች እና ዘመናዊ AI የታገዘ የጥናት መሳሪያዎችን ያግኙ!

ለመመዝገብ በቅርብ የሚከፈተውን ድረ-ገጻችንን ይጎብኙ: [የእርስዎ ድረ-ገጽ ሊንክ - ለምሳሌ፣ acematric.com]

ለመሞከር የፕሪሚየም አገልግሎትን ለማስመሰል /simulate_premium ትዕዛዝ መጠቀም ይችላሉ።
"""

# Example Daily Challenge (can be updated daily/weekly)
DAILY_CHALLENGE_EN = {
    "question": "Which of the following is the main function of the kidney?",
    "options": ["A) Pumping blood", "B) Producing hormones", "C) Filtering blood and producing urine",
                "D) Digesting food"],
    "answer": "C",
    "explanation": "The kidneys play a vital role in filtering waste products from the blood and regulating fluid balance by producing urine."
}
DAILY_CHALLENGE_AM = {
    "question": "ከሚከተሉት ውስጥ የኩላሊት ዋና ተግባር የትኛው ነው?",
    "options": ["ሀ) ደም ማፍሰስ", "ለ) ሆርሞኖችን ማምረት", "ሐ) ደምን ማጣራት እና ሽንት ማምረት", "መ) ምግብ መፈጨት"],
    "answer": "ሐ",
    "explanation": "ኩላሊት ከደም ውስጥ ቆሻሻዎችን በማጣራት እና ሽንትን በማምረት የሰውነት ፈሳሽ ሚዛንን በመጠበቅ ረገድ ወሳኝ ሚና ይጫወታል።"
}

# Example Concepts in a Minute (can add many more)
CONCEPTS = [
    {
        "title_en": "Photosynthesis Basics (Biology)",
        "title_am": "የፎቶሲንተሲስ መሰረታዊ ነገሮች (ባዮሎጂ)",
        "content_en": "Photosynthesis is the process by which green plants, algae, and some bacteria convert light energy into chemical energy, in the form of glucose. It primarily occurs in the chloroplasts using chlorophyll. Key ingredients are carbon dioxide, water, and sunlight, producing glucose and oxygen.",
        "content_am": "ፎቶሲንተሲስ አረንጓዴ ተክሎች፣ አልጌዎች እና አንዳንድ ባክቴሪያዎች የብርሃን ኃይልን ወደ ኬሚካዊ ኃይል (ግሉኮስ) የሚቀይሩበት ሂደት ነው። በዋነኛነት የሚካሄደው በክሎሮፕላስትስ ውስጥ ክሎሮፊልን በመጠቀም ነው። ዋናዎቹ ግብዓቶች ካርቦን ዳይኦክሳይድ፣ ውሃ እና የፀሐይ ብርሃን ሲሆኑ፣ ግሉኮስ እና ኦክሲጅን ያመነጫል።",
        "stream": "Natural Science"
    },
    {
        "title_en": "Supply and Demand (Economics)",
        "title_am": "አቅርቦትና ፍላጎት (ኢኮኖሚክስ)",
        "content_en": "In economics, supply and demand is a fundamental concept describing the interaction between the availability of a product or service (supply) and the desire for it (demand). This interaction determines market price and quantity. High demand with low supply typically leads to higher prices, and vice versa.",
        "content_am": "በኢኮኖሚክስ ውስጥ፣ አቅርቦትና ፍላጎት የምርት ወይም አገልግሎት መገኘትን (አቅርቦት) እና ለእሱ ያለውን ፍላጎት (ፍላጎት) መካከል ያለውን መስተጋብር የሚገልጽ መሰረታዊ ጽንሰ-ሀሳብ ነው። ይህ መስተጋብር የገበያ ዋጋን እና መጠኑን ይወስናል። ከፍተኛ ፍላጎት ከዝቅተኛ አቅርቦት ጋር ሲጣመር ብዙውን ጊዜ ወደ ከፍተኛ ዋጋዎች ይመራል፣ እና በተቃራኒው።",
        "stream": "Social Science"
    }
]

MOTIVATIONAL_QUOTES = [
    "The only way to do great work is to love what you do. – Steve Jobs\nትልቅ ስራ ለመስራት ብቸኛው መንገድ የሚሰሩትን መውደድ ነው። – ስቲቭ ጆብስ",
    "Believe you can and you're halfway there. – Theodore Roosevelt\nእንደሚችሉ ካመኑ ግማሽ መንገድ ተጉዘዋል። – ቴዎዶር ሩዝቬልት",
    "Success is not final, failure is not fatal: It is the courage to continue that counts. – Winston Churchill\nስኬት የመጨረሻ አይደለም፣ ውድቀትም ገዳይ አይደለም፡ ዋናው የመቀጠል ድፍረት ነው። – ዊንስተን ቸርችል",
    "Education is the most powerful weapon which you can use to change the world. – Nelson Mandela\nትምህርት ዓለምን ለመለወጥ የሚጠቀሙበት እጅግ ኃይለኛ መሳሪያ ነው። – ኔልሰን ማንዴላ"
]


# --- HELPER FUNCTIONS ---

def is_premium_user(chat_id):
    """
    Checks if a user is a premium user.
    In MVP, this is a simulated check. In production, it would query a database.
    """
    return chat_id in PREMIUM_USERS


def get_files_in_directory(directory_path):
    """
    Function to get PDF files from a specified path.
    """
    files = []
    if os.path.exists(directory_path):
        for f in os.listdir(directory_path):
            if f.endswith('.pdf'):
                files.append(os.path.join(directory_path, f))
    return files


# --- BOT HANDLERS ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """
    Handles /start and /help commands, sending a welcome message and main menu.
    """
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_resources = types.KeyboardButton('📚 Resources')
    btn_daily_challenge = types.KeyboardButton('🧠 Daily Challenge')
    btn_concept_in_minute = types.KeyboardButton('💡 Concept in a Minute')
    btn_motivate = types.KeyboardButton('✨ Motivation')
    btn_premium = types.KeyboardButton('🌟 Premium Access')

    # Add premium simulation buttons for testing, keeping them somewhat distinct
    btn_sim_premium = types.KeyboardButton('🧪 Simulate Premium')
    btn_check_premium = types.KeyboardButton('✅ Check Premium Status')

    markup.add(btn_resources, btn_daily_challenge, btn_concept_in_minute, btn_motivate, btn_premium, btn_sim_premium,
               btn_check_premium)

    bot.send_message(
        message.chat.id,
        f"{WELCOME_MESSAGE_EN}\n\n{WELCOME_MESSAGE_AM}",
        reply_markup=markup
    )


@bot.message_handler(commands=['resources'])
def show_grades_menu(message):
    """
    Displays the grade selection menu first.
    """
    markup = types.InlineKeyboardMarkup(row_width=4)
    for grade in GRADES:
        markup.add(types.InlineKeyboardButton(f"Grade {grade} | {grade}ኛ ክፍል", callback_data=f'select_grade_{grade}'))

    bot.send_message(
        message.chat.id,
        "Which grade's resources would you like to explore? | የየትኛው ክፍል ይዘቶችን ማሰስ ይፈልጋሉ?",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('select_grade_'))
def show_resource_types_menu(call):
    """
    Displays resource type menu after grade selection.
    """
    bot.answer_callback_query(call.id)
    grade = call.data.split('_')[2]

    markup = types.InlineKeyboardMarkup(row_width=2)

    # Free Resources
    markup.add(types.InlineKeyboardButton("Official Textbooks (Free) | መጽሃፍት (ነፃ)",
                                          callback_data=f'select_type_{grade}_textbooks_free'))
    markup.add(types.InlineKeyboardButton("Teacher Guides (Free) | የመምህር መመሪያ (ነፃ)",
                                          callback_data=f'select_type_{grade}_teacher_guides_free'))
    markup.add(types.InlineKeyboardButton("Free Mock Exams | ነፃ ሞክ ፈተናዎች",
                                          callback_data=f'select_type_{grade}_mock_exams_free'))

    # Premium Resources
    markup.add(types.InlineKeyboardButton("Premium Past Papers (Paid) | ያለፉት ፈተናዎች (የሚከፈልበት)",
                                          callback_data=f'select_type_{grade}_past_papers_premium'))
    markup.add(types.InlineKeyboardButton("Advanced Practice Content (Paid) | የላቀ የልምምድ ይዘት (የሚከፈልበት)",
                                          callback_data=f'select_type_{grade}_advanced_practice_premium'))
    markup.add(types.InlineKeyboardButton("Premium Study Resources (Paid) | ፕሪሚየም የጥናት ግብዓቶች (የሚከፈልበት)",
                                          callback_data=f'select_type_{grade}_study_resources_premium'))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Great! Now, what type of Grade {grade} resource are you looking for? | በጣም ጥሩ! አሁን፣ የ{grade}ኛ ክፍል ምን አይነት ይዘት እየፈለጉ ነው?",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('select_type_'))
def show_stream_selection_or_send(call):
    """
    Displays stream selection menu for grades 11 and 12,
    or directly sends files for grades 9 and 10 (general stream),
    or sends 'coming soon' for advanced premium types.
    """
    bot.answer_callback_query(call.id)
    parts = call.data.split('_')
    grade = parts[2]
    resource_type = parts[3]  # e.g., 'textbooks', 'past_papers'
    access_type = parts[4]  # 'free' or 'premium'

    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Handle premium access check
    if access_type == 'premium' and not is_premium_user(chat_id):
        bot.send_message(
            chat_id,
            "Access to this resource requires AceMatric Premium! �\n"
            "ይህንን ይዘት ለመድረስ የኤሴማትሪክ ፕሪሚየም አገልግሎት ያስፈልግዎታል። 🚀\n\n"
            "Use /premium to learn more or /simulate_premium for testing purposes. \n"
            "ለበለጠ መረጃ /premiumን ይጠቀሙ ወይም ለመሞከር /simulate_premiumን ይጠቀሙ።"
        )
        return

    # For 'coming soon' categories (Advanced Practice, Study Resources)
    if resource_type in ['advanced_practice', 'study_resources']:
        bot.send_message(
            chat_id=chat_id,
            text=f"Content for Grade {grade} {resource_type.replace('_', ' ').title()} is being prepared! Check back soon. 🚧\n"
                 f"ለ{grade}ኛ ክፍል {resource_type.replace('_', ' ').title()} ይዘት እየተዘጋጀ ነው። በቅርቡ ይመለሱ። 🚧"
        )
        return

    # Determine if stream selection is needed based on grade
    if grade in ['9', '10']:
        # For Grade 9 and 10, no stream selection needed, directly send files from 'general' stream folder
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Fetching Grade {grade} {resource_type.replace('_', ' ').title()} (General Curriculum)...\n"
                 f"{grade}ኛ ክፍል {resource_type.replace('_', ' ').title()} (አጠቃላይ ሥርዓተ ትምህርት) እየተጫነ ነው።"
        )
        # Directly call the file sending function with 'general' as stream_type
        # Construct a dummy call object to pass all required data to send_files_by_grade_type_stream
        dummy_call_data = f'send_files_{grade}_{resource_type}_{access_type}_general'  # Using 'general' as stream
        dummy_call = types.CallbackQuery(id=call.id, from_user=call.from_user, message=call.message,
                                         data=dummy_call_data)
        send_files_by_grade_type_stream(dummy_call)

    else:  # Grade 11 and 12, require stream selection
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_ns = types.InlineKeyboardButton("Natural Science | የተፈጥሮ ሳይንስ",
                                            callback_data=f'send_files_{grade}_{resource_type}_{access_type}_natural_science')
        btn_ss = types.InlineKeyboardButton("Social Science | የማህበራዊ ሳይንስ",
                                            callback_data=f'send_files_{grade}_{resource_type}_{access_type}_social_science')
        markup.add(btn_ns, btn_ss)

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Please select your stream for Grade {grade} {resource_type.replace('_', ' ').title()}:\n"
                 f"የ{grade}ኛ ክፍል {resource_type.replace('_', ' ').title()} ለማግኘት ክፍልዎን ይምረጡ:",
            reply_markup=markup
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith('send_files_'))
def send_files_by_grade_type_stream(call):
    """
    Sends files based on selected grade, resource type, and stream.
    Callback data: send_files_{grade}_{resource_type}_{access_type}_{stream_name}
    """
    bot.answer_callback_query(call.id)
    parts = call.data.split('_')
    # Expected parts: [send, files, grade, resource_type, access_type, stream_name]
    grade = parts[2]
    resource_type = parts[3]
    access_type = parts[4]
    stream_name = parts[5]  # 'general', 'natural_science', or 'social_science'

    chat_id = call.message.chat.id
    message_id = call.message.message_id

    # Double-check premium access
    if access_type == 'premium' and not is_premium_user(chat_id):
        bot.send_message(
            chat_id,
            "Access to this resource requires AceMatric Premium! 🚀\n"
            "ይህንን ይዘት ለመድረስ የኤሴማትሪክ ፕሪሚየም አገልግሎት ያስፈልግዎታል። 🚀\n\n"
            "Use /premium to learn more or /simulate_premium for testing purposes. \n"
            "ለበለጠ መረጃ /premiumን ይጠቀሙ ወይም ለመሞከር /simulate_premiumን ይጠቀሙ።"
        )
        return

    # Construct the file path dynamically
    # Example: resources/textbooks/grade_12/natural_science/ or resources/textbooks/grade_9/general/
    selected_path = os.path.join(RESOURCES_BASE_PATH, resource_type, f'grade_{grade}', stream_name)

    files = get_files_in_directory(selected_path)

    if files:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Sending Grade {grade} {stream_name.replace('_', ' ').title()} {resource_type.replace('_', ' ').title()}...\n"
                 f"{grade}ኛ ክፍል {stream_name.replace('_', ' ').title()} {resource_type.replace('_', ' ').title()} እየላኩ ነው።"
        )
        for file_path in files:
            try:
                with open(file_path, 'rb') as f:
                    bot.send_document(chat_id, f)
                time.sleep(0.5)  # Small delay between sending files
            except Exception as e:
                bot.send_message(chat_id,
                                 f"Error sending {os.path.basename(file_path)}: {e}\n{os.path.basename(file_path)} ሲላክ ስህተት ተፈጥሯል፡ {e}")
        bot.send_message(chat_id, "All requested files sent! ✅\nየጠየቁት ፋይሎች በሙሉ ተልከዋል! ✅")
    else:
        bot.send_message(chat_id,
                         "No files found for this category yet. Please check back later! 📚\nለዚህ ምድብ እስካሁን ምንም ፋይሎች የሉም። እባክዎ በኋላ ይሞክሩ! 📚")


@bot.message_handler(commands=['dailychallenge'])
def daily_challenge(message):
    """
    Presents a daily EUEE-style multiple-choice question.
    """
    # Simulate alternating streams for the challenge
    if random.random() < 0.5:
        challenge_data_en = DAILY_CHALLENGE_EN
        challenge_data_am = DAILY_CHALLENGE_AM
        stream_tag = "#NaturalScience"
    else:
        # For simplicity, using same challenge, but in real scenario, fetch a different one
        challenge_data_en = CONCEPTS[1]  # Using Economics concept as a stand-in for SS challenge
        challenge_data_am = CONCEPTS[1]
        stream_tag = "#SocialScience"

    markup = types.InlineKeyboardMarkup(row_width=1)
    for option_text in challenge_data_en["options"]:
        markup.add(types.InlineKeyboardButton(option_text, callback_data=f'dc_answer_{option_text[0]}'))

    bot.send_message(
        message.chat.id,
        f"*{stream_tag} Daily Ace Challenge!* 🧠\n\n"
        f"**Question (English):** {challenge_data_en['question']}\n"
        f"**Question (Amharic):** {challenge_data_am['question']}\n\n"
        f"Options:\n" + "\n".join(challenge_data_en["options"]) + "\n" + "\n".join(challenge_data_am["options"]),
        reply_markup=markup,
        parse_mode='Markdown'
    )
    bot.user_data = bot.user_data if hasattr(bot, 'user_data') else {}
    bot.user_data[message.chat.id] = {"challenge_answer": challenge_data_en["answer"],
                                      "challenge_explanation_en": challenge_data_en["explanation"],
                                      "challenge_explanation_am": challenge_data_am["explanation"]}


@bot.callback_query_handler(func=lambda call: call.data.startswith('dc_answer_'))
def handle_daily_challenge_answer(call):
    """
    Handles answers to the daily challenge.
    """
    bot.answer_callback_query(call.id)
    selected_option = call.data.split('_')[2]

    user_challenge_data = bot.user_data.get(call.message.chat.id)

    if user_challenge_data:
        correct_answer = user_challenge_data["challenge_answer"]
        explanation_en = user_challenge_data["challenge_explanation_en"]
        explanation_am = user_challenge_data["challenge_explanation_am"]

        if selected_option.upper() == correct_answer.upper():
            bot.send_message(call.message.chat.id, "Correct! 🎉 You're an Ace! \nትክክል! 🎉 ጎበዝ ነህ/ሽ!")
        else:
            bot.send_message(call.message.chat.id,
                             f"Oops! That's not quite right. The correct answer was {correct_answer}. \nስህተት ነው! ትክክለኛው መልስ {correct_answer} ነበር።")

        bot.send_message(
            call.message.chat.id,
            f"**Explanation (English):** {explanation_en}\n\n**ማብራሪያ (አማርኛ):** {explanation_am}",
            parse_mode='Markdown'
        )
        del bot.user_data[call.message.chat.id]  # Clear challenge data after response
    else:
        bot.send_message(call.message.chat.id,
                         "Challenge data expired or not found. Try a new `/dailychallenge`! \nየፈተናው መረጃ አልቋል ወይም አልተገኘም። አዲስ `/dailychallenge` ይሞክሩ! ")


@bot.message_handler(commands=['concept'])
def concept_in_minute(message):
    """
    Sends a random 'concept in a minute' explanation.
    """
    concept = random.choice(CONCEPTS)

    bot.send_message(
        message.chat.id,
        f"*{concept['stream']} Concept in a Minute!* 💡\n\n"
        f"**{concept['title_en']}**\n{concept['content_en']}\n\n"
        f"**{concept['title_am']}**\n{concept['content_am']}",
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['motivate'])
def motivate_student(message):
    """
    Sends a random motivational quote.
    """
    quote = random.choice(MOTIVATIONAL_QUOTES)
    bot.send_message(
        message.chat.id,
        f"✨ *Motivation from AceMatric!* ✨\n\n_{quote}_",
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['premium'])
def show_premium_direct(message):
    """
    Allows direct access to premium features teaser.
    """
    bot.send_message(
        message.chat.id,
        f"{PREMIUM_TEASE_MESSAGE_EN}\n{PREMIUM_TEASE_MESSAGE_AM}",
        parse_mode='Markdown'
    )


@bot.message_handler(commands=['simulate_premium'])
def simulate_premium(message):
    """
    Adds the user's chat_id to the PREMIUM_USERS set, simulating premium access.
    """
    PREMIUM_USERS.add(message.chat.id)
    bot.send_message(
        message.chat.id,
        "🎉 You now have simulated AceMatric Premium access! Try accessing 'Premium Past Papers' via /resources.\n"
        "🎉 አሁን የኤሴማትሪክ ፕሪሚየም አገልግሎት አስመስለዋል። 'Premium Past Papers'ን በ /resources በኩል ለመድረስ ይሞክሩ።"
    )


@bot.message_handler(commands=['check_premium'])
def check_premium_status(message):
    """
    Checks and reports the user's premium status.
    """
    if is_premium_user(message.chat.id):
        bot.send_message(message.chat.id,
                         "✅ You currently have AceMatric Premium access! \n✅ በአሁኑ ጊዜ የኤሴማትሪክ ፕሪሚየም አገልግሎት አለዎት።")
    else:
        bot.send_message(message.chat.id,
                         "❌ You do not have AceMatric Premium access. Use /premium to learn more. \n❌ የኤሴማትሪክ ፕሪሚየም አገልግሎት የለዎትም። የበለጠ ለማወቅ /premiumን ይጠቀሙ።")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """
    Responds to any other text message with a prompt to use commands.
    """
    bot.reply_to(
        message,
        "I'm AceMatric Bot! Please use the commands or buttons to interact with me. \n"
        "እኔ ኤሴማትሪክ ቦት ነኝ! እባክዎን ለመግባባት ትዕዛዞችን ወይም ቁልፎችን ይጠቀሙ።"
    )


# --- START THE BOT ---
print("AceMatric Bot is starting...")
# Only start polling if API_TOKEN is available
if API_TOKEN:
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error occurred: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except apihelper.ApiTelegramException as e:
            print(f"Telegram API error occurred: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"An unexpected error occurred: {e}. Retrying in 5 seconds...")
            time.sleep(5)
else:
    print("Bot not started due to missing API_TOKEN.")