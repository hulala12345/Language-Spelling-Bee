import json
import os
import random
from datetime import datetime, UTC
from collections import defaultdict

DATA_FILE = os.path.join('data', 'words.json')
PROGRESS_FILE = os.path.join('progress', 'history.json')

class WordDatabase:
    def __init__(self, path=DATA_FILE):
        with open(path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def languages(self):
        return list(self.data.keys())

    def difficulties(self, language):
        return list(self.data.get(language, {}).keys())

    def topics(self, language, difficulty):
        return list(self.data.get(language, {}).get(difficulty, {}).keys())

    def get_words(self, language, difficulty, topic):
        return self.data.get(language, {}).get(difficulty, {}).get(topic, [])

class ProgressTracker:
    def __init__(self, path=PROGRESS_FILE):
        self.path = path
        if os.path.exists(self.path):
            with open(self.path, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
        else:
            self.history = []

    def add_record(self, language, difficulty, topic, word, correct):
        self.history.append({
            'timestamp': datetime.now(UTC).isoformat(),
            'language': language,
            'difficulty': difficulty,
            'topic': topic,
            'word': word,
            'correct': correct
        })
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2)

    def stats(self):
        stats = defaultdict(lambda: {'correct': 0, 'total': 0})
        for record in self.history:
            key = (record['language'], record['difficulty'], record['topic'])
            stats[key]['total'] += 1
            if record['correct']:
                stats[key]['correct'] += 1
        return stats

    def display_summary(self):
        stats = self.stats()
        if not stats:
            print('No progress yet.')
            return
        print('\nProgress Summary:')
        for (lang, diff, topic), s in stats.items():
            rate = 100 * s['correct'] / s['total'] if s['total'] else 0
            bar = '#' * int(rate / 10)
            print(f'{lang} / {diff} / {topic}: {s["correct"]}/{s["total"]} ({rate:.1f}%) {bar}')

class SpellingBeeApp:
    def __init__(self):
        self.db = WordDatabase()
        self.tracker = ProgressTracker()

    def run(self):
        print('Welcome to the Language Spelling Bee!')
        language = self.choose_option('Select language', self.db.languages())
        difficulty = self.choose_option('Select difficulty', self.db.difficulties(language))
        topic = self.choose_option('Select topic', self.db.topics(language, difficulty))
        words = self.db.get_words(language, difficulty, topic)
        random.shuffle(words)
        for entry in words:
            self.ask_word(language, difficulty, topic, entry)
        self.tracker.display_summary()

    def choose_option(self, message, options):
        while True:
            print('\n' + message + ':')
            for i, opt in enumerate(options, 1):
                print(f'{i}. {opt}')
            choice = input('Enter number: ')
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                return options[int(choice)-1]
            print('Invalid choice.')

    def ask_word(self, language, difficulty, topic, entry):
        definition = entry['definition']
        correct_spelling = entry['word']
        print(f"\nDefinition: {definition}")
        user_input = input('Spell the word: ').strip()
        if user_input.lower() == correct_spelling.lower():
            print('Correct!')
            self.tracker.add_record(language, difficulty, topic, correct_spelling, True)
        else:
            print(f'Incorrect. Correct spelling: {correct_spelling}')
            self.tracker.add_record(language, difficulty, topic, correct_spelling, False)

if __name__ == '__main__':
    app = SpellingBeeApp()
    app.run()
