import joblib
import sklearn
import pandas
# Load the saved model and LabelEncoder
def predict_value(values):
    svc_model = joblib.load('./data/svc_model.pkl')
    le = joblib.load('./data/label_encoder.pkl')

    # Manually input a sample with the same number of features as X_train
    manual_input = values#[[0, 1, 2, 2, 1, 0, 2, 1, 1, 0, 2, 0, 1, 2, 1, 0, 0, 1, 0, 1, 0, 2, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0]]  # Replace these values with appropriate features

    # Predict the label for this manually input sample
    predicted_label = svc_model.predict(manual_input)

    # Decode the predicted label back to the original class (if using LabelEncoder)
    predicted_class = le.inverse_transform(predicted_label)

    # Print the predicted class for the manually entered sample
    print(f"Predicted label for the manually entered sample: {predicted_class[0]}")
    return (predicted_class[0])
