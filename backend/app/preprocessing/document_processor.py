"""
GENIQ - Educational Document & PDF Chunking Pipeline
===================================================
Handles PDF document text extraction, cleaning, header/footer stripping,
and intelligent semantic chunking for question generation.
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Processes educational texts and PDFs into grounded chunks."""

    def __init__(self, target_chunk_words: int = 250, chunk_overlap_words: int = 40):
        self.target_chunk_words = target_chunk_words
        self.chunk_overlap_words = chunk_overlap_words

    def extract_text_from_pdf(self, pdf_bytes_or_path: Any) -> Dict[str, Any]:
        """
        Extracts structured text from a PDF file using PyMuPDF (fitz).
        Handles page numbers, header/footer repetition, and metadata.
        """
        try:
            if isinstance(pdf_bytes_or_path, (bytes, bytearray)):
                doc = fitz.open(stream=pdf_bytes_or_path, filetype="pdf")
            else:
                doc = fitz.open(pdf_bytes_or_path)

            pages_content = []
            full_text_list = []

            total_pages = len(doc)
            for page_num in range(total_pages):
                page = doc[page_num]
                text = page.get_text("text")
                cleaned_page_text = self._clean_page_text(text)
                if cleaned_page_text:
                    pages_content.append({
                        "page_number": page_num + 1,
                        "text": cleaned_page_text
                    })
                    full_text_list.append(cleaned_page_text)

            doc.close()

            full_text = "\n\n".join(full_text_list)
            is_scanned = len(full_text.strip()) < 50 and total_pages > 0

            return {
                "success": True,
                "total_pages": total_pages,
                "is_scanned": is_scanned,
                "full_text": full_text,
                "pages": pages_content,
                "error": None if not is_scanned else "Document appears to be scanned or contains non-extractable text."
            }
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return {
                "success": False,
                "total_pages": 0,
                "is_scanned": False,
                "full_text": "",
                "pages": [],
                "error": str(e)
            }

    def _clean_page_text(self, text: str) -> str:
        """Removes standalone page numbers, redundant linebreaks, and header noise."""
        lines = text.splitlines()
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            # Ignore empty lines or simple lone page numbers
            if not stripped or re.match(r"^Page \d+ of \d+$|^\d+$", stripped, re.IGNORECASE):
                continue
            cleaned_lines.append(stripped)
        return " ".join(cleaned_lines)

    def chunk_text(self, text: str, source_reference: str = "custom_document") -> List[Dict[str, Any]]:
        """
        Chunks text into approximately 200-350 word passages with overlap,
        respecting sentence boundaries where possible.
        """
        cleaned = re.sub(r"\s+", " ", text).strip()
        if not cleaned:
            return []

        # Split into sentences roughly
        sentences = re.split(r"(?<=[.!?]) +", cleaned)
        chunks = []
        current_chunk_sentences = []
        current_word_count = 0
        chunk_idx = 1

        for sentence in sentences:
            sentence_words = len(sentence.split())
            if current_word_count + sentence_words > self.target_chunk_words and current_chunk_sentences:
                chunk_text_str = " ".join(current_chunk_sentences)
                chunks.append({
                    "chunk_id": f"CHUNK_{chunk_idx:03d}",
                    "source": source_reference,
                    "text": chunk_text_str,
                    "word_count": len(chunk_text_str.split()),
                    "char_count": len(chunk_text_str)
                })
                chunk_idx += 1

                # Keep overlap sentences
                overlap_sentences = []
                overlap_count = 0
                for s in reversed(current_chunk_sentences):
                    cnt = len(s.split())
                    if overlap_count + cnt <= self.chunk_overlap_words:
                        overlap_sentences.insert(0, s)
                        overlap_count += cnt
                    else:
                        break

                current_chunk_sentences = overlap_sentences + [sentence]
                current_word_count = overlap_count + sentence_words
            else:
                current_chunk_sentences.append(sentence)
                current_word_count += sentence_words

        if current_chunk_sentences:
            chunk_text_str = " ".join(current_chunk_sentences)
            chunks.append({
                "chunk_id": f"CHUNK_{chunk_idx:03d}",
                "source": source_reference,
                "text": chunk_text_str,
                "word_count": len(chunk_text_str.split()),
                "char_count": len(chunk_text_str)
            })

        return chunks
