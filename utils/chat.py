from flask import session
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def get_chat_response(user_message, detection_result=None):
    try:
        # Inisialisasi session
        if 'conversation_history' not in session:
            session['conversation_history'] = []
        if 'detection_history' not in session:
            session['detection_history'] = []

        # Simpan deteksi terbaru sebagai dict (tanpa summary)
        if detection_result and isinstance(detection_result, dict):
            session['detection_history'].append(detection_result)
            # Batasi max 5 deteksi terakhir
            session['detection_history'] = session['detection_history'][-5:]
            session.modified = True

        # Batasi conversation history max 10
        session['conversation_history'] = session['conversation_history'][-10:]

        # System prompt
        system_prompt = """
        Role: You are an expert agricultural assistant specializing in rice leaf conditions.
        - You are ONLY allowed to identify rice leaf conditions as one of these five classes: Healthy, Bacterial Blight, Blast, Brown Spot, or Tungro.
        - Any condition or disease outside these five classes (such as neck blast or others) MUST NOT be discussed. 
        - If a user asks about a condition outside this scope, state that it is beyond the system’s capability.

        Guidelines:
        - Focus only on rice leaf conditions: healthy leaves or diseases including Bacterial Blight, Blast, Brown Spot, and Tungro.
        - Explain the detected condition:
          - If disease → describe symptoms, causes, prevention, early detection, and initial management.
          - If healthy → confirm no visible disease and provide monitoring tips and good practices.
        - Always mention AI detection is preliminary and must be confirmed by a qualified agricultural expert.
        - Do not answer questions unrelated to rice leaf health.
        - Keep responses concise, clear, and easy to understand.
        """

        messages = [{"role": "system", "content": system_prompt}]

        # Masukkan setiap deteksi sebagai sistem message
        for det in session['detection_history']:
            # konversi dict ke string langsung di sini
            det_message = f"Detection result: Type={det.get('label', 'Unknown')}, Confidence={det.get('confidence', 0)*100:.1f}%, Status={det.get('validation_status', 'unknown')}"
            messages.append({"role": "system", "content": det_message})

        # Tambahkan conversation history
        messages.extend(session['conversation_history'])

        # Tambahkan pesan user
        messages.append({"role": "user", "content": user_message})

        # Panggil GPT
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=500,  # lebih aman
            temperature=0.5
        )

        assistant_response = response.choices[0].message.content.strip()

        # Update conversation history
        session['conversation_history'].append({"role": "user", "content": user_message})
        session['conversation_history'].append({"role": "assistant", "content": assistant_response})
        session.modified = True

        return assistant_response

    except Exception as e:
        print(f"Error in get_chat_response: {str(e)}")
        return "Maaf, terjadi kesalahan dalam sistem. Silakan coba lagi nanti."





