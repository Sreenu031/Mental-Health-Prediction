# Mental-Health-Prediction

This project aims to address mental health issues by developing a web-based platform that helps organizations assess and support individuals based on their mental health conditions. The system utilizes machine learning to predict mental health conditions and provides timely recommendations for further care.

## Key Features

- **Machine Learning Integration**: Uses a Support Vector Machine (SVM) model to classify mental health conditions (Mild, Moderate, Serious) based on responses to a 30-question mental health assessment.
- **Personalized Precautions and Recommendations**: Displays specific precautions based on the test results, offering tailored guidance to individuals.
- **Doctor Recommendation System**: 
  - Suggests nearby doctors based on location.
  - Matches individuals with top-rated doctors for serious conditions and other suitable doctors for moderate conditions.
- **Web Interface**: 
  - Built using HTML and Tailwind CSS for a responsive and user-friendly interface.
  - Enables students to take the test and view their results.
- **Backend and Database**: 
  - Developed with Python Flask for the server-side.
  - Connected to an SQL database to manage user data, test results, and doctor details.

## Technologies Used

1. **Machine Learning**: SVM model for mental health condition prediction.
2. **Frontend**: HTML and Tailwind CSS for the web interface.
3. **Backend**: Python Flask server for handling requests and processing data.
4. **Database**: SQL for storing test results, user information, and doctor details.

## How It Works

- **User Assessment**: 
  - Students log in through the platform and complete a mental health assessment comprising 30 questions.
- **Prediction and Results**: 
  - The SVM model processes the responses to predict the condition and assigns a category (Mild, Moderate, Serious).
- **Precaution Display**: 
  - Depending on the condition, specific precautionary measures are shown on the results page.
- **Doctor Recommendations**: 
  - Based on the user's location and condition severity, the system recommends suitable doctors from the database.

## Project Motivation

The project aims to provide accessible mental health support by leveraging AI to identify at-risk individuals and connecting them to appropriate care resources, especially in educational settings.
