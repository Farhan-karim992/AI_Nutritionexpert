import google.generativeai as genai

genai.configure(
    api_key="AIzaSyCMBejNBcvN5Jnqm-DPYlXx9rekVFhc6PE"
)

print(genai.list_models())