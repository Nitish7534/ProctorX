# 🎓 ProctorX – AI-Based Online Examination & Proctoring System

## 🚀 Overview

**ProctorX** is an end-to-end online examination system integrated with **AI-based proctoring and feedback-driven monitoring**.
It is designed to ensure **secure, fair, and transparent remote examinations** by combining **computer vision, real-time monitoring, and explainable AI**.

Unlike traditional systems, ProctorX avoids black-box decisions by providing **interpretable feedback reports** to examiners.

---

## 🎯 Key Features

* 🔐 Secure User Authentication (Admin & Student)
* 📝 Online Exam Creation & Management
* ⏱️ Timed Examinations with Auto Submission
* 🎥 Real-Time AI-Based Proctoring
* 👁️ Face Detection & Tracking (OpenCV)
* 👀 Gaze Tracking & Suspicious Activity Detection
* 📊 Feedback-Based Monitoring (Explainable AI)
* 📄 Detailed Reports for Examiners
* 📈 Scalable & Modular Architecture

---

## 🧠 Unique Contribution

> 🔍 **Feedback-Oriented Monitoring (Explainable AI)**
> Instead of just flagging students, ProctorX provides:

* Reason for detection (e.g., face not visible, gaze deviation)
* Time-stamped logs
* Behavior summaries

This eliminates **black-box AI decisions** and improves **trust & fairness**.

---

## 🏗️ System Architecture

* **Frontend:** HTML, CSS, JavaScript
* **Backend:** Python (Flask)
* **Database:** MySQL
* **AI Module:** OpenCV, Machine Learning

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/ProctorX.git
cd ProctorX
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Setup Database

* Create a MySQL database
* Update DB credentials in config file

### 5️⃣ Run the Application

```bash
python app.py
```

👉 Open in browser:

```
http://127.0.0.1:5000
```

---

## 📂 Project Structure

```
ProctorX/
│── app.py
│── preprocess.py
│── helper.py
│── static/
│── templates/
│── database/
│── models/
│── requirements.txt
│── README.md
```

---

## 🛠️ How It Works

1. User logs in securely
2. Admin creates exam
3. Student starts exam
4. Webcam monitoring begins
5. AI detects:

   * Face presence
   * Gaze movement
   * Suspicious behavior
6. Feedback module generates:

   * Logs
   * Alerts with explanation
7. Examiner reviews report

---

## 📊 Advantages

* ✅ Reduces cheating in online exams
* ✅ No need for physical invigilators
* ✅ Transparent AI decisions
* ✅ Scalable for large institutions
* ✅ Cost-effective solution

---

## ⚠️ Limitations

* Requires stable internet connection
* Webcam quality affects accuracy
* Privacy concerns need policy handling

---

## 🔮 Future Scope

* 🎤 Voice-based monitoring
* 😊 Emotion detection
* ☁️ Cloud deployment (AWS)
* 📱 Mobile support
* 🔐 Blockchain-based exam logs

---

## 🤝 Contributing

Contributions are welcome!
Feel free to fork this repo and submit a pull request.

---

## 📜 License

This project is for academic and educational purposes.

---

## 👨‍💻 Author

**Nitish**
🎤 💻 MCA Student | 🚀 Tech Enthusiast

---

## ⭐ Support

If you like this project, please ⭐ star the repository!
