import csv
import random

# All survey questions with their options
general_questions = [
    {"question": "What is your gender?", "options": ["Male", "Female", "Prefer not to say"]},
    {"question": "What is your age group?", "options": ["<18", "18-24", "25-34", "35-44", "45-54", "55+"]},
    {"question": "What is your highest level of education?",
     "options": ["No formal education", "Primary", "Secondary", "Bachelor's", "Master's", "Doctorate"]},
    {"question": "Which region do you live in?",
     "options": ["North America", "Europe", "Asia", "South America", "Africa", "Australia/Oceania"]},
    {"question": "Do you live in an urban or rural area?", "options": ["Urban", "Rural"]},
    {"question": "What is your employment status?", "options": ["Employed", "Unemployed", "Student", "Retired"]},
    {"question": "What is your monthly income?",
     "options": ["< $500", "$500-$1000", "$1,000-$3,000", "$3,000+", "Prefer not to say"]},
    {"question": "Do you enjoy music with strong bass frequencies?", "options": ["Yes", "No", "Neutral"]},
    {"question": "Do you prefer vocals or instrumental music?", "options": ["Vocals", "Instrumental", "Both"]},
    {"question": "What time of day do you usually listen to music?",
     "options": ["Morning", "Afternoon", "Evening", "Night"]},
    {"question": "What is the most important factor in your music preference?",
     "options": ["Genre", "Mood", "Lyrics", "Beats", "Other"]},
    {"question": "Which platform do you primarily use to listen to music?",
     "options": ["Spotify", "Apple Music", "YouTube", "Yandex Music", "Other"]},
    {"question": "What device do you use most often for listening to music?",
     "options": ["Phone", "Laptop", "Smart Speakers", "Earphones", "Other"]},
    {"question": "What are your top 3 favorite music genres?",
     "options": ["Pop", "Rock", "Jazz", "Hip-Hop", "Classical", "EDM", "Country", "Reggae", "Blues", "Metal", "Folk",
                 "Other"]},
    {"question": "Do you prefer music with high energy (fast, upbeat), low energy (slow, calming), or mid-range?",
     "options": ["High energy", "Low energy", "Mid-range"]},
    {"question": "How do you usually discover new music?",
     "options": ["Recommendations", "Social Media", "Friends", "Radio", "Movies", "Other"]},
    {"question": "How does music usually affect your emotions?",
     "options": ["Lifts my mood", "Helps me relax", "Makes me feel energetic", "Makes me nostalgic", "Helps me focus",
                 "Other"]},
    {"question": "What factors make a music recommendation good for you?",
     "options": ["Matching mood", "Discovering new genres", "Fitting current activities", "Introducing unique sounds",
                 "Ease of access", "Other"]},
    {"question": "Do you usually listen to music alone or with others?",
     "options": ["Alone", "With others", "Both equally"]},
    {"question": "Do you change your music preferences based on your mood?", "options": ["Yes", "No", "Sometimes"]},
    {"question": "How do you usually listen to music: for nostalgia or creating new experiences?",
     "options": ["Nostalgia", "New experiences", "Both"]},
    {"question": "What is your primary reason for listening to music?",
     "options": ["Entertainment", "Relaxation", "Focus", "Emotional connection", "Background noise"]}
]

# Songs across frequency ranges
songs = {
    "bass": ["Bass Song 1: Bad Guy by Billie Eilish", "Bass Song 2: God's plan by Drake",
             "Bass Song 3: Bangarang by Skrillex"],
    "midrange": ["Midrange Song 1: Rolling in the deep by Adele", "Midrange Song 2: Yellow by Coldplay",
                 "Midrange Song 3: Shape of you by Ed Sheeran"],
    "treble": ["Treble Song 1: Symphony No. 40 by Mozart", "Treble Song 2: Love Story by Taylor Swift",
               "Treble Song 3: Billie Jean by Michael Jackson"]
}


# Generate mock data
def generate_mock_data(num_users):
    data = []
    for user_id in range(1, num_users + 1):
        # General survey responses
        general_responses = [random.choice(question["options"]) for question in general_questions]

        # Big Five Personality Test scores
        big_five_scores = {
            "Extraversion": random.randint(0, 50),
            "Agreeableness": random.randint(0, 50),
            "Conscientiousness": random.randint(0, 50),
            "Neuroticism": random.randint(0, 50),
            "Openness": random.randint(0, 50)
        }

        # Song ratings (1-5)
        song_ratings = {song: random.randint(1, 5) for category in songs.values() for song in category}

        # Combine into a row
        row = [user_id] + general_responses + list(big_five_scores.values()) + list(song_ratings.values())
        data.append(row)
    return data


# Save to CSV
def save_mock_data_to_csv(data, filename="mock_survey_data.csv"):
    # Prepare the header
    header = (
            ["User ID"] + [q["question"] for q in general_questions] +
            ["Extraversion", "Agreeableness", "Conscientiousness", "Neuroticism", "Openness"] +
            [song for category in songs.values() for song in category]
    )

    # Write to CSV
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)


# Generate and save mock data
num_users = 50000  # Adjust for desired number of users
mock_data = generate_mock_data(num_users)
save_mock_data_to_csv(mock_data)

print(f"Mock data for {num_users} users saved to 'mock_survey_data.csv'")



