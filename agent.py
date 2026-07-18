import json
import speech_recognition as sr
from groq import Groq
import asyncio
import edge_tts
import pygame
import os
import time
import warnings
import datetime
from dotenv import load_dotenv
from ddgs import DDGS

warnings.filterwarnings("ignore")

# ============================================================
# إعدادات Groq
# ============================================================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("[ERROR] مفيش GROQ_API_KEY! حط المفتاح في ملف .env")

groq_client = Groq(api_key=GROQ_API_KEY)

print("[WAIT] بنجهز النظام...")
pygame.mixer.init()
print("[OK] النظام جاهز (Groq + Edge-TTS بصوت سلمى الهادي)!")

# ================= الذاكرة =================
conversation_history = []

# ================= دالة النطق (صوت طبيعي هادي وجاهز) =================
def speak_text(text):
    audio_file = "temp_response.mp3"
    
    async def _generate_audio():
        # الصوت هنا سلمى، وبطأنا السرعة 10% عشان يبان طبيعي ومش مستعجل
        communicate = edge_tts.Communicate(
            text=text, 
            voice="ar-EG-SalmaNeural", 
            rate="-10%",
            pitch="+0Hz"
        )
        await communicate.save(audio_file)
    
    asyncio.run(_generate_audio())
    
    try:
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"[ERROR] خطأ في تشغيل الصوت: {e}")
    finally:
        pygame.mixer.music.unload()
        time.sleep(0.1) 
        if os.path.exists(audio_file):
            try:
                os.remove(audio_file)
            except:
                pass

# ================= دالة الاستماع =================
def listen_and_transcribe():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 200 
    recognizer.dynamic_energy_threshold = False 
    recognizer.pause_threshold = 2.0 
    recognizer.non_speaking_duration = 0.8 

    with sr.Microphone() as source:
        print("\n[LIVE] تحدث الآن، أنا أستمع...")
        audio = recognizer.listen(source, timeout=None, phrase_time_limit=30)

    try:
        text = recognizer.recognize_google(audio, language="ar-EG")
        print(f"إنت قلت: {text}")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        print("[ERROR] مشكلة في الاتصال بالإنترنت!")
        return ""

# ================= أداة البحث الذكية =================
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        if not results:
            return "لا توجد نتائج."
        summary = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
        return summary
    except Exception as e:
        return "حدث خطأ في البحث."

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Use this tool to search the web for current news, sports match results, or any information you don't know. DO NOT use this tool if the user is just greeting you.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query in Arabic language (e.g., 'أين يلعب ميسي الآن؟')",
                    }
                },
                "required": ["query"],
            },
        },
    }
]

# ================= دالة الرد =================
def chat_and_get_response(user_text):
    global conversation_history
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    system_prompt = (
        f"Today's date is {current_date}. "
        "You are a smart and helpful assistant. "
        "CRITICAL INSTRUCTION: You MUST reply ONLY in clear Arabic language (اللغة العربية الفصحى). "
        "Do NOT use Egyptian slang in your response. Keep your answers very short and direct. "
        "If the user greets you, greet them back in Arabic without using any tools."
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_text})

    print("رد الذكاء الاصطناعي: ", end="", flush=True)

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.3
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            messages.append(response_message) 
            
            for tool_call in tool_calls:
                function_args = json.loads(tool_call.function.arguments)
                search_query = function_args.get("query")
                print(f"\n[SEARCH] الموديل قرر يبحث في النت عن: {search_query}...")
                
                search_result = search_web(search_query)
                
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_call.function.name,
                    "content": search_result,
                })
            
            final_response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.3
            )
            full_response = final_response.choices[0].message.content
            
        else:
            full_response = response_message.content

        print(full_response)

        conversation_history.append({"role": "user", "content": user_text})
        conversation_history.append({"role": "assistant", "content": full_response})

        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]

        if full_response.strip():
            speak_text(full_response)

    except Exception as e:
        print(f"\n[ERROR] مشكلة: {e}")

# ================= دورة التشغيل =================
while True:
    try:
        user_text = listen_and_transcribe()
        if not user_text or len(user_text) < 2:
            continue
        if "سلام" in user_text or "وداعاً" in user_text:
            print("إلى اللقاء!")
            pygame.mixer.quit()
            break
        chat_and_get_response(user_text)
    except KeyboardInterrupt:
        print("\nتم إغلاق البرنامج. إلى اللقاء!")
        pygame.mixer.quit()
        break
    except Exception as e:
        print(f"[ERROR] {e}")
        continue
