import re
from typing import List
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


class TextParser:
    """Парсер для английских слов из текста"""
    def __init__(self):
        self.word_pattern = re.compile(r'\b[a-zA-Z]+\b')
        self.timeout = 5

    def extract_words(self, text: str) -> List[str]:
        """Извлекает английские слова"""
        words = self.word_pattern.findall(text)
        filtered_words = [
                word.lower() for word in words
                if len(word) >= 2 and word.isalpha()
                ]
        unique_words = list(set(filtered_words))
        return unique_words

    def parser_url(self, url:str) -> List[str]:
        """Парсит веб-страницу"""
        try:
            if not self._is_valid_url(url):
                raise ValueError("Некорректный URL")

            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            text = self._extract_clean_text(soup)
            return self.extract_words(text)
        except requests.RequestException as e:
            print(f"Ошибка при запросе к url: {e}")
            return []
        except Exception as e:
            print(f"Ошибка при парсинге: {e}")
            return []

    def _is_valid_url(self, url: str) -> bool:
        """Проверяет, является ли строка валидным url"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def _extract_clean_text(self, soup: BeautifulSoup) -> str:
        """Извлекает чистый текст из HTML, игнорируя скрипты и стили"""
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()

        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        return text
