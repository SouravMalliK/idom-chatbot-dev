#install and import for idiom use accuracy
from fuzzywuzzy import process, fuzz, utils


#install and import for spelling use accuracy
from spellchecker import SpellChecker
spell = SpellChecker()

#install and import for grammar accuracy
import language_tool_python
tool = language_tool_python.LanguageTool('en-IN')

#install and import for sentiment score
import nltk
nltk.download('punkt')
nltk.download('vader_lexicon') 
from nltk.sentiment.vader import SentimentIntensityAnalyzer


def idiom_accuracy_score(input_text, comparing_idiom):
    string_matched = fuzz.partial_ratio(input_text, comparing_idiom)
    if string_matched > 50:
        print("Idiom accuracy:", string_matched, "%")
    else:
        print("poor accuracy of idiom")
    return 0


def spell_accuracy_score(input_text):
    number_of_words = len(input_text.split())

    # find those words that may be misspelled
    misspelled = spell.unknown(nltk.word_tokenize(input_text))

    accuracy = (number_of_words - len(misspelled)) / number_of_words
    print("number of misspelled words:", len(misspelled))
    if len(misspelled) > 0:
        print("words misspelled: ", misspelled)
    return print("spelling accuracy:", accuracy)


def grammar_accuracy_score(input_text):
    matches = tool.check(input_text)
    
    # prints total mistakes which are found from the document
    print("No. of mistakes found in document is ", len(matches))
    print()

    # prints mistake one by one
    for mistake in matches:
        print(mistake)
        print()

    return 0


def sentiment_score(input_text):
    sid = SentimentIntensityAnalyzer()
    sent_score = sid.polarity_scores(input_text)
    return print("sentiment score is:", sent_score['compound'])

if __name__ == '__main__':
    input_string = input("Enter the answer: ")
    target_idiom = input("Enter the target idiom: ")
    idiom_accuracy_score(input_string, target_idiom)
    print("--------------")
    spell_accuracy_score(input_string)
    print("--------------")
    grammar_accuracy_score(input_string)
    print("--------------")
    sentiment_score(input_string)

