import grequests
from bs4 import BeautifulSoup
import pandas as pd
import nltk
import re
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize
nltk.download('punkt')
nltk.download('wordnet')

dataframe1 = pd.read_excel('Input.xlsx')
file_path= "C:\\Users\\rohit\\OneDrive\\Desktop\\BlackcofferAssignment\\Textfiles"

## Function to get URLs from the input Excel file
def get_urls(dataframe1):
    """
    This function takes a pandas DataFrame as input and returns a list of URLs from the 'URL' column.

    Args:
        dataframe1 (pandas.DataFrame): The input DataFrame containing the 'URL' column.

    Returns:
        list: A list of URLs.
    """
    urls = []
    for url in dataframe1['URL']:
        urls.append(url)
    return urls

## Function to fetch data from the URLs using grequests
def get_data(urls):
    """
    This function takes a list of URLs as input and fetches the data from those URLs using grequests.

    Args:
        urls (list): A list of URLs.

    Returns:
        list: A list of response objects from grequests.
    """
    reqs = [grequests.get(link) for link in urls]
    resp = grequests.map(reqs)
    return resp

## Function to get URL IDs from the input Excel file
def get_urlid(dataframe1):
    """
    This function takes a pandas DataFrame as input and returns a list of URL IDs from the 'URL_ID' column.

    Args:
        dataframe1 (pandas.DataFrame): The input DataFrame containing the 'URL_ID' column.

    Returns:
        list: A list of URL IDs.
    """
    urlid = []
    uid = dataframe1['URL_ID']

    for id in uid:
        file_name = id.strip("\'")
        urlid.append(file_name)
    return urlid

## Function to parse the data and save it to text files
def parse_data(resp, urlid, file_path):
    """
    This function takes the response objects from grequests, a list of URL IDs, and a file path as input.
    It parses the data from the response objects and saves the article title and text to text files.

    Args:
        resp (list): A list of response objects from grequests.
        urlid (list): A list of URL IDs.
        file_path (str): The file path where the text files will be saved.

    Returns:
        int: The number of exceptions encountered during parsing.
    """
    index = 0
    exception_cnt = 0
    for r in resp:
        try:
            doc = BeautifulSoup(r.text, 'html.parser')
            article_title = doc.find("h1").text
            article_text = doc.find("div", class_="td-post-content tagdiv-type").get_text(strip=True, separator='\n')

            file = open(f"{file_path}\\{urlid[index]}.txt", 'w+', encoding="utf-8")
            file.writelines(article_title)
            file.writelines(" ")
            file.writelines(article_text)
            file.close()

        except (AttributeError, UnicodeEncodeError) as error:
            file = open(f"{file_path}\\{urlid[index]}.txt", 'w+')
            file.writelines("None")
            file.close()
            exception_cnt += 1

        index += 1
    return exception_cnt

## Function to read stop words from text files
def read_stop_words():
    """
    This function reads stop words from multiple text files and returns a list of stop words.

    Returns:
        list: A list of stop words.
    """
    f1 = open(r"C:\Users\rohit\OneDrive\Desktop\BlackcofferAssignment\StopWords-20240324T102531Z-001\StopWords\StopWords_Auditor.txt", "r", encoding="utf-8")
    f2 = open(r"C:\Users\rohit\OneDrive\Desktop\BlackcofferAssignment\StopWords-20240324T102531Z-001\StopWords\StopWords_Currencies.txt", "r", encoding="utf-8")
    f3 = open(r"C:\Users\rohit\OneDrive\Desktop\BlackcofferAssignment\StopWords-20240324T102531Z-001\StopWords\StopWords_DatesandNumbers.txt", "r", encoding="utf-8")
    f4 = open(r"C:\Users\rohit\OneDrive\Desktop\BlackcofferAssignment\StopWords-20240324T102531Z-001\StopWords\StopWords_Generic.txt", "r", encoding="utf-8")
    f5 = open(r"C:\Users\rohit\OneDrive\Desktop\BlackcofferAssignment\StopWords-20240324T102531Z-001\StopWords\StopWords_GenericLong.txt", "r", encoding="utf-8")
    f6 = open(r"C:\Users\rohit\OneDrive\Desktop\BlackcofferAssignment\StopWords-20240324T102531Z-001\StopWords\StopWords_Geographic.txt", "r", encoding="utf-8")
    f7 = open(r"C:\Users\rohit\OneDrive\Desktop\BlackcofferAssignment\StopWords-20240324T102531Z-001\StopWords\StopWords_Names.txt", "r", encoding="utf-8")

    tsw = f1.read() + f2.read() + f3.read() + f4.read() + f5.read() + f6.read() + f7.read()
    tsw = re.sub(r'[^\w\s]', '', tsw)
    stopwords = nltk.word_tokenize(tsw)

    f1.close()
    f2.close()
    f3.close()
    f4.close()
    f5.close()
    f6.close()
    f7.close()

    return stopwords

## Function to read positive and negative words from text files
def read_positive_negative_words():
    """
    This function reads positive and negative words from text files and returns lists of positive and negative words.

    Returns:
        tuple: A tuple containing two lists: (negative_words, positive_words).
    """
    f8 = open(r"C:\Users\rohit\OneDrive\Desktop\BlackcofferAssignment\MasterDictionary-20240324T102549Z-001\MasterDictionary\negative-words.txt")
    f9 = open(r"C:\Users\rohit\OneDrive\Desktop\BlackcofferAssignment\MasterDictionary-20240324T102549Z-001\MasterDictionary\positive-words.txt")

    tnw = f8.read()
    tpw = f9.read()

    tnw = re.sub(r'[^\w\s]', '', tnw)
    tpw = re.sub(r'[^\w\s]', '', tpw)

    negative_words = nltk.word_tokenize(tnw)
    positive_words = nltk.word_tokenize(tpw)

    f8.close()
    f9.close()

    return negative_words, positive_words

## Function to clean the data
def clean_data(urlid, file_path, stopwords):
    """
    This function cleans the data by removing stop words, lemmatizing words, and calculating various metrics.

    Args:
        urlid (list): A list of URL IDs.
        file_path (str): The file path where the text files are located.
        stopwords (list): A list of stop words.

    Returns:
        tuple: A tuple containing the following lists:
            (clean_list, total_sentences, total_words, Avg_word_len, Personal_pronoun)
    """
    pronounRegex = re.compile(r'\b(I|we|my|ours|(?-i:us))\b', re.I)
    lemmetizer = WordNetLemmatizer()
    clean_list = []
    total_sentences = []
    total_words = []
    Avg_word_len = []
    Personal_pronoun = []

    for i in urlid:
        filter_sentence = []
        f = open(f"{file_path}\\{i}.txt", "r", encoding="utf-8")
        a = f.read()
        number_of_sentences = sent_tokenize(a)
        total_sentences.append(len(number_of_sentences))

        a = re.sub(r'[^\w\s]', '', a)
        words = nltk.word_tokenize(a)
        words = [w for w in words if w not in stopwords]

        for j in words:
            filter_sentence.append(lemmetizer.lemmatize(j))
        f_s = list(set(filter_sentence))

        sum_char = 0
        for char in f_s:
            sum_char += len(char)
        Avg_word_len.append(sum_char / len(f_s))

        pronouns = 0
        for i in f_s:
            pronouns += len(pronounRegex.findall(i))
        Personal_pronoun.append(pronouns)
        total_words.append(len(f_s))
        clean_list.append(f_s)
        f.close()

    return clean_list, total_sentences, total_words, Avg_word_len, Personal_pronoun

## Function to perform sentimental analysis
def sentimental_analysis(clean_list, negative_words, positive_words, total_words):
    """
    This function performs sentimental analysis on the cleaned data.

    Args:
        clean_list (list): A list of cleaned word lists.
        negative_words (list): A list of negative words.
        positive_words (list): A list of positive words.
        total_words (list): A list of total word counts.

    Returns:
        tuple: A tuple containing the following lists:
            (polarity_score, subjectivity_score, positive_score, negative_score)
    """
    negative_score = []
    positive_score = []
    for i in clean_list:
        negative_cnt = 0
        positive_cnt = 0
        for j in i:
            if j in negative_words:
                negative_cnt += 1
            elif j in positive_words:
                positive_cnt += 1
        negative_score.append(negative_cnt)
        positive_score.append(positive_cnt)

    polarity_score = []
    subjectivity_score = []
    for i in range(0, 100):
        ps = positive_score[i]
        ns = negative_score[i]

        pol_score = (ps - ns) / ((ps + ns) + 0.000001)
        polarity_score.append(pol_score)

        sub_score = (ps + ns) / ((total_words[i]) + 0.000001)
        subjectivity_score.append(sub_score)

    return polarity_score, subjectivity_score,positive_score, negative_score


## Function to analyze readability
def analyze_readability(clean_list, total_sentences, total_words):
    """
    This function analyzes the readability of the text by calculating various metrics.

    Args:
        clean_list (list): A list of cleaned word lists.
        total_sentences (list): A list of total sentence counts.
        total_words (list): A list of total word counts.

    Returns:
        tuple: A tuple containing the following lists:
            (Avg_sen_len, complex_word_count, syllable_count, per_com_words, Fox_index)
    """
    Avg_sen_len = []

    for i in range(0, 100):
        avg = total_words[i] / total_sentences[i]
        Avg_sen_len.append(avg)

    syllable_count = []
    complex_word_count = []
    for i in clean_list:
        syll_count = 0
        com_count = 0
        cnt = 0
        for word in i:
            vowels = 'aeiou'
            if word[0] in vowels:
                syll_count += 1
            for index in range(1, len(word)):
                if word[index] in vowels and word[index - 1] not in vowels:
                    syll_count += 1
            if word.endswith('e'):
                syll_count -= 1
            if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
                syll_count += 1
            if syll_count == 0:
                syll_count += 1
            if word.endswith('es') or word.endswith('ed'):
                syll_count -= 1
            if syll_count > 2:
                com_count += 1

        complex_word_count.append(com_count)
        syllable_count.append(int(syll_count / total_words[cnt]))
        cnt += 1

    per_com_words = []

    for i in range(0, 100):
        pcw = (complex_word_count[i] / total_words[i]) * 100
        per_com_words.append(pcw)

    Fog_index = []
    for i in range(0, 100):
        fog_ind = 0.4 * (Avg_sen_len[i] + per_com_words[i])
        Fog_index.append(fog_ind)

    return Avg_sen_len, complex_word_count, syllable_count, per_com_words, Fog_index

## Function to create a DataFrame and save it to CSV and Excel files
def create_dataframe(urlid, urls, positive_score, negative_score, polarity_score, subjectivity_score, Avg_sen_len,
                     per_com_words, Fog_index, total_words, complex_word_count, syllable_count, Personal_pronoun,
                     Avg_word_len):
    """
    This function creates a pandas DataFrame with the given data and saves it to CSV and Excel files.

    Args:
        urlid (list): A list of URL IDs.
        urls (list): A list of URLs.
        positive_score (list): A list of positive scores.
        negative_score (list): A list of negative scores.
        polarity_score (list): A list of polarity scores.
        subjectivity_score (list): A list of subjectivity scores.
        Avg_sen_len (list): A list of average sentence lengths.
        per_com_words (list): A list of percentages of complex words.
        Fog_index (list): A list of Fog index values.
        total_words (list): A list of total word counts.
        complex_word_count (list): A list of complex word counts.
        syllable_count (list): A list of syllable counts per word.
        Personal_pronoun (list): A list of personal pronoun counts.
        Avg_word_len (list): A list of average word lengths.
    """
    name_dict = {
        'URL_ID': urlid,
        'URL': urls,
        'POSITIVE SCORE': positive_score,
        'NEGATIVE SCORE': negative_score,
        'POLARITY SCORE': polarity_score,
        'SUBJECTIVITY SCORE': subjectivity_score,
        'AVG SENTENCE LENGTH': Avg_sen_len,
        'PERCENTAGE OF COMPLEX WORDS': per_com_words,
        'FOG INDEX': Fog_index,
        'AVG NUMBER OF WORDS PER SENTENCE': Avg_sen_len,
        'COMPLEX WORD COUNT': complex_word_count,
        'WORD COUNT': total_words,
        'SYLLABLE PER WORD': syllable_count,
        'PERSONAL PRONOUNS': Personal_pronoun,
        'AVG WORD LENGTH': Avg_word_len
    }

    df = pd.DataFrame(name_dict)

    df.to_csv(r'C:\Users\rohit\OneDrive\Desktop\BlackcofferAssignment\Output\Output_struct.csv', index=False)

    read_file = pd.read_csv(r'C:\Users\rohit\OneDrive\Desktop\BlackcofferAssignment\Output\Output_struct.csv')
    read_file.to_excel(r'C:\Users\rohit\OneDrive\Desktop\BlackcofferAssignment\Output\Output_Data_Structur.xlsx', index=False, header=True)



# Define the main method to run the code
def main():
    # Load your Excel file into a pandas DataFrame
    dataframe = pd.read_excel('Input.xlsx')

    # Get URLs from the input Excel file
    urls = get_urls(dataframe)

    # Fetch data from the URLs using grequests
    responses = get_data(urls)

    # Get URL IDs from the input Excel file
    url_ids = get_urlid(dataframe)

    # Parse the data and save it to text files
    exceptions = parse_data(responses, url_ids, file_path)
    print(exceptions)

    # Read stop words from text files
    stopwords = read_stop_words()

    # Read positive and negative words from text files
    negative_words, positive_words = read_positive_negative_words()

    # Clean the data
    clean_data_list, total_sentences, total_words, avg_word_len, personal_pronoun = clean_data(url_ids, file_path, stopwords)

    # Perform sentimental analysis
    polarity_scores, subjectivity_scores, positive_scores, negative_scores = sentimental_analysis(clean_data_list, negative_words, positive_words, total_words)

    # Analyze readability
    avg_sentence_len, complex_word_count, syllable_count, per_complex_words, fog_index = analyze_readability(clean_data_list, total_sentences, total_words)

    # Create a DataFrame and save it to CSV and Excel files
    create_dataframe(url_ids, urls, positive_scores, negative_scores, polarity_scores, subjectivity_scores, avg_sentence_len, per_complex_words, fog_index, total_words, complex_word_count, syllable_count, personal_pronoun, avg_word_len)

# Call the main method to execute the code
if __name__ == "__main__":
    main()