# Readability.Lib 📚

> **A New Generation Accessible Library**

Readability.Lib is an innovative platform designed to engage the new generation with reading. Recognizing the preference for fast content consumption, our story formats are designed to be read in **1-2 minutes**, accompanied by AI-generated imagery and full accessibility features.

## 🚀 Overview

The project leverages cutting-edge AI (Gemini, OpenAI, and our fine-tuned model "Ozi") to create immersive storytelling experiences. We prioritize accessibility using Google Cloud's Text-to-Speech and Speech-to-Text APIs, ensuring stories are available to everyone.

**Key Objectives:**
* **Fast Consumption:** Bite-sized stories for modern attention spans.
* **Visual Immersion:** Every story is paired with context-aware AI imagery.
* **Interactivity:** Users become players in the story.
* **Accessibility:** Full audio support for reading and navigation.

---

## 🛠 Tech Stack

We utilize a robust stack of modern AI and security technologies:

* **Generative AI:** Google Gemini 1.5 Pro, OpenAI, and "Ozi" (Fine-tuned model).
* **Image Generation:** Hugging Face Text-to-Image models.
* **Accessibility:** Google Cloud Text-to-Speech (TTS) & Speech-to-Text (STT).
* **Database:** SQLite3 (History management & storage).
* **Security:** Fernet Encryption (Messaging) & OTP Email Verification.

---

## 🌟 Key Features

### 📖 Immersive Storytelling
* **Short Stories:** curated 1-2 minute reads.
* **Interactive Mode:** Powered by **Gemini 1.5 Pro**, users can roleplay within stories (e.g., inside the Harry Potter universe).
* **PDF Extractor:** Upload PDFs and convert them into enjoyable, readable formats.

### 🔒 Security & Authentication
* **Encrypted Storage:** Passwords are hashed and stored securely.
* **OTP Verification:** Mandatory email verification via One-Time Password to ensure user authenticity.
* **Secure Messaging:** Real-time messaging encrypted using **Fernet**.

### 🤝 Community
* **Forums:** A space for users to share their stories and discuss plots.
* **Interactive Sharing:** A lively environment for story lovers to enhance creativity.



## 📸 Gallery

### User Interface
| Landing Page | Main Page |
|:---:|:---:|
| ![Landing](https://github.com/ArifKuru/ReadabilityLib/assets/125080971/d42eadb8-fecd-495c-a4da-e410e6b5809d) | ![Main](https://github.com/ArifKuru/Readability.Lib/assets/125080971/79e0ddc1-2f72-4ac2-9478-23df5621bd7c) |

### Authentication
| Login | Register |
|:---:|:---:|
| ![Login](https://github.com/ArifKuru/ReadabilityLib/assets/125080971/94446d78-bd1b-4a8b-a57c-428c64dda0b1) | ![Register](https://github.com/ArifKuru/ReadabilityLib/assets/125080971/5184c1e9-c6b1-4565-8f69-9e0fe8191155) |

### Interactive Stories & Games
*Roleplay as characters using Gemini 1.5 Pro context handling.*

![Harry Potter Game](https://github.com/ArifKuru/ReadabilityLib/assets/125080971/b1702021-43d6-4605-a8ee-fffb36337f5f)
![Game Choice](https://github.com/ArifKuru/ReadabilityLib/assets/125080971/5f983902-7f15-4a86-a02c-5c8bcbf9dd92)

### Tools & Social
**PDF Extraction**
![PDF Tool](https://github.com/ArifKuru/ReadabilityLib/assets/125080971/7ca49a49-bfe2-4d57-9d54-e183512c924c)

**Encrypted Messaging**
![Messaging](https://github.com/ArifKuru/Readability.Lib/assets/125080971/866d4eb5-1ae6-4879-bf7c-43316b96b9e6)

---

---

## 🧩 Summary 
<p align="center">

<img
  src="https://github.com/ArifKuru/Readability.Lib/assets/125080971/46431bbc-4fe5-4f2b-bdc1-dd9756b24de3"
  alt="Summary"
  width="800"
/>
</p>
---

## ✅ Roadmap & To-Do

- [ ] Refactor OTP handling: Move definition out of the global scope for better security practices.
- [ ] Expand the forum features for better user interaction.
- [ ] Optimization of image generation latency.
