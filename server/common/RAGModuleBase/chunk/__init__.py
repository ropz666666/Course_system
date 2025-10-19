from abc import ABC, abstractmethod
import re
from collections import Counter
import string

import markdown
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize

# Define the abstract base class for chunking strategies
class ChunkingStrategy(ABC):
    @abstractmethod
    def chunk(self, text: str) -> list:
        """
        Abstract method to chunk the given text.
        """
        pass

# Regex-based chunking
class RegexChunking(ChunkingStrategy):
    def __init__(self, patterns=None, **kwargs):
        if patterns is None:
            patterns = [r'\n\n']  # Default split pattern
        self.patterns = patterns

    def chunk(self, text: str) -> list:
        paragraphs = [text]
        for pattern in self.patterns:
            new_paragraphs = []
            for paragraph in paragraphs:
                new_paragraphs.extend(re.split(pattern, paragraph))
            paragraphs = new_paragraphs
        return paragraphs


class MarkdownChunkingStrategy:
    def __init__(self, patterns=None, **kwargs):
        if patterns is None:
            patterns = [r'\n\n']
        self.patterns = patterns

    def chunk(self, text: str) -> list:
        # 将Markdown文本转换为HTML
        html = markdown.markdown(text)

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html, 'html.parser')

        # 提取所有标题
        headers = []
        for i in range(1, 7):  # h1 to h6
            headers.extend(soup.find_all(f'h{i}'))

        # 提取所有段落
        paragraphs = soup.find_all('p')

        # 提取所有列表
        lists = soup.find_all(['ul', 'ol'])

        # 结构化结果
        structured_content = {
            'headers': [header.text for header in headers],
            'paragraphs': [para.text for para in paragraphs],
            'lists': [[item.text for item in list_.find_all('li')] for list_ in lists]
        }

        return structured_content['paragraphs']


# Topic-based segmentation using TextTiling
class TopicSegmentationChunking(ChunkingStrategy):
    def __init__(self, num_keywords=3, **kwargs):
        import nltk as nl
        self.tokenizer = nl.toknize.TextTilingTokenizer()
        self.num_keywords = num_keywords

    def chunk(self, text: str) -> list:
        # Use the TextTilingTokenizer to segment the text
        segmented_topics = self.tokenizer.tokenize(text)
        return segmented_topics

    def extract_keywords(self, text: str) -> list:
        # Tokenize and remove stopwords and punctuation
        import nltk as nl
        tokens = nl.toknize.word_tokenize(text)
        tokens = [token.lower() for token in tokens if token not in nl.corpus.stopwords.words('english') and token not in string.punctuation]

        # Calculate frequency distribution
        freq_dist = Counter(tokens)
        keywords = [word for word, freq in freq_dist.most_common(self.num_keywords)]
        return keywords

    def chunk_with_topics(self, text: str) -> list:
        # Segment the text into topics
        segments = self.chunk(text)
        # Extract keywords for each topic segment
        segments_with_topics = [(segment, self.extract_keywords(segment)) for segment in segments]
        return segments_with_topics

# Fixed-length word chunks
class FixedLengthWordChunking(ChunkingStrategy):
    def __init__(self, chunk_size=100, **kwargs):
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list:
        words = text.split()
        return [' '.join(words[i:i + self.chunk_size]) for i in range(0, len(words), self.chunk_size)]

# Sliding window chunking
class SlidingWindowChunking(ChunkingStrategy):
    def __init__(self, window_size=100, step=50, **kwargs):
        self.window_size = window_size
        self.step = step

    def chunk(self, text: str) -> list:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.step):
            chunks.append(' '.join(words[i:i + self.window_size]))
        return chunks


# Factory class for chunking strategies
class FileChunking:
    @staticmethod
    def create_strategy(strategy_type, **kwargs):
        if strategy_type == "regex":
            return RegexChunking(**kwargs)
        elif strategy_type == "topic":
            return TopicSegmentationChunking(**kwargs)
        elif strategy_type == "fixed_length":
            return FixedLengthWordChunking(**kwargs)
        elif strategy_type == "sliding_window":
            return SlidingWindowChunking(**kwargs)
        elif strategy_type == "markdown_chunking":
            return MarkdownChunkingStrategy(**kwargs)
        else:
            raise ValueError("Unsupported chunking strategy type")

# # 使用示例
# text = "Your text here."
#
# # 创建不同的分块策略
# regex_chunking = FileChunking.create_strategy("regex", patterns=[r'\n\n'])
# topic_chunking = FileChunking.create_strategy("topic", num_keywords=3)
# fixed_length_chunking = FileChunking.create_strategy("fixed_length", chunk_size=100)
# sliding_window_chunking = FileChunking.create_strategy("sliding_window", window_size=100, step=50)
#
# # 使用策略对文本进行分块
# print(regex_chunking.chunk(text))
# print(topic_chunking.chunk(text))
# print(fixed_length_chunking.chunk(text))
# print(sliding_window_chunking.chunk(text))
