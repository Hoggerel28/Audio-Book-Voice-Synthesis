"""文件读取模块：支持 TXT / PDF / EPUB 文本导入。"""
from __future__ import annotations

from pathlib import Path
from typing import Union


def read_txt(path: Union[str, Path]) -> str:
    """读取 TXT 文件，自动尝试常见编码。"""
    path = Path(path)
    encodings = ["utf-8", "utf-8-sig", "gbk", "gb18030"]
    last_error: Exception | None = None
    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
    raise UnicodeDecodeError("unknown", b"", 0, 1, f"无法识别文本编码：{last_error}")


def read_pdf(path: Union[str, Path]) -> str:
    """读取 PDF 文件中的文字。"""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("缺少 pypdf，请先运行：pip install pypdf") from exc

    reader = PdfReader(str(path))
    pages: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text)
        else:
            pages.append(f"\n[第{index}页未提取到可识别文字，可能是扫描图片 PDF]\n")
    return "\n".join(pages)


def read_epub(path: Union[str, Path]) -> str:
    """读取 EPUB 文件中的正文。"""
    try:
        from ebooklib import epub
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise RuntimeError("缺少 EPUB 依赖，请先运行：pip install ebooklib beautifulsoup4") from exc

    book = epub.read_epub(str(path))
    chapters: list[str] = []
    for item in book.get_items():
        media_type = getattr(item, "media_type", "")
        if media_type == "application/xhtml+xml":
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = soup.get_text("\n", strip=True)
            if text:
                chapters.append(text)
    return "\n\n".join(chapters)


def read_book_file(path: Union[str, Path]) -> str:
    """根据扩展名自动读取文件内容。"""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return read_txt(path)
    if suffix == ".pdf":
        return read_pdf(path)
    if suffix == ".epub":
        return read_epub(path)
    raise ValueError("暂只支持 TXT、PDF、EPUB 格式")
